# Quickstart Guide: Type Checking with ty

**Feature**: Type Checking Integration
**Audience**: Developers working on google-sync-simple
**Time to Complete**: 5-10 minutes
**Date**: 2025-12-29

## Overview

This guide helps you set up and use ty type checking for the google-sync-simple project. You'll learn how to run type checks locally, integrate with your IDE, and understand the type checking workflow.

---

## Prerequisites

- ✅ Python 3.12+ installed
- ✅ uv package manager installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- ✅ Repository cloned locally
- ✅ Basic understanding of Python type hints

---

## Step 1: Install Development Dependencies

### Install ty and pytest

```bash
# Add development dependencies to the project
uv add --dev ty pytest hypothesis

# Verify installation
uv run ty --version
```

**Expected Output**:
```
ty 0.1.0
```

**Time**: ~30 seconds (depending on network speed)

---

## Step 2: Configure Type Checking

### Add Configuration to pyproject.toml

Open `pyproject.toml` and add this section at the end:

```toml
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

# Show error codes for easier documentation lookup
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
```

**Time**: 2 minutes

---

## Step 3: Run Your First Type Check

```bash
# Check all Python files in the project
uv run ty check

# Or check specific files
uv run ty check main.py
uv run ty check drive_revisions.py
```

**Expected Output (if no errors)**:
```
✓ Checked 2 files
Type checking passed
```

**Expected Output (if errors found)**:
```
main.py:45:12: error: Expected 'str' but got 'int' [type-mismatch]

Found 1 error in 2 files
Type checking failed
```

**Time**: < 1 second

---

## Step 4: Set Up IDE Integration (VS Code)

### Install VS Code Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "ty"
4. Install the official "ty" extension by Astral

### Configure VS Code Settings

