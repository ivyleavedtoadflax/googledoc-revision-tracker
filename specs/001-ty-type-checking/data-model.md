# Data Model: Type Checking with ty

**Feature**: Type Checking Integration
**Date**: 2025-12-29
**Status**: Phase 1 - Design

## Overview

This document defines the data structures and entities involved in type checking integration. Since this is a development tooling feature, the "data model" primarily consists of configuration structures, diagnostic outputs, and workspace definitions rather than traditional application data.

---

## Entity: Type Diagnostic

### Description
Represents a type error, warning, or informational message produced by the ty type checker. These diagnostics are the primary output of type checking operations.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| file_path | string | Yes | Absolute or relative path to the file containing the issue |
| line_number | integer | Yes | Line number where the issue occurs (1-indexed) |
| column_number | integer | Yes | Column number where the issue starts (1-indexed) |
| severity | enum | Yes | One of: error, warning, info |
| rule_code | string | Yes | Identifier for the type checking rule violated (e.g., "type-mismatch") |
| message | string | Yes | Human-readable description of the issue |
| suggestion | string | No | Optional fix suggestion or guidance |
| context_lines | array[string] | No | Surrounding source code lines for context |

### Example

```json
{
  "file_path": "main.py",
  "line_number": 45,
  "column_number": 12,
  "severity": "error",
  "rule_code": "type-mismatch",
  "message": "Expected 'str' but got 'int'",
  "suggestion": "Convert to string using str()",
  "context_lines": [
    "    def process_document(doc_id: str):",
    "        return doc_id + 1  # Error here"
  ]
}
```

### Validation Rules

- `line_number` must be >= 1
- `column_number` must be >= 1
- `severity` must be one of the defined enum values
- `file_path` must point to an existing file in the workspace
- `message` must not be empty

### State Transitions

Diagnostics are immutable once generated. They don't have state transitions but can be:
1. Generated during type checking
2. Displayed to user (CLI/IDE)
3. Logged for CI/CD reporting
4. Archived after fixes

---

## Entity: Type Configuration

### Description
Settings that control ty type checker behavior, including strictness levels, exclusions, and rule configurations. Maps to the `[tool.ty]` section in pyproject.toml.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| strict | boolean | No | Enable strict type checking mode (default: false for gradual adoption) |
| exclude | array[string] | No | Glob patterns for files/directories to exclude |
| python_version | string | No | Target Python version for type checking (e.g., "3.12") |
| rules | object | No | Rule-specific configurations (see Rules Configuration below) |
| show_error_codes | boolean | No | Include rule codes in diagnostic messages (default: true) |
| max_line_length | integer | No | Maximum line length for context display (default: 100) |

### Rules Configuration

Nested object where keys are rule names and values are severity levels:

```toml
[tool.ty.rules]
index-out-of-bounds = "ignore"
type-mismatch = "error"
missing-return = "warning"
```

Possible severity values: `"ignore"`, `"warning"`, `"error"`

### Example

```toml
[tool.ty]
strict = false
exclude = [".venv", "tests", "__pycache__"]
python_version = "3.12"
show_error_codes = true

[tool.ty.rules]
type-mismatch = "error"
```

### Validation Rules

- `python_version` must be valid Python version string (e.g., "3.12", "3.11")
- `exclude` patterns must be valid glob patterns
- `max_line_length` must be > 0 if specified
- Rule severity values must be one of: "ignore", "warning", "error"

### Relationships

- Configuration applies to → Project Workspace
- Configuration determines → Diagnostic generation behavior

---

## Entity: Project Workspace

### Description
The set of Python files and directories subject to type checking. Represents the scope of type analysis.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| root_directory | string | Yes | Absolute path to project root (where pyproject.toml is located) |
| python_files | array[string] | Yes | List of Python files to check (after applying exclusions) |
| excluded_patterns | array[string] | No | Glob patterns for excluded files (from configuration) |
| total_file_count | integer | Yes | Total number of Python files discovered |
| checked_file_count | integer | Yes | Number of files actually checked (after exclusions) |

### Example

```json
{
  "root_directory": "/home/user/google-sync-simple",
  "python_files": [
    "main.py",
    "drive_revisions.py"
  ],
  "excluded_patterns": [".venv/*", "tests/*"],
  "total_file_count": 2,
  "checked_file_count": 2
}
```

### Validation Rules

- `root_directory` must exist and contain pyproject.toml or ty.toml
- `python_files` must contain only .py files
- `checked_file_count` <= `total_file_count`
- All paths in `python_files` must be relative to `root_directory`

### State Transitions

