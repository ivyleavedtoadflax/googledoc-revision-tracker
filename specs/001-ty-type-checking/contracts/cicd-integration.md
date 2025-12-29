# CI/CD Integration Contract

**Feature**: Type Checking with ty
**Contract Type**: Continuous Integration/Deployment
**Version**: 1.0
**Date**: 2025-12-29

## Overview

This contract defines how ty type checking integrates with CI/CD pipelines, specifically GitHub Actions. It ensures consistent type checking across all environments and blocks merges when type errors are present.

---

## GitHub Actions Workflow Contract

### Workflow File Location

**Path**: `.github/workflows/type-check.yml`

**Requirements**:
- Must be committed to version control
- Must run on push to main branch
- Must run on all pull requests
- Must use latest stable uv action

### Minimal Workflow Specification

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
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup uv
        uses: astral-sh/setup-uv@v4

      - name: Run type checking
        run: uv run ty check
```

**Contract Guarantees**:
1. Workflow fails if type errors found (exit code 1)
2. Workflow passes if no type errors (exit code 0)
3. Workflow fails if configuration invalid (exit code 2)
4. All Python files are checked (except excluded patterns)
5. Results are visible in workflow logs

---

## Full Workflow Specification

### Complete GitHub Actions Implementation

```yaml
name: Type Checking

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

permissions:
  contents: read
  pull-requests: write  # For posting comments (optional enhancement)

jobs:
  type-check:
    name: Run ty Type Checker
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better context

      - name: Setup uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
          enable-cache: true

      - name: Verify Python version
        run: python --version

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run type checking
        id: typecheck
        run: |
          echo "Running ty type checker..."
          uv run ty check --show-error-codes
        continue-on-error: false

      - name: Collect statistics
        if: always()
        run: |
          echo "Type checking completed"
          echo "Exit code: $?"

      # Optional: Post results as PR comment
      - name: Comment on PR
        if: failure() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: '❌ Type checking failed. Please fix type errors before merging.'
            })
```

---

## Exit Code Contract

### Required Behavior

| Exit Code | Meaning | Workflow Action | PR Status |
|-----------|---------|----------------|-----------|
| 0 | No type errors | ✅ Pass | Can merge |
| 1 | Type errors found | ❌ Fail | Cannot merge |
| 2 | Configuration error | ❌ Fail | Cannot merge |

**Implementation**:
```bash
uv run ty check
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Type checking passed"
    exit 0
elif [ $EXIT_CODE -eq 1 ]; then
    echo "❌ Type checking failed - errors found"
    exit 1
else
    echo "❌ Type checking failed - configuration error"
    exit 2
fi
```

---

## Performance Requirements

Based on Success Criteria SC-001:

| Project Size | Maximum CI Duration | SLA |
|--------------|---------------------|-----|
| Current (2 files) | < 5 seconds | 99% |
| Small (< 50 files) | < 30 seconds | 99% |
| Medium (< 500 files) | < 2 minutes | 95% |

**Measurement**: From "Run type checking" step start to completion

**Current Project**: 2 Python files, expected < 5 seconds total (including uv setup)

---

## Output Format Requirements

### Standard Output (Logs)

**Format for CI logs**:
```
Starting type checking...
Checking 2 Python files...

main.py:45:12: error: Expected 'str' but got 'int' [type-mismatch]
drive_revisions.py:103:5: warning: Function may return None [missing-return]

Summary:
  Files checked: 2
  Errors: 1
  Warnings: 1
  Duration: 0.23s

Type checking failed ❌
```

**Requirements**:
1. Clear separation of errors and warnings
2. File path relative to repository root
3. Line and column numbers for IDE linking
4. Error codes in brackets for documentation lookup
5. Summary section with counts and timing

### JSON Output (Optional)

For programmatic parsing:

```bash
uv run ty check --json > type-check-results.json
```

```json
{
  "version": "1.0",
  "timestamp": "2025-12-29T19:30:45Z",
  "workspace": {
    "root": "/github/workspace",
    "files_checked": 2
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
    "warnings": 1,
    "duration_ms": 234
  },
  "success": false
}
```

---

## Branch Protection Rules

### Required Status Checks

**GitHub Settings**: Repository → Settings → Branches → Branch Protection Rules

For `main` branch:

```yaml
Require status checks to pass before merging: ✓
  Required checks:
    - Run ty Type Checker ✓

Require branches to be up to date before merging: ✓
```

**Contract**: Pull requests CANNOT merge if type checking fails

---

## Workflow Triggers

### Required Triggers

```yaml
on:
  push:
    branches: [main]  # Required: Validate main branch
  pull_request:      # Required: Validate PRs before merge
```

### Optional Triggers

```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Optional: Weekly health check
  workflow_dispatch:     # Optional: Manual trigger
