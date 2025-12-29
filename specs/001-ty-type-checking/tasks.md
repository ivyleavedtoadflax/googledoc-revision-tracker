# Tasks: Type Checking with ty

**Input**: Design documents from `/specs/001-ty-type-checking/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the specification - focusing on implementation and manual validation per acceptance scenarios

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure (CLI tool)
- Configuration in `pyproject.toml` at repository root
- CI/CD workflows in `.github/workflows/`
- IDE settings in `.vscode/`
- No source restructuring needed (existing `main.py`, `drive_revisions.py`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 Verify uv package manager is installed and operational
- [X] T002 Verify Python 3.12+ is active in project environment
- [X] T003 Verify git repository is initialized for version control
- [X] T004 [P] Create .gitignore entries for Python artifacts if not present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core type checking infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Install ty as development dependency using `uv add --dev ty`
- [X] T006 Install pytest and hypothesis as development dependencies using `uv add --dev pytest hypothesis`
- [X] T007 Add base [tool.ty] configuration section to pyproject.toml with strict=false for gradual typing

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic Type Checking for Development (Priority: P1) 🎯 MVP

**Goal**: Enable developers to run type checking locally via single command and receive clear diagnostic messages

**Independent Test**: Run `uv run ty check` on existing Python files and verify:
- Command executes successfully
- Diagnostics show file path, line number, error description
- Exit code 0 for clean code, 1 for errors

**Acceptance Scenarios**:
1. Running ty on annotated code shows clear diagnostics for any errors
2. Running ty on error-free code shows confirmation message
3. Errors include specific line numbers and descriptions

### Implementation for User Story 1

- [X] T0*8 [US1] Configure [tool.ty] table in pyproject.toml with python_version="3.12", show_error_codes=true
- [X] T0*9 [US1] Add exclude patterns to [tool.ty] in pyproject.toml for .venv, __pycache__, *.egg-info
- [X] T0*10 [US1] Configure [tool.ty.rules] in pyproject.toml with type-mismatch="error", unknown-attribute="error", wrong-argument-type="error"
- [X] T0*11 [US1] Add warning-level rules to [tool.ty.rules] in pyproject.toml for missing-return-type, unreachable-code
- [X] T0*12 [US1] Test type checking by running `uv run ty check` and verifying output format matches CLI contract
- [X] T0*13 [US1] Test type checking with --json flag and verify JSON output schema matches contract
- [X] T0*14 [US1] Verify exit codes: 0 for success, 1 for errors, 2 for config errors
- [X] T0*15 [US1] Document basic usage in project README.md referencing quickstart.md

**Checkpoint**: Developers can now run `uv run ty check` locally and get actionable type error feedback

---

## Phase 4: User Story 2 - IDE Integration for Real-Time Feedback (Priority: P2)

**Goal**: Enable real-time type checking feedback in VS Code for immediate error detection while writing code

**Independent Test**: Open Python file in VS Code, introduce type error, verify:
- Inline diagnostic appears immediately (< 1 second)
- Hovering shows type information
- Code completion is type-aware

**Acceptance Scenarios**:
1. Type errors show inline diagnostics immediately
2. Hovering over variables shows inferred types
3. Code completion suggests type-aware options

### Implementation for User Story 2

- [ ] T016 [P] [US2] Create .vscode directory in project root
- [ ] T017 [US2] Create .vscode/settings.json with python.languageServer="None" to disable conflicts
- [ ] T018 [US2] Add .vscode/extensions.json recommending "astral-sh.ty" extension
- [ ] T019 [US2] Document VS Code setup in quickstart.md (already done, verify completeness)
- [ ] T020 [US2] Test IDE integration by opening main.py in VS Code and verifying LSP features work
- [ ] T021 [US2] Verify language server starts automatically (check VS Code Output panel for ty)
- [ ] T022 [US2] Test hover information shows type data for variables and functions
- [ ] T023 [US2] Test code completion provides type-aware suggestions

**Checkpoint**: Developers get sub-second type feedback in VS Code while editing Python files

---

## Phase 5: User Story 3 - Automated Type Checking in CI/CD (Priority: P3)

**Goal**: Automatically run type checking on every push/PR to catch errors before merge

**Independent Test**: Create PR with type errors, verify:
- CI workflow runs automatically
- Type errors cause workflow to fail
- PR shows clear failure status with error details

**Acceptance Scenarios**:
1. Type checking runs on every push to main and PR
2. PRs with type errors fail CI checks
3. PRs passing type checking show green status

### Implementation for User Story 3

- [X] T0*24 [P] [US3] Create .github directory in project root
- [X] T0*25 [P] [US3] Create .github/workflows directory
- [X] T0*26 [US3] Create .github/workflows/type-check.yml implementing GitHub Actions workflow per CICD contract
- [X] T0*27 [US3] Configure workflow to run on push to main branch and all pull requests
- [X] T0*28 [US3] Add checkout step using actions/checkout@v4
- [X] T0*29 [US3] Add uv setup step using astral-sh/setup-uv@v4 with enable-cache=true
- [X] T0*30 [US3] Add type checking step running `uv run ty check` with continue-on-error=false
- [ ] T031 [US3] Test workflow by pushing to branch and verifying it runs in GitHub Actions
- [ ] T032 [US3] Test workflow failure by introducing type error and verifying CI fails with exit code 1
- [ ] T033 [US3] Test workflow success by removing type error and verifying CI passes with exit code 0
- [ ] T034 [US3] Document CI/CD setup in README.md with badge showing workflow status

**Checkpoint**: Type checking runs automatically in CI/CD, blocking PRs with type errors from merging

---

## Phase 6: User Story 4 - Gradual Type Adoption (Priority: P4)

**Goal**: Support incremental type annotation adoption without requiring full codebase coverage

**Independent Test**: Create test file with mixed typed/untyped code, verify:
- Only annotated code is type-checked
- Excluded files are skipped
- New annotations are validated immediately

**Acceptance Scenarios**:
1. Partially typed files are checked without errors on untyped portions
2. File exclusions in config are respected
3. Adding type annotations to untyped function enables checking for that function

### Implementation for User Story 4

- [ ] T035 [US4] Verify strict=false is set in [tool.ty] section of pyproject.toml (done in T007, validate)
- [ ] T036 [US4] Test gradual typing by creating example file with mixed typed/untyped code
- [ ] T037 [US4] Verify untyped code doesn't cause errors or warnings
- [ ] T038 [US4] Add type annotations to one function in test file and verify it's now checked
- [ ] T039 [US4] Test file exclusion by adding temporary pattern to exclude list in pyproject.toml
- [ ] T040 [US4] Verify excluded files are skipped using `uv run ty check --verbose`
- [ ] T041 [US4] Remove temporary test exclusion pattern from pyproject.toml
- [ ] T042 [US4] Document gradual adoption strategy in README.md or CONTRIBUTING.md
- [ ] T043 [US4] Create example showing incremental annotation workflow in quickstart.md (already done, verify)

**Checkpoint**: Project supports gradual type adoption, allowing incremental improvements without breaking existing code

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and overall project quality

- [X] T0*44 [P] Update project README.md with complete type checking setup and usage instructions
- [X] T0*45 [P] Add type checking section to CONTRIBUTING.md (if file exists) with developer guidelines
- [X] T0*46 [P] Verify all ignore files (.gitignore, .dockerignore if applicable) include relevant patterns
- [X] T0*47 Add type checking badge to README.md showing CI status
- [X] T0*48 Run through complete quickstart.md guide to validate all instructions work
- [X] T0*49 Verify performance: Type checking completes in < 5s for current codebase (SC-001)
- [X] T0*50 Verify diagnostic completeness: All errors include file:line:column:message (SC-003)
- [X] T0*51 Test exclusion compliance: Verify excluded files never appear in ty output (SC-006)
- [X] T0*52 Create sample commit demonstrating TDD workflow with type checking
- [X] T0*53 Update CLAUDE.md agent context if any new patterns or decisions emerged

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP baseline for all other stories
- **User Story 2 (Phase 4)**: Depends on Foundational and US1 config - IDE needs working ty config
- **User Story 3 (Phase 5)**: Depends on Foundational and US1 config - CI uses same config as local
- **User Story 4 (Phase 6)**: Depends on Foundational and US1 config - Tests gradual typing settings
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - Independently testable
- **User Story 2 (P2)**: Uses US1 configuration - Independently testable (separate concern: IDE vs CLI)
- **User Story 3 (P3)**: Uses US1 configuration - Independently testable (separate concern: CI vs local)
- **User Story 4 (P4)**: Uses US1 configuration - Independently testable (validates config flexibility)

**Note**: All user stories depend on US1's configuration but test different aspects (CLI, IDE, CI, gradual adoption), making them independently verifiable.

### Within Each User Story

- Configuration before testing
- CLI validation before IDE/CI integration
- Core implementation before edge case testing
- Story complete before moving to next priority

### Parallel Opportunities

**Within Phase 1 (Setup)**:
- T004 can run independently

**Within Phase 3 (US1)**:
- T012-T014 can run in parallel (independent verification tasks)

**Within Phase 4 (US2)**:
- T016, T017, T018 can run in parallel (different files in .vscode/)

**Within Phase 5 (US3)**:
- T024, T025 (directory creation) can run in parallel
- T031-T033 (CI testing) can run sequentially

**Within Phase 7 (Polish)**:
- T044, T045, T046 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# After T007-T011 configuration tasks complete, launch validation tasks together:
Task: "T012 Test type checking by running uv run ty check"
Task: "T013 Test type checking with --json flag"
Task: "T014 Verify exit codes"
# These run independently and verify different aspects
```