1. **Discovery**: Scan root_directory for .py files
2. **Filtering**: Apply exclusion patterns
3. **Type Checking**: Process each file
4. **Reporting**: Generate diagnostics

### Relationships

- Workspace contains → Python Files
- Workspace configured by → Type Configuration
- Type Checking on Workspace produces → Type Diagnostics

---

## Entity: Type Checking Result

### Description
Aggregated output of a type checking operation, combining diagnostics with summary statistics.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| workspace | Project Workspace | Yes | The workspace that was checked |
| diagnostics | array[Type Diagnostic] | Yes | All diagnostics generated (may be empty) |
| error_count | integer | Yes | Number of error-level diagnostics |
| warning_count | integer | Yes | Number of warning-level diagnostics |
| info_count | integer | Yes | Number of info-level diagnostics |
| success | boolean | Yes | True if error_count == 0 |
| duration_ms | integer | Yes | Time taken for type checking in milliseconds |
| timestamp | datetime | Yes | When the check was performed |

### Example

```json
{
  "workspace": {
    "root_directory": "/home/user/google-sync-simple",
    "checked_file_count": 2
  },
  "diagnostics": [
    {
      "file_path": "main.py",
      "line_number": 45,
      "severity": "error",
      "message": "Expected 'str' but got 'int'"
    }
  ],
  "error_count": 1,
  "warning_count": 0,
  "info_count": 0,
  "success": false,
  "duration_ms": 234,
  "timestamp": "2025-12-29T19:30:45Z"
}
```

### Validation Rules

- `error_count` = count of diagnostics where severity == "error"
- `warning_count` = count of diagnostics where severity == "warning"
- `info_count` = count of diagnostics where severity == "info"
- `success` = true if and only if `error_count` == 0
- `duration_ms` must be >= 0

---

## Data Flow

```
1. Load Configuration
   └─> Read pyproject.toml [tool.ty] section
       └─> Parse into Type Configuration entity

2. Discover Workspace
   └─> Scan for Python files
       └─> Apply exclusion patterns
           └─> Build Project Workspace entity

3. Execute Type Checking
   └─> For each file in workspace:
       └─> Analyze types
           └─> Generate Type Diagnostics

4. Generate Result
   └─> Aggregate diagnostics
       └─> Calculate statistics
           └─> Build Type Checking Result entity

5. Output/Report
   └─> CLI: Format and print to stdout/stderr
   └─> IDE: Send via Language Server Protocol
   └─> CI: Exit with code 0 (success) or 1 (errors)
```

---

## Configuration File Schema

### pyproject.toml Structure

```toml
[tool.ty]
# Boolean flag for strict mode
strict = false

# Array of glob patterns to exclude
exclude = [
    ".venv",
    "tests",
    "__pycache__",
]

# Python version target
python_version = "3.12"

# Display settings
show_error_codes = true

# Per-rule configuration
[tool.ty.rules]
type-mismatch = "error"
index-out-of-bounds = "warning"
```

### File Location Precedence

1. Command-line flags (highest priority)
2. `ty.toml` in project directory
3. `[tool.ty]` in pyproject.toml
4. `~/.config/ty/ty.toml` (user-level)
5. Built-in defaults (lowest priority)

---

## Integration Points

### Input Sources

1. **Configuration Files**: pyproject.toml, ty.toml
2. **Python Source Files**: main.py, drive_revisions.py, etc.
3. **Command-line Arguments**: Flags and options passed to `ty check`

### Output Destinations

1. **CLI (stdout/stderr)**: Human-readable diagnostic messages
2. **IDE (LSP)**: JSON-formatted diagnostics via language server protocol
3. **CI/CD (exit codes)**: 0 for success, non-zero for errors
4. **Log Files**: Optional structured logging for debugging

---

## Success Criteria Mapping

These entities support the success criteria defined in spec.md:

- **SC-001** (Complete in <5s): Measured by `Type Checking Result.duration_ms`
- **SC-002** (IDE feedback <1s): LSP incremental analysis (not directly modeled)
- **SC-003** (100% diagnostic completeness): `Type Diagnostic` attributes ensure file path, line number, and message always present
- **SC-004** (90% error detection): Validated by comparing diagnostics against known type error patterns
- **SC-005** (Zero false positives): Measured by diagnostic accuracy in testing
- **SC-006** (100% exclusion compliance): Validated by `Project Workspace.checked_file_count` vs `total_file_count`

---

## Notes

- This data model focuses on configuration and output structures since type checking is a development tool
- No database persistence required - all data is ephemeral (generated per check)
- Configuration persists in version-controlled files (pyproject.toml)
- IDE integration uses LSP JSON-RPC protocol for diagnostic transmission (separate from this model)
