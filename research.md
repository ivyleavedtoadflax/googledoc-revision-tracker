# Phase 0 Research: Google Doc Change Export CLI

**Date**: 2025-12-15  
**Feature**: 001-doc-change-export

## Overview

This document resolves technical uncertainties identified in the planning phase and establishes best practices for implementation.

---

## Decision 1: HTTP Retry Library

**Decision**: Use **urllib3's built-in Retry**

**Rationale**: 
- Already integrated into google-api-python-client's HTTP transport layer (zero additional dependencies)
- Provides native exponential backoff with jitter, HTTP 429 handling via `status_forcelist`, and Retry-After header respect
- Full type hint support (urllib3 2.x+) and proven stability with Google APIs
- Maps directly to spec requirement: "exponential backoff (3 attempts max, delays of 1s, 2s, 4s)"

**Configuration**:
```python
from urllib3.util import Retry

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 503],
    backoff_factor=1,  # Delays: 1s, 2s, 4s
    respect_retry_after_header=True
)
```

**Alternatives Considered**:

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| urllib3.Retry (chosen) | Built-in, HTTP-native, no deps | None for this use case | ✅ Best fit |
| tenacity | Highly configurable, general-purpose | +1 dependency, more complex | ❌ Overkill |
| backoff | Simple decorator syntax | Maintenance mode (2022), less HTTP-specific | ❌ Less maintained |
| google-api-python-client native | No extra dependency | No built-in retry mechanism | ❌ Not available |

---

## Decision 2: OAuth2 Browser Flow Implementation

**Decision**: Use **google-auth-oauthlib.InstalledAppFlow** with threading wrapper for timeout

**Key Patterns**:

1. **PKCE enabled**: Always use `autogenerate_code_verifier=True` for security
2. **Random port binding**: Use `port=0` to avoid conflicts
3. **State parameter**: Automatically generated and validated by library
4. **Timeout workaround**: `run_local_server()` has no built-in timeout; implement threading wrapper

**Implementation Pattern**:
```python
import threading
from google_auth_oauthlib.flow import InstalledAppFlow

def run_flow_with_timeout(flow, timeout=120):
    result = {'credentials': None, 'error': None}
    
    def target():
        try:
            result['credentials'] = flow.run_local_server(
                port=0,  # Random available port
                open_browser=True,
                authorization_prompt_message='Please authorize...',
                success_message='Authorization complete. Close this window.'
            )
        except Exception as e:
            result['error'] = e
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        raise TimeoutError(f"Authorization timed out after {timeout} seconds")
    
    if result['error']:
        raise result['error']
    
    return result['credentials']
```

**Security Considerations**:
- Credentials stored in memory only (no token caching)
- Localhost binding prevents external access
- PKCE protects against authorization code interception
- Client secrets for installed apps are intentionally non-confidential (per OAuth2 spec)

**Common Pitfalls Avoided**:
- Hardcoded ports (use random port selection)
- Missing timeout (implement threading wrapper)
- Insecure credential storage (memory-only approach)
- Not checking granted scopes (verify `credentials.scopes` after authorization)

---

## Decision 3: Google Docs Revision History API Usage

**CRITICAL FINDING**: Google Drive API **does NOT provide diff/change information OR text export for historical revisions**

**What the API Provides**:
- List of revisions with metadata (id, modifiedTime, lastModifyingUser)
- Export of the **HEAD** (current) revision only

**What the API Does NOT Provide**:
- Diff information between revisions
- Explicit insertion/deletion markers
- **Export of historical revisions** (attempting `files.export` with `revisionId` fails; `revisions.get_media` returns 404 for native Docs)

**Spec Impact**:
Original spec and previous research assumed we could export revision N to text/plain. **This is incorrect.** We cannot access the content of past revisions via the API.

**Decision**: Pivot to **Metadata Listing Only**

**Rationale**:
- Technical impossibility of fetching historical text content for native Google Docs via the API.
- CLI will now focus on providing a clear log of *who* changed the doc and *when*.

**Implementation Strategy**:
- `list_revisions_since` fetches metadata.
- CLI displays this metadata.
- No diffing or text extraction is performed.

---

## Decision 4: File Naming and Organization
...
(rest of file remains similar, but file export is no longer relevant for revisions)

...

## Summary of Resolved Unknowns

| Unknown | Resolution |
|---------|------------|
| HTTP retry library | urllib3.Retry (built-in) |
| OAuth timeout implementation | Threading wrapper (no native support) |
| Revision diff/insertion markers | **NOT AVAILABLE** |
| Historical Revision Text Export | **NOT AVAILABLE** (API limitation) |
| API rate limit handling | urllib3.Retry with `status_forcelist=[429, 503]` |
| Date-based revision filtering | Client-side filtering (API doesn't support) |

---

## Spec Updates Required

Based on final implementation findings:

1. **FR-004**: ~~"CLI MUST parse revision diffs..."~~ -> **DROPPED**
   - **New**: "CLI MUST list revision metadata (ID, time, author) for all revisions since the specified date."

2. **FR-003**: ...
   - **Updated**: "CLI MUST fetch all revisions... then filter client-side..."

3. **Key Entities**: `TextInsertion` and `DocumentSnapshot` are **DROPPED**. `Revision` metadata is the primary entity.

4. **Success Criteria**:
   - **Updated**: "CLI successfully lists revision metadata for documents with up to 500 revisions."

---

## Next Phase

**Phase 1**: Design data model and contracts based on these decisions.

Key data models needed:
- `Revision` (from API response)
- `DocumentSnapshot` (exported text at revision point)
- `TextInsertion` (diff result)
- `ExportFile` (output metadata)
