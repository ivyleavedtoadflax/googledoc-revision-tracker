# Research: Type Checking with ty

**Feature**: Type Checking Integration
**Date**: 2025-12-29
**Status**: Phase 0 Complete

## Overview

This document consolidates research findings for integrating ty (Astral's Python type checker) into the google-sync-simple project. Research covered installation methods, configuration, IDE integration, CI/CD automation, and testing framework selection.

---

## Decision 1: Testing Framework

### Decision
**pytest + hypothesis** (with optional pytest-mypy for type validation)

### Rationale

1. **TDD Alignment**: pytest's simple syntax (`assert` statements) and excellent error messages support rapid test-first development as required by CLAUDE.md guidelines

2. **Community Standard**: pytest is ranked #1 by the Python community with 800+ plugins and is the de facto standard for Python projects in 2025

3. **CLI Testing**: Seamless integration with typer (already a project dependency) via `typer.testing.CliRunner`

4. **Type Safety**: pytest-mypy plugin enables type checking during test runs, ensuring type annotations are validated

5. **Property-Based Testing**: hypothesis integration supports comprehensive edge case testing and aligns with behavior-driven testing principles

6. **uv Compatibility**: Works flawlessly with uv package manager, leveraging its 10-100x faster installation speed

### Alternatives Considered

- **unittest**: Built-in but more verbose, class-based syntax less suitable for TDD workflows
- **nose2**: Less actively maintained, smaller ecosystem than pytest

### Implementation

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.5",
    "hypothesis>=6.148.8",
]
```

Install and run:
```bash
uv add --dev pytest hypothesis
uv run pytest
```

---

## Decision 2: ty Installation Method

### Decision
**uv package manager** (development dependency)

### Rationale

1. **Project Consistency**: Project already uses uv for package management (evidenced by uv.lock)

2. **Reproducibility**: Adding ty as dev dependency ensures all team members use the same version

3. **Performance**: uv provides 10-100x faster package installation than pip

4. **Versioning**: Lock file ensures reproducible builds across environments

### Alternatives Considered

- **uvx (ephemeral)**: Fast for one-off checks but doesn't pin versions
- **Global installation**: Less reproducible across team/CI environments
- **pipx**: Not aligned with project's uv-first approach

### Implementation

```bash
# Add as development dependency
uv add --dev ty

# Run type checking
uv run ty check

# Or check specific files
uv run ty check main.py drive_revisions.py
```

---

## Decision 3: ty Configuration Approach

### Decision
**pyproject.toml with `[tool.ty]` table** for project-level configuration

### Rationale

1. **Centralization**: Keeps all project configuration in single file alongside dependencies

2. **Standard Practice**: pyproject.toml is Python ecosystem standard for tool configuration

3. **Version Control**: Configuration is tracked in git, ensuring consistency across environments

4. **Precedence**: Project-level config (pyproject.toml) takes precedence over user-level config

### Configuration Options

ty supports configuration through:
- `[tool.ty]` table in pyproject.toml
- `ty.toml` file (takes precedence over pyproject.toml if both exist)
- User-level config at `~/.config/ty/ty.toml`
- Command-line flags (highest precedence)

### Example Configuration

```toml
[tool.ty]
# Enable gradual typing - don't error on untyped code
strict = false

# File exclusions
exclude = [
    ".venv",
    "tests",
    "__pycache__",
]

