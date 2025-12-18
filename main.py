from __future__ import annotations

import os
import os.path
import sys

import typer
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

from drive_revisions import (
    GOOGLE_DRIVE_SCOPES,
    DocumentConfig,
    build_drive_service,
    build_drive_service_v2,
    download_revisions,
    fetch_document_title,
    get_required_env,
    load_document_ids_from_config,
    run_flow_with_timeout,
)

app = typer.Typer(
    help="Download and track Google Docs revision history with granular time filtering."
)


def credentials_exist() -> bool:
    """Check if valid credentials exist."""
    token_file = "token.json"
    if not os.path.exists(token_file):
        return False

    try:
        credentials = Credentials.from_authorized_user_file(token_file, GOOGLE_DRIVE_SCOPES)
        # Check if credentials are valid or can be refreshed
        return credentials and (credentials.valid or (credentials.expired and credentials.refresh_token))
    except Exception:
        return False


def get_credentials(timeout: int = 120, force_reauth: bool = False) -> Credentials:
    """
    Get or refresh Google OAuth credentials.

    Handles the complete OAuth flow:
    1. Tries to load existing credentials from token.json
    2. Refreshes expired credentials if refresh token is available
    3. Runs full OAuth flow if needed
    4. Saves credentials to token.json for future use

    Args:
        timeout: Seconds to wait for OAuth browser authorization (default: 120).
        force_reauth: Force re-authentication even if valid credentials exist.

    Returns:
        Valid OAuth2 credentials.

    Raises:
        SystemExit: If required environment variables are missing.
        TimeoutError: If OAuth authorization times out.
    """
    client_secret_file = get_required_env("GOOGLE_OAUTH_CLIENT_SECRETS")

    credentials = None
    token_file = "token.json"

    # Try to load existing credentials (unless forcing reauth)
    if not force_reauth and os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, GOOGLE_DRIVE_SCOPES)

    # Refresh or re-authorize if needed
    if force_reauth or not credentials or not credentials.valid:
        if not force_reauth and credentials and credentials.expired and credentials.refresh_token:
            # Refresh expired credentials
            print("Refreshing expired credentials...")
            credentials.refresh(Request())
        else:
            # Run full OAuth flow
            print("\n🔐 Starting Google OAuth authentication...")
            print("A browser window will open for you to authorize access.")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=client_secret_file,
                scopes=GOOGLE_DRIVE_SCOPES,
                autogenerate_code_verifier=True,
            )
            credentials = run_flow_with_timeout(flow, timeout=timeout)
            print("✓ Authentication successful!\n")

        # Save credentials for next time with restrictive permissions
        with open(token_file, "w") as token:
            token.write(credentials.to_json())

        # Set file permissions to owner read/write only (0600)
        os.chmod(token_file, 0o600)

    return credentials


@app.command()
def auth(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force re-authentication even if already authenticated"
    ),
    timeout: int = typer.Option(
        120, help="Seconds to wait for OAuth browser authorization"
    ),
) -> None:
    """
    Authenticate with Google OAuth.

    This will open a browser window for you to authorize the application
    to access your Google Drive. Credentials are saved to token.json.

    Examples:
        uv run google-sync auth              # Authenticate (or check existing auth)
        uv run google-sync auth --force      # Force re-authentication
    """
    if not force and credentials_exist():
        print("✓ Already authenticated!")
        print("Use 'auth --force' to re-authenticate.")
        return

    try:
        get_credentials(timeout=timeout, force_reauth=force)
        print("✓ Successfully authenticated!")
        print("\nYou can now use 'google-sync download' to fetch document revisions.")
    except Exception as e:
        print(f"✗ Authentication failed: {e}", file=sys.stderr)
        raise typer.Exit(1)