Open `.vscode/settings.json` (create if it doesn't exist):

```json
{
  "python.languageServer": "None",
  "python.analysis.typeCheckingMode": "off",
  "editor.formatOnSave": true
}
```

**Why these settings?**
- `"python.languageServer": "None"` - Disables conflicting language servers
- ty's language server will provide type checking automatically

### Verify IDE Integration

1. Open `main.py` in VS Code
2. Introduce a type error (e.g., assign number to string variable)
3. You should see inline diagnostics immediately

**Time**: 3 minutes

---

## Step 5: Understanding Type Checking Results

### Reading Diagnostic Messages

Format: `file:line:column: severity: message [rule-code]`

Example:
```
main.py:45:12: error: Expected 'str' but got 'int' [type-mismatch]
```

**Breakdown**:
- `main.py` - File with the issue
- `45` - Line number
- `12` - Column number (character position)
- `error` - Severity level (error/warning/info)
- `Expected 'str' but got 'int'` - Description
- `[type-mismatch]` - Rule code for documentation lookup

### Severity Levels

| Level | Symbol | Meaning | Action Required |
|-------|--------|---------|-----------------|
| error | ❌ | Type error that must be fixed | Fix before committing |
| warning | ⚠️ | Potential issue | Should fix, can defer |
| info | ℹ️ | Informational message | Optional improvement |

---

## Step 6: Common Workflows

### Before Committing Code

```bash
# Run type check on your changes
git diff --name-only | grep '\.py$' | xargs uv run ty check

# Or check entire project
uv run ty check

# Fix any errors, then commit
git add main.py
git commit -m "Fix: Correct type annotations in main.py"
```

### Fixing Type Errors

**Example Error**:
```python
# main.py:45
def process_document(doc_id: str) -> dict:
    return doc_id + 1  # ❌ Error: str + int
```

**Fix**:
```python
def process_document(doc_id: str) -> dict:
    doc_number = int(doc_id) + 1  # ✓ Correct
    return {"id": doc_number}
```

**Verify**:
```bash
uv run ty check main.py
# ✓ Type checking passed
```

### Adding Type Annotations Incrementally

**Before** (untyped):
```python
def get_revision(revision_id):
    return fetch_from_api(revision_id)
```

**After** (typed):
```python
from typing import Dict, Any

def get_revision(revision_id: str) -> Dict[str, Any]:
    return fetch_from_api(revision_id)
```

**Check**:
```bash
uv run ty check drive_revisions.py
```

---

## Step 7: CI/CD Integration (GitHub Actions)

### Create Workflow File

Create `.github/workflows/type-check.yml`:

```yaml
name: Type Checking

on:
  push:
    branches: [main]
  pull_request:

jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup uv
        uses: astral-sh/setup-uv@v4

      - name: Run type checking
        run: uv run ty check
```

### Test Locally First

```bash
# Simulate CI environment
uv run ty check
echo "Exit code: $?"

# Exit code 0 = pass, 1 = errors, 2 = config error
```

### Push and Verify

```bash
git add .github/workflows/type-check.yml pyproject.toml
git commit -m "CI: Add type checking workflow"
git push
```

Visit GitHub Actions tab to see results.

**Time**: 5 minutes

---

## Troubleshooting

### Problem: "command not found: uv"

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell or source profile
source ~/.bashrc  # or ~/.zshrc
```

### Problem: "No Python files found"

**Solution**:
```bash
# Verify you're in project root
ls pyproject.toml

# Check exclude patterns aren't too broad
grep -A 5 "\[tool.ty\]" pyproject.toml
```

### Problem: IDE not showing diagnostics

**Solution**:
1. Restart VS Code
2. Check ty extension is installed and enabled
3. Verify `python.languageServer` is set to `"None"`
4. Check Output panel (View → Output → Select "ty" from dropdown)

### Problem: Too many false positives

**Solution**:
```toml
# Adjust strictness in pyproject.toml
[tool.ty]
strict = false  # Ensure gradual typing mode

# Disable specific rules temporarily
[tool.ty.rules]
problematic-rule = "ignore"
```

### Problem: Type check passes locally but fails in CI

**Solution**:
```bash
# Ensure lock file is committed
git add uv.lock
git commit -m "Lock dependencies"

# Use exact command from CI
uv run ty check

# Check Python version matches
python --version  # Should be 3.12+
```

---

## Best Practices

### When to Add Type Annotations

✅ **Always type**:
- Public function signatures
- Function parameters and return types
- Class attributes
- Global constants

⚠️ **Can skip initially**:
- Private/internal functions (prefix with `_`)
- Test files
- One-off scripts
- Legacy code (add gradually)

### Type Annotation Examples

```python
# Good: Clear type hints
from typing import List, Dict, Optional

def fetch_revisions(doc_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch document revisions."""
    ...

# Better: Use modern syntax (Python 3.12+)
def fetch_revisions(doc_id: str, limit: int = 10) -> list[dict[str, any]]:
    """Fetch document revisions."""
    ...

# Best: Specific types with type aliases
from typing import TypeAlias

Revision: TypeAlias = dict[str, str | int]

def fetch_revisions(doc_id: str, limit: int = 10) -> list[Revision]:
    """Fetch document revisions."""
    ...
```

### Gradual Adoption Strategy

**Week 1-2**: Set up infrastructure
- ✅ Install ty
- ✅ Configure pyproject.toml
- ✅ Run checks (informational only)

**Week 3-4**: Type new code
- ✅ Add types to all new functions
- ✅ CI warns but doesn't block

**Month 2**: Enforce in CI
- ✅ CI blocks PRs with type errors
- ✅ Gradually add types to existing code

**Month 3+**: Increase strictness
- ✅ Enable strict mode for typed modules
- ✅ Target 80%+ coverage

---

## Quick Reference

### Common Commands

```bash
# Check entire project
uv run ty check

# Check specific files
uv run ty check main.py drive_revisions.py

# Show verbose output
uv run ty check --verbose

# Get JSON output
uv run ty check --json

# Use strict mode (override config)
uv run ty check --strict

# Start language server (for IDE)
uv run ty server
```

### Exit Codes

- `0` - Type checking passed ✅
- `1` - Type errors found ❌
- `2` - Configuration error ❌

### Configuration Quick Reference

```toml
[tool.ty]
strict = false          # Gradual typing mode
exclude = [".venv"]     # Exclude patterns
python_version = "3.12" # Target version
show_error_codes = true # Show rule codes

[tool.ty.rules]
rule-name = "error" | "warning" | "ignore"
```

---

## Next Steps

Now that you have type checking set up:

1. ✅ Run `uv run ty check` before committing
2. ✅ Fix any errors found
3. ✅ Gradually add type annotations to existing code
4. ✅ Monitor CI for type checking results
5. ✅ Read research.md for detailed configuration options
6. ✅ Read contracts/ for API specifications

---

## Getting Help

### Documentation

- [ty Official Docs](https://docs.astral.sh/ty/)
- [Python Typing Docs](https://docs.python.org/3/library/typing.html)
- Project research.md for detailed analysis

### Common Type Errors

See [py Typing Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) for quick reference on type annotations.

### Report Issues

If you encounter bugs with ty:
- Check [ty GitHub Issues](https://github.com/astral-sh/ty/issues)
- Report project-specific issues to team

---

## Summary

You now have:

✅ ty installed and configured
✅ Type checking running locally
✅ IDE integration set up
✅ CI/CD workflow configured
✅ Understanding of type checking workflow

**Estimated setup time**: 10-15 minutes
**Ongoing time per commit**: < 1 minute to run checks

Start typing your code and catch bugs early! 🚀
