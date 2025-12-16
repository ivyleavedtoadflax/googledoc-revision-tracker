from __future__ import annotations

import os
import os.path
import sys

import typer
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from drive_revisions import (
    GOOGLE_DRIVE_SCOPES,
    build_drive_service,
    build_drive_service_v2,
    download_revisions,
    fetch_document_title,
    get_required_env,
    load_document_ids_from_config,
    run_flow_with_timeout,
)

app = typer.Typer()


def get_credentials(timeout: int = 120) -> Credentials:
    """
    Get or refresh Google OAuth credentials.

    Handles the complete OAuth flow:
    1. Tries to load existing credentials from token.json
    2. Refreshes expired credentials if refresh token is available
    3. Runs full OAuth flow if needed
    4. Saves credentials to token.json for future use

    Args:
        timeout: Seconds to wait for OAuth browser authorization (default: 120).

    Returns:
        Valid OAuth2 credentials.

    Raises:
        SystemExit: If required environment variables are missing.
        TimeoutError: If OAuth authorization times out.
    """
    client_secret_file = get_required_env("GOOGLE_OAUTH_CLIENT_SECRETS")

    credentials = None
    token_file = "token.json"

    # Try to load existing credentials
    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, GOOGLE_DRIVE_SCOPES)

    # Refresh or re-authorize if needed
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Refresh expired credentials
            credentials.refresh(Request())
        else:
            # Run full OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=client_secret_file,
                scopes=GOOGLE_DRIVE_SCOPES,
                autogenerate_code_verifier=True,
            )
            credentials = run_flow_with_timeout(flow, timeout=timeout)

        # Save credentials for next time
        with open(token_file, "w") as token:
            token.write(credentials.to_json())

    return credentials


@app.command()
def download(
    document_ids: list[str] = typer.Argument(
        None,
        help="Google Doc IDs to download. If not provided, reads from config file or GOOGLE_DOCUMENT_ID env var",
    ),
    timeout: int = typer.Option(
        120, help="Seconds to wait for OAuth browser authorization"
    ),
) -> None:
    """
    Download all revision history for one or more Google Docs.

    Examples:
        python main.py                           # Use config file or env var
        python main.py DOC_ID_1                  # Single document
        python main.py DOC_ID_1 DOC_ID_2         # Multiple documents
    """
    # Resolve document IDs and names from multiple sources (priority order)
    # doc_map is a dict mapping document IDs to optional folder names
    doc_map: dict[str, str | None] = {}

    # 1. CLI arguments (highest priority) - no custom names for CLI args
    if document_ids:
        doc_map = {doc_id: None for doc_id in document_ids}

    # 2. Config file from GOOGLE_DOCUMENTS_FILE env var
    if not doc_map:
        config_file = os.environ.get("GOOGLE_DOCUMENTS_FILE")
        if config_file:
            doc_map = load_document_ids_from_config(config_file)

    # 3. Default config file: documents.yaml
    if not doc_map:
        doc_map = load_document_ids_from_config("documents.yaml")

    # 4. Single document from GOOGLE_DOCUMENT_ID env var (backward compatibility)
    if not doc_map:
        single_doc_id = os.environ.get("GOOGLE_DOCUMENT_ID")
        if single_doc_id:
            doc_map = {single_doc_id: None}

    # Error if no document IDs found
    if not doc_map:
        print(
            "Error: No document IDs provided.\n"
            "Please provide document IDs via:\n"
            "  1. CLI arguments: python main.py DOC_ID_1 DOC_ID_2\n"
            "  2. Config file: Create documents.yaml with document IDs\n"
            "  3. Environment variable: export GOOGLE_DOCUMENT_ID='your_doc_id'",
            file=sys.stderr,
        )
        raise typer.Exit(1)

    # Get credentials
    credentials = get_credentials(timeout)

    # Build Drive services
    service_v2 = build_drive_service_v2(credentials)
    service_v3 = build_drive_service(credentials)

    # Process each document
    total_downloaded = 0
    total_documents = len(doc_map)
    successful_downloads = 0

    print(f"Processing {total_documents} document(s)...\n")

    for idx, (doc_id, folder_name) in enumerate(doc_map.items(), 1):
        try:
            # Fetch document title for display
            doc_title = fetch_document_title(service_v3, doc_id)
            print(f"[{idx}/{total_documents}] Downloading '{doc_title}' ({doc_id})...")

            # Download revisions with custom folder name or document ID
            downloaded_files = download_revisions(
                service_v2,
                doc_id,
                "revisions",
                credentials,
                doc_title=doc_title,
                folder_name=folder_name,
            )

            file_count = len(downloaded_files)
            total_downloaded += file_count
            successful_downloads += 1

            # Show which folder was used
            target_folder = folder_name if folder_name else doc_id
            print(f"  ✓ Downloaded {file_count} revision(s) to revisions/{target_folder}/\n")

        except Exception as e:
            print(f"  ✗ Error downloading {doc_id}: {e}\n")
            continue

    # Print summary
    print("=" * 50)
    print(f"Summary: Successfully downloaded {successful_downloads}/{total_documents} document(s)")
    print(f"Total revisions downloaded: {total_downloaded}")
    print("=" * 50)


if __name__ == "__main__":
    app()
