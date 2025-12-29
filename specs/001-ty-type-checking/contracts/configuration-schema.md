# Configuration Schema Contract

**Feature**: Type Checking with ty
**Contract Type**: Configuration File Schema
**Version**: 1.0
**Date**: 2025-12-29

## Overview

This contract defines the configuration schema for ty type checking. Configuration must be valid TOML and conform to this schema to ensure predictable type checking behavior.

---

## Configuration File Locations

### Precedence Order (Highest to Lowest)

1. **Command-line flags**: `--strict`, `--exclude`, etc.
2. **Project-level ty.toml**: `./ty.toml`
3. **Project-level pyproject.toml**: `./pyproject.toml` (under `[tool.ty]`)
4. **User-level config**: `~/.config/ty/ty.toml`
5. **Built-in defaults**

### File Format

**pyproject.toml** (Recommended for this project):
```toml
[tool.ty]
# Configuration under [tool.ty] table
```

**ty.toml** (Alternative):
```toml
# Configuration at root level (no [tool.ty] prefix)
```

---

## Schema Definition

### Root Configuration Options

```toml
[tool.ty]

# Boolean: Enable strict type checking mode
# Default: false (gradual typing)
strict = false

# Array[String]: Glob patterns for files/directories to exclude
# Default: []
exclude = [
    ".venv",
    "tests",
    "__pycache__",
    "*.pyi"  # Type stub files
]

# String: Target Python version for type checking
# Format: "MAJOR.MINOR" (e.g., "3.12", "3.11")
# Default: Current Python interpreter version
python_version = "3.12"

# Boolean: Include error codes in diagnostic messages
# Default: true
show_error_codes = true

# Integer: Maximum line length for context display
# Default: 100
# Range: 40-200
max_line_length = 100

# Boolean: Show progress during type checking
# Default: false (true for --verbose)
show_progress = false
```

### Rule Configuration

```toml
[tool.ty.rules]

# Each rule can be set to: "ignore", "warning", or "error"
# Default severity varies by rule (see ty documentation)

# Type mismatch errors
type-mismatch = "error"

# Missing return type annotations
missing-return-type = "warning"

# Index out of bounds
index-out-of-bounds = "warning"

# Accessing attributes that don't exist
unknown-attribute = "error"

# Calling with wrong argument types
wrong-argument-type = "error"

# Division by zero
division-by-zero = "warning"

# Unreachable code
unreachable-code = "warning"
```

---

## Complete Configuration Example

### For google-sync-simple Project

**File**: `pyproject.toml`

```toml
[project]
name = "google-sync-simple"
version = "0.1.0"
description = "A Python CLI tool to download and track Google Docs content and revision history"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "google-api-python-client>=2.149.0",
    "google-auth-oauthlib>=1.2.0",
    "pyyaml>=6.0.3",
    "typer>=0.20.0",
    "urllib3>=2.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.5",
    "hypothesis>=6.148.8",
    "ty>=0.1.0",
]

[project.scripts]
google-sync = "main:app"

[tool.setuptools]
py-modules = ["drive_revisions", "main"]

# ty Type Checker Configuration
[tool.ty]
# Start with gradual typing - don't require all code to be typed
strict = false

# Exclude virtual environment and cache directories
exclude = [
    ".venv",
    "__pycache__",
    "*.egg-info",
]

# Target Python 3.12 (project minimum)
python_version = "3.12"

# Show error codes for easier rule configuration
show_error_codes = true

# Configure rule severities
[tool.ty.rules]
# Critical: Must fix before merge
type-mismatch = "error"
unknown-attribute = "error"
wrong-argument-type = "error"

# Important: Should fix but can warn
missing-return-type = "warning"
unreachable-code = "warning"

# Informational: Can ignore initially
division-by-zero = "warning"
index-out-of-bounds = "warning"
```

---

## Validation Rules

### Structural Validation

1. **File Format**: Must be valid TOML syntax
2. **Section Name**: Must be `[tool.ty]` in pyproject.toml
3. **Type Safety**: All values must match declared types
4. **Required Fields**: None (all fields optional with defaults)

### Value Validation

| Field | Validation Rule | Error if Invalid |
|-------|----------------|------------------|
| `strict` | Must be boolean | "strict must be true or false" |
| `exclude` | Must be array of strings | "exclude must be an array of glob patterns" |
| `python_version` | Must match pattern `^\d+\.\d+$` | "python_version must be MAJOR.MINOR format" |
| `show_error_codes` | Must be boolean | "show_error_codes must be true or false" |
| `max_line_length` | Must be integer 40-200 | "max_line_length must be between 40 and 200" |
| `[tool.ty.rules].*` | Value must be "ignore", "warning", or "error" | "Rule severity must be ignore, warning, or error" |