[tool.ty.rules]
# Configure specific type checking rules
# (specific rules TBD based on codebase needs)
```

---

## Decision 4: IDE Integration Strategy

### Decision
**VS Code extension** with language server configuration

### Rationale

1. **Official Support**: Astral provides official VS Code extension for ty

2. **Zero Configuration**: Extension works out of the box after installation

3. **Language Server Features**: Provides code navigation, completions, auto-import, inlay hints, and hover help

4. **Performance**: Fine-grained incremental analysis ensures fast updates while editing

### Alternatives Considered

- **Neovim**: Good LSP support but requires more manual configuration
- **PyCharm**: Native support only from version 2025.3+
- **Manual LSP**: `ty server` command available but VS Code extension is simpler

### Implementation

1. Install VS Code extension: "ty" from marketplace
2. Disable conflicting language server in settings.json:
   ```json
   {
     "python.languageServer": "None"
   }
   ```
3. ty language server activates automatically for Python files

---

## Decision 5: CI/CD Integration Pattern

### Decision
**GitHub Actions workflow** with uv run ty check

### Rationale

1. **Simplicity**: Single command runs type checking without complex setup

2. **Fast Execution**: ty is 10-60x faster than mypy/Pyright, reducing CI time

3. **Zero Cache Needed**: Speed eliminates need for caching strategies

4. **Compact Output**: Easy to parse programmatically for CI reporting

### Implementation Pattern

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

### Alternatives Considered

- **Pre-commit hooks**: Useful but doesn't replace CI validation
- **Caching**: Unnecessary given ty's speed
- **Multiple Python versions**: Not needed for type checking (checks code, not runtime)

---

## Decision 6: Gradual Typing Adoption Strategy

### Decision
**Incremental adoption** starting with new code and critical paths

### Rationale

1. **Pragmatic**: Avoid rewriting entire codebase upfront

2. **Supported by ty**: ty explicitly designed for "redeclarations and partially typed code"

3. **Immediate Value**: Get type checking benefits on new code immediately

4. **Low Risk**: Doesn't require touching working code unnecessarily

### Adoption Plan

**Phase 1** (P1 - Basic Type Checking):
- Configure ty to not error on untyped code (`strict = false`)
- Add type hints to new functions/classes as they're written
- Run ty check in CI (informational, doesn't block PRs initially)

**Phase 2** (P2 - IDE Integration):
- Install VS Code extension for real-time feedback
- Developers get type hints as they work

**Phase 3** (P3 - CI Enforcement):
- After sufficient coverage, make type checking a blocking CI check
- Configure strictness levels per module if needed

**Phase 4** (P4 - Full Coverage):
- Systematically add types to existing code
- Increase strictness settings progressively

### File Exclusion Strategy

Configure exclusions for:
- Third-party code (`.venv/`)
- Test files initially (`tests/` - add types later)
- Generated files
- Migration/one-off scripts

---

## Technical Constraints Resolved

### Original Unknowns from Technical Context

1. ✅ **Testing Framework**: pytest + hypothesis (decided above)
2. ✅ **ty Installation**: uv add --dev ty
3. ✅ **Configuration Format**: pyproject.toml with [tool.ty] table
4. ✅ **IDE Setup**: VS Code extension + language server
5. ✅ **CI/CD Pattern**: GitHub Actions with uv run ty check
6. ✅ **Gradual Typing**: Supported natively, use strict = false initially

### Performance Characteristics

- **Speed**: 10-100x faster than mypy and Pyright (according to benchmarks)
- **Incremental Analysis**: Fast updates when editing files in IDE
- **Current Codebase**: 2 Python files will check in <1 second (well under 5s requirement)
- **IDE Responsiveness**: Sub-second feedback (meets <1s requirement from spec)

### Integration Points

1. **pyproject.toml**: Configuration and dev dependencies
2. **GitHub Actions**: CI/CD automation
3. **VS Code**: IDE integration via extension
4. **uv**: Package management and execution
5. **pytest**: Test framework (separate but complementary)

---

## Sources

- [ty Documentation](https://docs.astral.sh/ty/)
- [ty Configuration Reference](https://docs.astral.sh/ty/configuration/)
- [ty Installation Guide](https://docs.astral.sh/ty/installation/)
- [ty Editor Integration](https://docs.astral.sh/ty/editors/)
- [ty GitHub Repository](https://github.com/astral-sh/ty)
- [A Github Actions setup for Python projects in 2025](https://ber2.github.io/posts/2025_github_actions_python/)
- [Meet "ty": Astral's Powerful New Python Type Checker](https://codeunleashed.blooggy.com/news/2025/05/20/astral-releases-ty-a-new-python-type-checker-formerly-red-knot.html)
- [Astral's ty: A New Blazing-Fast Type Checker for Python – Real Python](https://realpython.com/python-ty/)
- [3 Python Unit Testing Frameworks to Know About in 2025](https://zencoder.ai/blog/python-unit-testing-frameworks)
- [10 Best Python Testing Frameworks in 2025 - GeeksforGeeks](https://www.geeksforgeeks.org/python/best-python-testing-frameworks/)
- [Pytest vs Unittest: A Comparison | BrowserStack](https://www.browserstack.com/guide/pytest-vs-unittest)
- [Managing Python Projects With uv: An All-in-One Solution – Real Python](https://realpython.com/python-uv/)
- [Python UV: The Ultimate Guide to the Fastest Python Package Manager | DataCamp](https://www.datacamp.com/tutorial/python-uv)

---

## Next Steps

Phase 1 (Design & Contracts) will use these research findings to:
1. Define data model for type diagnostics and configuration
2. Create configuration templates
3. Generate quickstart guide for developers
4. Update agent context with ty tooling decisions