@app.command()
def download(
    document_ids: list[str] = typer.Argument(
        None,
        help="Google Doc IDs to download. If not provided, reads from config file.",
    ),
    timeout: int = typer.Option(
        120, help="Seconds to wait for OAuth browser authorization"
    ),
) -> None:
    """
    Download revision history for one or more Google Docs.

    Requires authentication first (run 'google-sync auth' if needed).

    Examples:
        uv run google-sync download                    # Use config file (documents.yaml)
        uv run google-sync download DOC_ID_1           # Single document
        uv run google-sync download DOC_ID_1 DOC_ID_2  # Multiple documents
    """
    # Check for authentication
    if not credentials_exist():
        print("✗ Not authenticated!", file=sys.stderr)
        print("\nPlease run 'google-sync auth' first to authenticate with Google.", file=sys.stderr)
        raise typer.Exit(1)
    # Resolve document configurations from multiple sources (priority order)
    doc_configs: list[DocumentConfig] = []

    # 1. CLI arguments (highest priority) - no custom names/granularity for CLI args
    if document_ids:
        doc_configs = [DocumentConfig(doc_id=doc_id) for doc_id in document_ids]

    # 2. Default config file: documents.yaml
    if not doc_configs:
        doc_configs = load_document_ids_from_config("documents.yaml")


    # Error if no document IDs found
    if not doc_configs:
        print(
            "Error: No document IDs provided.\n"
            "Please provide document IDs via:\n"
            "  1. CLI arguments: python main.py DOC_ID_1 DOC_ID_2\n"
            "  2. Config file: Create documents.yaml with document IDs\n",
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
    total_documents = len(doc_configs)
    successful_downloads = 0

    print(f"Processing {total_documents} document(s)...\n")

    for idx, doc_config in enumerate(doc_configs, 1):
        try:
            # Fetch document title for display
            doc_title = fetch_document_title(service_v3, doc_config.doc_id)
            granularity_info = f" ({doc_config.granularity} granularity)" if doc_config.granularity != "all" else ""
            print(f"[{idx}/{total_documents}] Downloading '{doc_title}' ({doc_config.doc_id}){granularity_info}...")

            # Download revisions with config settings
            downloaded_files = download_revisions(
                service_v2,
                doc_config.doc_id,
                "revisions",
                credentials,
                doc_title=doc_title,
                folder_name=doc_config.folder_name,
                granularity=doc_config.granularity,
            )

            file_count = len(downloaded_files)
            total_downloaded += file_count
            successful_downloads += 1

            # Show which folder was used
            target_folder = doc_config.folder_name if doc_config.folder_name else doc_config.doc_id
            print(f"  ✓ Downloaded {file_count} revision(s) to revisions/{target_folder}/\n")

        except HttpError as e:
            # Handle common HTTP errors with friendly messages
            doc_id = doc_config.doc_id
            if e.resp.status == 404:
                print(f"  ✗ Document not found: {doc_id}", file=sys.stderr)
                print(f"    → Check that the document ID is correct", file=sys.stderr)
                print(f"    → Ensure you have access to this document\n", file=sys.stderr)
            elif e.resp.status == 403:
                print(f"  ✗ Permission denied: {doc_id}", file=sys.stderr)
                print(f"    → You don't have permission to access this document", file=sys.stderr)
                print(f"    → Ask the owner to share it with you\n", file=sys.stderr)
            elif e.resp.status == 401:
                print(f"  ✗ Authentication error: {doc_id}", file=sys.stderr)
                print(f"    → Try re-authenticating with: google-sync auth --force\n", file=sys.stderr)
            else:
                print(f"  ✗ HTTP {e.resp.status} error for {doc_id}: {e.error_details}\n", file=sys.stderr)
            continue
        except Exception as e:
            print(f"  ✗ Unexpected error downloading {doc_config.doc_id}: {e}\n", file=sys.stderr)
            continue

    # Print summary
    print("=" * 50)
    print(f"Summary: Successfully downloaded {successful_downloads}/{total_documents} document(s)")
    print(f"Total revisions downloaded: {total_downloaded}")
    print("=" * 50)


if __name__ == "__main__":
    app()
