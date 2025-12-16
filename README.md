# Google Docs Sync

A Python CLI tool to download and track Google Docs content and revision history.

## Features

- **Export Current Content**: Download the current state of a Google Doc as plain text
- **Revision History**: Download all historical revisions of a document with timestamps and author information
- **Diff Comparison**: Compare the two most recent exports and generate a unified diff

## Prerequisites

- Python 3.12+
- Google Cloud Project with Drive API enabled
- OAuth 2.0 Client ID credentials

## Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Library"
4. Enable the **Google Drive API**

### 2. Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "+ Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as the application type
4. Download the JSON file and save it (e.g., `client_secrets.json`)

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Path to your OAuth client secrets JSON file
GOOGLE_OAUTH_CLIENT_SECRETS=path/to/client_secrets.json

# Your Google Doc ID (from the document URL)
# https://docs.google.com/document/d/YOUR_DOC_ID_HERE/edit
GOOGLE_DOCUMENT_ID=your_document_id_here
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Or if using `uv`:

```bash
uv sync
```

## Usage

### Export Current Content

Download the current state of your Google Doc:

```bash
python main.py export
```

Output: `exports/YYYY-MM-DD-HHMMSS_Document_Title.txt`

### Download Revision History

Download all historical revisions of the document:

```bash
python main.py revisions
```

Output: `revisions/DOCUMENT_ID/REVISION_ID_author_timestamp.txt`

Each revision file includes:
- Revision ID
- Author email (username part only)
- Modification timestamp

### Compare Recent Exports

Generate a diff between the two most recent exports:

```bash
python main.py diff
```

Output: `diffs/YYYY-MM-DD-HHMMSS_diff.txt`

## Authentication

On first run, the tool will:
1. Open your browser for Google OAuth authorization
2. Ask you to grant access to Google Drive
3. Save credentials to `token.json` for future use

The OAuth flow has a 2-minute timeout. If you need more time, use:

```bash
python main.py export --timeout 300  # 5 minutes
python main.py revisions --timeout 300
```

## Project Structure

```
google-sync-simple/
├── main.py          # CLI commands and OAuth flow
├── doc_sync.py      # Core functionality (export, diff, revisions)
├── .env             # Environment variables (not committed)
├── .env.example     # Example environment configuration
├── token.json       # OAuth credentials (generated, not committed)
├── exports/         # Current content exports
├── revisions/       # Historical revisions
└── diffs/           # Diff outputs
```

## How It Works

### Export Process

1. Authenticate with Google OAuth 2.0
2. Use Drive API v3 to fetch document metadata and current content
3. Export as plain text
4. Save with timestamp and sanitized document title

### Revision History Process

1. Authenticate with Google OAuth 2.0
2. Use Drive API **v2** to access revision history (v3 doesn't support this)
3. For each revision:
   - Fetch metadata (ID, timestamp, author)
   - Download export link for plain text format
   - Save with descriptive filename

### Diff Process

1. Find the two most recent files in `exports/` directory
2. Generate unified diff with minimal context (0 lines)
3. Save to `diffs/` directory

## Troubleshooting

### "Missing required environment variable" Error

Ensure your `.env` file exists and contains both required variables:
- `GOOGLE_OAUTH_CLIENT_SECRETS`
- `GOOGLE_DOCUMENT_ID`

### "Authorization timed out" Error

Increase the timeout:

```bash
python main.py export --timeout 300
```

### "Insufficient permissions" or "Access denied"

1. Delete `token.json`
2. Re-run the command to re-authenticate with updated scopes
3. Ensure your Google account has access to the document

### No revisions found

The Drive API v2 only returns "grouped" revisions. Fine-grained revision history visible in the Google Docs UI may not all be accessible via the API.

## Development

### Running Tests

```bash
# TODO: Add test suite
```

### Code Structure

- `doc_sync.py`: Pure functions for Google Drive operations
- `main.py`: Typer CLI interface and OAuth flow management

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]
