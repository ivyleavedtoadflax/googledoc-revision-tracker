# Implementation Plan: Type Checking with ty

**Branch**: `001-ty-type-checking` | **Date**: 2025-12-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ty-type-checking/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate ty (Astral's high-performance Python type checker) into the google-sync-simple project to enable:
1. Local type checking via simple command
2. IDE integration for real-time type feedback
3. CI/CD automation for enforcing type correctness
4. Gradual type adoption in the existing codebase

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: uv (package manager), ty (type checker), typer, google-api-python-client
**Storage**: Files (Python source files: main.py, drive_revisions.py)
**Testing**: NEEDS CLARIFICATION - testing framework not specified in pyproject.toml
**Target Platform**: Linux (developer workstations and CI/CD environments)
**Project Type**: Single CLI application
**Performance Goals**: Type checking completes in <5s for current codebase, IDE feedback <1s
**Constraints**: Must work with uv package manager, Python 3.12+, gradual typing support required
**Scale/Scope**: Small codebase (2 Python files currently), will grow incrementally

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file is currently a template without specific project principles. Applying general best practices:

### Initial Analysis (Pre-Research)

| Principle | Status | Notes |
|-----------|--------|-------|
| Test-Driven Development | ⚠️ NEEDS ATTENTION | Testing framework not specified; must define before implementation |
| Simplicity | ✅ PASS | Adding type checking is a standard development tool, not complexity |
| Dependencies | ✅ PASS | ty is part of uv ecosystem (already in use), minimal new dependency |
| Backwards Compatibility | ✅ PASS | Type checking is additive; doesn't break existing code |
| Platform Support | ✅ PASS | Works on Linux (current platform), cross-platform compatible |

### Re-evaluation (Post-Phase 1 Design)

| Principle | Status | Notes |
|-----------|--------|-------|
| Test-Driven Development | ✅ PASS | Testing framework selected: pytest + hypothesis (see research.md) |
| Simplicity | ✅ PASS | Type checking is a standard development tool, reduces complexity |
| Dependencies | ✅ PASS | ty + pytest added as dev dependencies, both part of Python ecosystem |
| Backwards Compatibility | ✅ PASS | Type checking is additive; existing code continues to work |
| Platform Support | ✅ PASS | All tools support Linux/macOS/Windows, well-tested |
| Data Model | ✅ PASS | No persistent storage required, all data ephemeral |
| Configuration | ✅ PASS | Standard pyproject.toml, version controlled |

### Final Gate Decision: **✅ FULL PASS**

**Resolution of Conditions**:
- ✅ Testing framework resolved: pytest + hypothesis selected in Phase 0 research
- ✅ Configuration approach defined: pyproject.toml with [tool.ty] table
- ✅ CI/CD integration pattern established: GitHub Actions workflow
- ✅ IDE integration strategy defined: VS Code extension + LSP

**No violations or complexity to justify**:
- Type checking is a standard, recommended practice
- All dependencies are minimal and well-maintained
- No architectural changes required to existing code
- Fully compatible with TDD workflow (CLAUDE.md requirement)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Current Structure (Single CLI Project)
.
├── main.py                      # CLI entry point
├── drive_revisions.py           # Core functionality
├── pyproject.toml               # Project configuration (to be updated with ty)
├── .github/                     # CI/CD workflows (to be created)
│   └── workflows/
│       └── type-check.yml       # Type checking automation
├── .vscode/                     # IDE settings (to be created)
│   └── settings.json            # ty language server configuration
└── tests/                       # Test directory (to be created if needed)
    ├── test_main.py
    └── test_drive_revisions.py
```

**Structure Decision**: This is a simple single-project CLI tool. The flat structure with two Python modules is appropriate for the current scope. Type checking integration requires:
1. Configuration in pyproject.toml
2. CI/CD workflow files in .github/workflows/
3. Optional IDE settings for LSP integration
4. No source restructuring needed

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations to track. Type checking is a standard development tool that reduces complexity by catching errors early.

---

## Planning Status

### Phase 0: Outline & Research ✅ COMPLETE

**Completed**: 2025-12-29

**Deliverables**:
- ✅ research.md - Comprehensive research on ty configuration, testing frameworks, IDE integration, and CI/CD patterns
- ✅ All technical unknowns resolved
- ✅ Testing framework selected: pytest + hypothesis
- ✅ Installation method decided: uv add --dev ty
- ✅ Configuration approach defined: pyproject.toml with [tool.ty] table
- ✅ Gradual typing adoption strategy established

**Key Decisions**:
1. **Testing Framework**: pytest + hypothesis for TDD workflow
2. **Installation**: uv package manager (project dependency)
3. **Configuration**: pyproject.toml for centralization
4. **IDE Integration**: VS Code extension with LSP
5. **CI/CD**: GitHub Actions with simple uv run ty check
6. **Adoption**: Gradual typing with strict = false initially

### Phase 1: Design & Contracts ✅ COMPLETE

**Completed**: 2025-12-29

**Deliverables**:
- ✅ data-model.md - Defined Type Diagnostic, Type Configuration, Project Workspace, and Type Checking Result entities
- ✅ contracts/cli-interface.md - CLI command specifications, exit codes, and output formats
- ✅ contracts/configuration-schema.md - Complete pyproject.toml schema with validation rules
- ✅ contracts/cicd-integration.md - GitHub Actions workflow contract and requirements
- ✅ quickstart.md - Developer guide for setup and usage
- ✅ Agent context updated (CLAUDE.md) with ty tooling decisions

**Architecture Decisions**:
1. **Data Model**: Ephemeral diagnostic structures (no persistence)
2. **CLI Interface**: Standard uv run ty check with --json option
3. **Configuration**: TOML schema with rule-level customization
4. **CI/CD**: Simple GitHub Actions workflow without caching (ty is fast enough)
5. **Exit Codes**: 0 (pass), 1 (errors), 2 (config error)

### Phase 2: Tasks Generation - PENDING

**Next Command**: `/speckit.tasks`

**Expected Deliverables**:
- tasks.md - Dependency-ordered implementation tasks
- Test cases for each user story
- Incremental implementation steps

### Constitution Re-evaluation ✅ PASS

All gates passed after Phase 1 design:
- ✅ Testing framework resolved
- ✅ No architectural violations
- ✅ Compatible with TDD principles
- ✅ Standard dependency management
- ✅ Simple, focused solution

---

## Planning Summary

**Branch**: `001-ty-type-checking`
**Specification**: [spec.md](spec.md)
**Implementation Plan**: This document
**Status**: Ready for task generation

**Artifacts Generated**:
1. [research.md](research.md) - Research findings and technical decisions
2. [data-model.md](data-model.md) - Entity definitions and data flows
3. [contracts/cli-interface.md](contracts/cli-interface.md) - CLI contract
4. [contracts/configuration-schema.md](contracts/configuration-schema.md) - Config schema
5. [contracts/cicd-integration.md](contracts/cicd-integration.md) - CI/CD contract
6. [quickstart.md](quickstart.md) - Developer quickstart guide

**Ready for Next Phase**: Yes - All planning artifacts complete, all gates passed

**Next Steps**:
1. Run `/speckit.tasks` to generate implementation tasks
2. Review and approve tasks
3. Begin implementation following TDD workflow