```

---

## Integration with Other Workflows

### Test Workflow Coordination

**Pattern**: Type checking should run in parallel with tests

```yaml
# Example: Multiple jobs running in parallel
jobs:
  type-check:
    # ... ty check steps

  test:
    # ... pytest steps

  lint:
    # ... ruff check steps
```

**Requirement**: All jobs must pass for PR to merge

### Dependency Caching

**Contract**: Use uv's built-in caching for faster CI

```yaml
- name: Setup uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true  # Required for performance
```

**Performance Gain**: 30-60% faster dependency installation on cache hit

---

## Error Handling

### Configuration Errors

**Scenario**: Invalid pyproject.toml

**Expected Behavior**:
```
Error: Invalid configuration in pyproject.toml
  Line 5: python_version must be MAJOR.MINOR format
  Found: "3"
  Expected: "3.12"

Type checking failed ❌
Exit code: 2
```

**Workflow Result**: ❌ Failed

### File Not Found Errors

**Scenario**: Python file deleted but still in config

**Expected Behavior**:
```
Warning: File not found: old_module.py
Skipping: old_module.py

Checked 2 files (1 skipped)
Type checking passed ✓
Exit code: 0
```

**Workflow Result**: ✅ Passed (with warning log)

---

## Notification Contract

### PR Comments (Optional Enhancement)

**When**: Type checking fails on PR

**Format**:
```markdown
## ❌ Type Checking Failed

Type errors were found in your changes. Please fix before merging.

### Errors Found (1)

- `main.py:45:12` - Expected 'str' but got 'int' [type-mismatch]

### Warnings Found (1)

- `drive_revisions.py:103:5` - Function may return None [missing-return]

[View full type checking logs](https://github.com/user/repo/actions/runs/12345)
```

**Requirement**: Comment must link to full logs

### Slack/Email Integration (Future)

Not required for initial implementation but contract allows for:
- Slack notifications on main branch failures
- Email alerts for repeated type checking failures
- Metrics dashboard integration

---

## Rollback Strategy

### When Type Checking Breaks

**Scenario**: ty update introduces false positives

**Resolution Steps**:

1. **Immediate**: Temporarily allow failures
   ```yaml
   - name: Run type checking
     run: uv run ty check
     continue-on-error: true  # Temporary only
   ```

2. **Short-term**: Pin ty version
   ```toml
   [project.optional-dependencies]
   dev = [
       "ty==0.5.0",  # Pin to last known good version
   ]
   ```

3. **Long-term**: Fix type annotations or report ty bug

**Contract**: `continue-on-error: true` must NEVER be permanent

---

## Testing the Workflow

### Workflow Test Cases

**TC-1: Clean codebase**
```bash
# Trigger: Push to PR
# Expected: ✅ Workflow passes
```

**TC-2: Type error introduced**
```bash
# Modify main.py to introduce type error
# Trigger: Push to PR
# Expected: ❌ Workflow fails, PR cannot merge
```

**TC-3: Configuration error**
```bash
# Break pyproject.toml syntax
# Trigger: Push to PR
# Expected: ❌ Workflow fails with config error message
```

**TC-4: Local vs CI consistency**
```bash
# Run locally: uv run ty check
# Push to PR: workflow runs uv run ty check
# Expected: Same results (exit code, diagnostics)
```

---

## Success Criteria Mapping

This contract ensures:

- **SC-001** (< 5s for 2 files): Verified in CI logs
- **SC-003** (100% diagnostic completeness): All diagnostics include file:line:column:message
- **SC-008** (Automatable in CI/CD): Fully automated GitHub Actions workflow
- **FR-008** (Type checking MUST be automatable): Contract defines automation pattern

---

## Version Compatibility

| Component | Version | Requirement |
|-----------|---------|-------------|
| GitHub Actions | Any | Built-in platform |
| setup-uv action | v4+ | Latest recommended |
| ty | 0.1.0+ | As in dev dependencies |
| Python | 3.12+ | Project requirement |
| uv | Latest | Managed by setup-uv action |

---

## Related Contracts

- **CLI Interface**: Defines `uv run ty check` command used in workflow
- **Configuration Schema**: Defines pyproject.toml format for CI
- **Exit Codes**: Defines 0/1/2 behavior used in workflow logic

---

## Migration Path

### Phase 1: Informational (Week 1)
```yaml
- name: Run type checking
  run: uv run ty check
  continue-on-error: true  # Don't block merges yet
```

### Phase 2: Blocking (Week 2)
```yaml
- name: Run type checking
  run: uv run ty check
  # Blocks PRs with type errors
```

### Phase 3: Enforcement (Week 3+)
```yaml
# Enable branch protection
# Required status check: "Run ty Type Checker"
```

---

## Notes

- Workflow runs in clean environment each time (no state between runs)
- uv ensures consistent dependency versions via lock file
- Type checking is deterministic (same input → same output)
- No credentials or secrets required for type checking
- Workflow compatible with fork PRs (read-only operations)
