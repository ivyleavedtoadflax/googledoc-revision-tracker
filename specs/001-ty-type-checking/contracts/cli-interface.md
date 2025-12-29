# CLI Interface Contract

**Feature**: Type Checking with ty
**Contract Type**: Command-Line Interface
**Version**: 1.0
**Date**: 2025-12-29

## Overview

This contract defines the command-line interface for running type checking operations. All developers and CI/CD systems must adhere to these interface specifications.

---

## Commands

### Primary Command: `uv run ty check`

**Purpose**: Run type checking on Python files in the current workspace

**Syntax**:
```bash
uv run ty check [OPTIONS] [FILES...]
```

**Arguments**:
- `FILES` (optional): Specific Python files to check. If omitted, checks entire workspace.

**Options**:
- `--config PATH`: Path to configuration file (default: auto-discover pyproject.toml)
- `--exclude PATTERN`: Additional exclusion patterns (can be specified multiple times)
- `--strict`: Enable strict type checking mode
- `--no-error-codes`: Hide error codes in output
- `--json`: Output results in JSON format
- `--quiet`: Suppress all output except errors
- `--verbose`: Show detailed progress information

**Exit Codes**:
- `0`: Type checking passed (no errors)
- `1`: Type checking failed (errors found)
- `2`: Invalid usage or configuration error

**Examples**:

```bash
# Check entire workspace
uv run ty check

# Check specific files
uv run ty check main.py drive_revisions.py

# Check with strict mode
uv run ty check --strict

# Get JSON output for CI parsing
uv run ty check --json

# Check with custom config
uv run ty check --config custom-ty.toml
```

---

## Output Format

### Standard Output (Human-Readable)

**Format**:
```
{file_path}:{line}:{column}: {severity}: {message} [{rule_code}]
```

**Example**:
```
main.py:45:12: error: Expected 'str' but got 'int' [type-mismatch]
drive_revisions.py:103:5: warning: Function may return None [missing-return]

Found 1 error and 1 warning in 2 files
Type checking failed
```

**Color Coding** (when terminal supports it):
- Errors: Red
- Warnings: Yellow
- Info: Blue
- File paths: Bold
- Rule codes: Dim

### JSON Output

**Format** (when `--json` flag is used):

```json
{
  "version": "1.0",
  "timestamp": "2025-12-29T19:30:45Z",
  "workspace": {
    "root": "/home/user/google-sync-simple",
    "files_checked": 2,
    "files_total": 2
  },
  "diagnostics": [
    {
      "file": "main.py",
      "line": 45,
      "column": 12,
      "severity": "error",
      "message": "Expected 'str' but got 'int'",
      "rule": "type-mismatch"
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 0,
    "info": 0,
    "duration_ms": 234
  },
  "success": false
}
```

**JSON Schema**:
- `version`: String, contract version
- `timestamp`: ISO 8601 datetime
- `workspace`: Object with root, files_checked, files_total
- `diagnostics`: Array of diagnostic objects
- `summary`: Aggregate counts and metrics
- `success`: Boolean, true if errors == 0

---

## Error Output

Errors are written to stderr in the same format as diagnostics:

```
Error: Configuration file not found: custom-ty.toml
Error: Invalid Python version specified: 3.9
Error: No Python files found in workspace
```

**Error Categories**:
1. **Configuration Errors**: Invalid or missing config files
2. **File Errors**: Files not found or not readable
3. **Runtime Errors**: Unexpected failures during type checking

---

## Integration Points

### CI/CD Usage

**Recommended Pattern**:
```yaml
- name: Run type checking
  run: uv run ty check
  continue-on-error: false
```

**Exit code handling**:
- Exit 0: Continue pipeline
- Exit 1: Fail pipeline (type errors found)
- Exit 2: Fail pipeline (configuration issue)

### Pre-commit Hook Usage

**Example**:
```bash
#!/bin/bash
# .git/hooks/pre-commit
uv run ty check $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
```

### IDE Integration

IDE integration uses `ty server` command (Language Server Protocol), not the CLI interface defined here. See `lsp-interface.md` for LSP contract.

---

## Performance Guarantees

Based on Success Criteria SC-001:

| Workspace Size | Maximum Duration |
|----------------|------------------|
| 1-10 files | < 1 second |
| 11-100 files | < 5 seconds |
| 101-1000 files | < 30 seconds |

**Current Project**: 2 files, expected < 1 second

---

## Compatibility

- **Python Version**: 3.12+
- **uv Version**: Latest (installed via project dependency)
- **Operating Systems**: Linux, macOS, Windows
- **Shell**: bash, zsh, PowerShell, cmd

---

## Contract Validation

### Test Cases

**TC-1: Successful Check**
```bash
$ uv run ty check
✓ Checked 2 files
Type checking passed
$ echo $?
0
```

**TC-2: Type Errors Found**
```bash
$ uv run ty check
main.py:45:12: error: Expected 'str' but got 'int' [type-mismatch]

Found 1 error in 2 files
Type checking failed
$ echo $?
1
```

**TC-3: Specific Files**
```bash
$ uv run ty check main.py
✓ Checked 1 file
Type checking passed
$ echo $?
0
```

**TC-4: JSON Output**
```bash
$ uv run ty check --json | jq '.success'
true
$ echo $?
0
```

**TC-5: Invalid Configuration**
```bash
$ uv run ty check --config missing.toml
Error: Configuration file not found: missing.toml
$ echo $?
2
```

---

## Backward Compatibility

This is version 1.0 (initial release). Future versions will maintain:
- Exit code semantics (0/1/2 meanings)
- Basic output format (file:line:column: severity: message)
- JSON output schema (with version field for evolution)

Breaking changes will increment the major version and provide migration guide.

---

## Notes

- ty command must be run via `uv run` to ensure correct virtual environment activation
- Direct `ty` invocation requires global installation (not recommended for project consistency)
- Configuration precedence: CLI flags > project config > user config > defaults
- All file paths in output are relative to workspace root for portability
