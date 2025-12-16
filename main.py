from __future__ import annotations

import argparse
import os.path
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from doc_sync import (
    SCOPES,
    build_drive_service,
    export_file_content,
    fetch_document_title,
    get_required_env,
    run_flow_with_timeout,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the current content of a Google Doc to a text file",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Seconds to wait for OAuth browser authorization",
    )
    args = parser.parse_args()

    document_id = get_required_env("GOOGLE_DOCUMENT_ID")
    client_secret_file = get_required_env("GOOGLE_OAUTH_CLIENT_SECRETS")

    credentials = None
    token_file = "token.json"

    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=client_secret_file,
                scopes=SCOPES,
                autogenerate_code_verifier=True,
            )
            credentials = run_flow_with_timeout(flow, timeout=args.timeout)

        with open(token_file, "w") as token:
            token.write(credentials.to_json())

    service = build_drive_service(credentials)

    doc_title = fetch_document_title(service, document_id)
    response = (
        service.files()
        .export(
            fileId=document_id,
            mimeType="text/plain",
        )
        .execute()
    )

    if isinstance(response, bytes):
        content = response.decode("utf-8")
    else:
        content = str(response)

    export_path = export_file_content(content, doc_title)

    print(f"Exported current content of '{doc_title}' to {export_path}")


if __name__ == "__main__":
    main()