### Semantic Validation

1. **Python Version**: Must be >= 3.12 (project requirement)
2. **Exclude Patterns**: Must be valid glob patterns
3. **Rule Names**: Must be recognized ty rules (unknown rules logged as warnings)

---

## Migration from Other Type Checkers

### From mypy

**mypy.ini** → **pyproject.toml [tool.ty]**

```ini
# mypy.ini (old)
[mypy]
python_version = 3.12
ignore_missing_imports = True
strict = False
exclude = venv/
```

```toml
# pyproject.toml (new)
[tool.ty]
python_version = "3.12"
strict = false
exclude = [".venv"]

[tool.ty.rules]
# ty handles missing imports differently
# See ty documentation for equivalent rules
```

### From Pyright

**pyrightconfig.json** → **pyproject.toml [tool.ty]**

```json
// pyrightconfig.json (old)
{
  "pythonVersion": "3.12",
  "typeCheckingMode": "basic",
  "exclude": [".venv", "__pycache__"]
}
```

```toml
# pyproject.toml (new)
[tool.ty]
python_version = "3.12"
strict = false  # "basic" mode equivalent
exclude = [".venv", "__pycache__"]
```

---

## Configuration Discovery Process

When `ty check` runs:

1. **Search for config**: Start in current directory, walk up to root
2. **Find first**: `ty.toml` OR `pyproject.toml` with `[tool.ty]`
3. **Load user config**: Merge with `~/.config/ty/ty.toml` (if exists)
4. **Apply CLI flags**: Override file-based settings
5. **Validate schema**: Report errors if invalid
6. **Use for type checking**: Apply configuration to workspace

**Example Discovery**:
```
/home/user/google-sync-simple/
├── pyproject.toml         # Found! Load [tool.ty]
├── main.py
└── drive_revisions.py
```

---

## Default Configuration

If no configuration file is found, ty uses these defaults:

```toml
[tool.ty]
strict = false
exclude = []
python_version = "3.12"  # Current interpreter version
show_error_codes = true
max_line_length = 100
show_progress = false

# All rules use their built-in default severities
```

---

## Configuration Testing

### Valid Configuration Tests

**Test 1**: Minimal valid config
```toml
[tool.ty]
# Empty is valid, uses all defaults
```
✓ Should pass validation

**Test 2**: Full configuration
```toml
[tool.ty]
strict = true
exclude = [".venv", "tests"]
python_version = "3.12"
show_error_codes = false

[tool.ty.rules]
type-mismatch = "error"
```
✓ Should pass validation

### Invalid Configuration Tests

**Test 3**: Wrong type for strict
```toml
[tool.ty]
strict = "yes"  # Should be boolean
```
✗ Should fail: "strict must be true or false"

**Test 4**: Invalid Python version
```toml
[tool.ty]
python_version = "3"  # Missing minor version
```
✗ Should fail: "python_version must be MAJOR.MINOR format"

**Test 5**: Invalid rule severity
```toml
[tool.ty.rules]
type-mismatch = "critical"  # Not a valid severity
```
✗ Should fail: "Rule severity must be ignore, warning, or error"

---

## Environment Variable Overrides

ty supports environment variables for some settings:

| Environment Variable | Overrides | Example |
|---------------------|-----------|---------|
| `TY_CONFIG` | Config file path | `TY_CONFIG=./custom.toml` |
| `TY_PYTHON_VERSION` | python_version | `TY_PYTHON_VERSION=3.11` |
| `TY_STRICT` | strict mode | `TY_STRICT=true` |

**Precedence**: CLI flags > env vars > config file > defaults

---

## Backward Compatibility

Configuration schema version 1.0 (this document).

Future versions will:
- Add new optional fields (backward compatible)
- Deprecate fields with migration period (12 months notice)
- Never remove fields without major version bump
- Always support pyproject.toml `[tool.ty]` format

---

## Related Contracts

- **CLI Interface**: How to invoke ty with configuration
- **LSP Interface**: Language server configuration (separate from type checking config)
- **CI/CD Integration**: Using configuration in automated pipelines

---

## Notes

- Configuration is shared between CLI (`ty check`) and LSP (`ty server`)
- Changes to pyproject.toml require restarting IDE for LSP to pick up
- Git should track pyproject.toml (project config) but not user-level config
- Exclude patterns use gitignore-style syntax (**, *, ?, etc.)