---

## Parallel Example: User Story 2

```bash
# Create .vscode configuration files in parallel:
Task: "T016 Create .vscode directory"  # Must complete first
Task: "T017 Create .vscode/settings.json"  # Can run after T016
Task: "T018 Add .vscode/extensions.json"  # Can run in parallel with T017
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T007) - CRITICAL
3. Complete Phase 3: User Story 1 (T008-T015)
4. **STOP and VALIDATE**: Run `uv run ty check` and verify all acceptance scenarios
5. Commit and create baseline for other stories

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + ty installed → Ready for type checking
2. **MVP** (Phase 3 - US1): Local CLI type checking → Developers can check code manually ✅
3. **Enhanced DX** (Phase 4 - US2): IDE integration → Real-time feedback while coding ✅
4. **Automation** (Phase 5 - US3): CI/CD integration → Automated quality gates ✅
5. **Flexibility** (Phase 6 - US4): Gradual adoption → Supports incremental improvement ✅
6. **Polish** (Phase 7): Documentation and refinement → Production-ready

### Parallel Team Strategy

With multiple developers:

1. **Team** completes Setup + Foundational together (T001-T007)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T008-T015) - CLI configuration
   - **Developer B**: User Story 2 (T016-T023) - IDE setup (after US1 config exists)
   - **Developer C**: User Story 3 (T024-T034) - CI/CD (after US1 config exists)
   - **Developer D**: User Story 4 (T035-T043) - Gradual typing tests (after US1 config exists)
3. Stories integrate without conflicts (different files/concerns)

**Note**: US2, US3, US4 all reuse US1's configuration, so US1 should complete first, but the others can then proceed in parallel.

---

## Notes

- **No tests requested**: Specification doesn't request automated test suite, focusing on manual verification per acceptance scenarios
- **Configuration-heavy**: Most tasks involve setting up pyproject.toml, VS Code settings, GitHub Actions - very little code to write
- **Tool integration**: This feature integrates external tool (ty) rather than implementing new code
- **Validation approach**: Manual verification against acceptance scenarios rather than automated test suite
- **TDD compatible**: While no automated tests requested, the workflow supports TDD for application code (ty validates types)
- **File isolation**: Most tasks touch different files, enabling high parallelization potential
- **Incremental value**: Each user story delivers standalone value - can stop after any phase
- **Performance focused**: SC-001 requires <5s checking time - validate in T049
- **Documentation emphasis**: Multiple documentation tasks ensure developer adoption

---

## Success Criteria Validation

Tasks are mapped to success criteria from spec.md:

- **SC-001** (Type checking < 5s): Validated in T049
- **SC-002** (IDE feedback < 1s): Validated in T020-T023 (LSP performance)
- **SC-003** (100% diagnostic completeness): Validated in T012, T050
- **SC-004** (90% error detection): Inherent to ty's capabilities, no separate validation needed
- **SC-005** (Zero false positives): Validated through gradual typing tests in T036-T037
- **SC-006** (100% exclusion compliance): Validated in T040, T051

---

## Total Tasks: 53

**By Phase:**
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 3 tasks (CRITICAL - blocks all stories)
- Phase 3 (US1 - Basic Type Checking): 8 tasks 🎯 MVP
- Phase 4 (US2 - IDE Integration): 8 tasks
- Phase 5 (US3 - CI/CD Automation): 11 tasks
- Phase 6 (US4 - Gradual Adoption): 9 tasks
- Phase 7 (Polish): 10 tasks

**Parallel Opportunities**: 12 tasks marked [P] can run in parallel with others

**MVP Scope (Recommended)**: Phase 1 + Phase 2 + Phase 3 (15 tasks) delivers working type checking for local development
