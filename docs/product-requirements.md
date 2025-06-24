# Product Requirements Document: **pytest-LLM-Validate**

## 1. Overview

**Project Name:** **pytest-LLM-Validate**
**Import Namespace / PyPI package:** `numerous.pytest_llm_validate`

`pytest-LLM-Validate` is a pytest plugin and toolkit that lets developers embed **AI-driven qualitative & behavioural tests** into their codebase with minimal boilerplate.

* **Built-in rule prompts** are packaged as Markdown-Cursor (`.mdc`) files for reuse in CursorAI. **Users do not create or edit these files.**
* **End-users author ordinary pytest tests** and express qualitative expectations in plain English, while executing actual code. Two APIs are provided:

  1. **Decorator API** – annotate a test with `@llm_eval`, return the artefact to evaluate.
  2. **Object/Fixture API** – obtain a tester object via `llm_eval("spec", **opts)`, then call `tester.check(output, label="...")` for flexible multiple checks.
* Both APIs capture:

  * the natural-language specification,
  * observed artefacts (return value, captured `stdout`/`stderr`), and
  * optional metadata (`threshold`, `model`).
    The helper constructs an `EvalRequest`, invokes a **PydanticAI** agent (tested with OpenAI `o4-mini`), and receives an `EvalResult` containing **score, comment, pass/fail**. Failures raise pytest assertions with explanatory comments.
* Exposed via a **core library** and thin wrappers:
  **core → CLI → FastAPI REST → MCP one-shot CLI → MCP server**.

---

## 2. Objectives

* Provide reusable internal `.mdc` prompts as CursorAI-compatible rule templates.
* Empower users to validate **live code outputs** against **natural-language criteria** using a simple decorator or fixture.
* Use **PydanticAI** for all LLM interactions; CI tests against `o4-mini`.
* Maintain a unified codebase underpinning CLI, REST, and MCP interfaces.

---

## 3. Scope

### In-Scope

1. **Packaged Rule Prompts**: internal `.mdc` files.
2. **Decorator & Fixture APIs**: `@llm_eval` and `llm_eval().check()`.
3. **Core Library**: rule loader, agent orchestration, stdout/stderr capture, deduplication, reporting.
4. **CLI** (`pytest-llm-mcp`): `run`, `generate`, `reference`, `serve`.
5. **FastAPI REST**: identical endpoints on `localhost`.
6. **MCP CLI (one-shot)**: single evaluation run for CursorAI.
7. **MCP Server**: persistent REST service for external agents.
8. **History**: JSON-based deduplication store.
9. **Reporting**: console tables & JUnit XML output.
10. **Toolchain**: MkDocs, ruff, mypy (strict), pytest-cov, semantic-release, GitHub Actions, MIT license, 80% coverage.

### Out-of-Scope

* User-authored `.mdc` files.
* Cloud/SaaS hosting of REST services.

---

## 4. Requirements

### Functional Requirements

1. Auto-load all packaged `.mdc` prompts at runtime.
2. Accept and parse user-provided NL criteria and artifacts via decorator/fixture.
3. Construct and dispatch `EvalRequest` to agent; enforce `EvalResult.passed`.
4. Expose consistent behavior via CLI, REST, MCP.
5. Skip repeated evaluations by hashing (criteria + code + artifacts).
6. Surface LLM feedback in console and JUnit XML.

### Non-Functional Requirements

* **Python**: ≥ 3.12, < 3.14 (CI matrix 3.12 & 3.13).
* **Lint & Format**: ruff with `ruff format`.
* **Typing**: mypy strict mode.
* **Coverage**: 80% enforced (reduced from 100% for pragmatic CI).
* **CI**: GitHub Actions for lint, type, test, docs.
* **LLM Testing**: OpenAI `o4-mini`.
* **Release**: semantic-release to PyPI.

---

## 5. Architecture

```text
pytest test
  ├─ Decorator/Fixture captures spec + artifacts
  ├─ Core builds EvalRequest
  ├─ EvalAgent (LLM) processes request
  ├─ EvalResult returned
  └─ Reporter asserts and logs feedback
```

Wrappers: core → CLI → REST → MCP CLI → MCP server

---

## 6. Toolchain Summary

| Category      | Tooling                             |
| ------------- | ----------------------------------- |
| Language      | Python 3.12 / 3.13                  |
| Testing       | pytest, pytest-cov (80% gate)       |
| Lint & Format | ruff (`ruff format`)                |
| Typing        | mypy (`--strict`)                   |
| Documentation | MkDocs (Material theme)             |
| CI            | GitHub Actions matrix (3.12 & 3.13) |
| Release       | semantic-release & PyPI             |

---

## 7. Development Plan — Ticket-Level Tasks & Commit Guidance

Adhere to **feature-branch**, **TDD-first**, **squash-on-merge**. After each Phase, cut a release that **includes updated docs and tests**.

### Phase 1 — Repository & Toolchain Foundation ✅ **COMPLETED (Release v0.1.0-rc1)**

| Task | Title                                   | Status | Description                                                                                                   |
| ---- | --------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| 1.1  | chore(repo): scaffold base repo         | ✅     | Initialize repo: add `pyproject.toml`, `README.md`, `LICENSE`, empty `numerous/pytest_llm_validate/` package. |
| 1.2  | docs(contributing): add CONTRIBUTING.md | ✅     | Create `CONTRIBUTING.md` with branching workflow, commit conventions, PR guidelines, and `docs/resume.md`.    |
| 1.3  | ci(setup): GitHub Actions & pre-commit  | ✅     | Configure CI: matrix for Python 3.12 & 3.13 lint, type, test, docs build. Add `.pre-commit-config.yaml`.      |
| 1.4  | test(skeleton): red tests for loader    | ✅     | Add placeholder tests expecting `NotImplementedError` for loader & decorator. Verify CI fails.                |

### Phase 2 — Core Library & Evaluation APIs ✅ **COMPLETED (Release v0.1.0)**

| Task | Title                                     | Status | Description                                                                                                      |
| ---- | ----------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------- |
| 2.1  | feat(loader): load packaged .mdc prompts  | ✅     | Implement loader to read `.mdc` files into `EvalRule` models; tests validate count and fields.                   |
| 2.2  | feat(decorator): implement `@llm_eval`    | ✅     | Provide decorator capturing docstring, executing test body to obtain return value/stdout, and building request.  |
| 2.3  | feat(fixture): object API with `.check()` | ✅     | Expose `Tester` via fixture; support multiple `check()` calls and artifact labels; tests for combined artifacts. |
| 2.4  | feat(history): deduplication JSON store   | ✅     | Implement JSON history store to skip duplicate evals; add `--no-dedupe` option; tests for skip logic.            |

### Phase 3 — CLI Interface 🚧 **IN PROGRESS (Target: Release v0.2.0)**

| Task | Title                                       | Status | Description                                                                                                                          |
| ---- | ------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| 3.1  | feat(cli): implement run/generate/reference | 🚧     | Build `pytest-llm-mpc` CLI using Click; `run` invokes pytest, `generate` writes in-memory tests to disk, `reference` outputs rubric. |
| 3.2  | feat(cli): add serve command                | ⏳     | Implement `serve` to start FastAPI on `--port`, support graceful shutdown; add integration test for `/health`.                       |

### Phase 4 — FastAPI REST Backend ⏳ **PLANNED (Target: Release v0.3.0)**

| Task | Title                                                 | Status | Description                                                                                                       |
| ---- | ----------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| 4.1  | feat(api): implement `/run-tests` & `/generate-tests` | ⏳     | Create FastAPI app with POST `/run-tests` and `/generate-tests` endpoints; use Pydantic schemas; tests via HTTPX. |
| 4.2  | feat(api): add `/reference` & `/health`               | ⏳     | Add GET `/reference` and `/health`; include OpenAPI docs; tests for both.                                         |

### Phase 5 — MCP Integration ⏳ **PLANNED (Target: Release v0.4.0)**

| Task | Title                                    | Status | Description                                                                                        |
| ---- | ---------------------------------------- | ------ | -------------------------------------------------------------------------------------------------- |
| 5.1  | feat(mcp-cli): one-shot mode             | ⏳     | Add `pytest-llm-mpc mcp-run` to start REST, perform single eval, output JSON to stdout, then exit. |
| 5.2  | feat(mcp-server): persistent server mode | ⏳     | Support `pytest-llm-mpc serve --persistent`; keep server alive; docs include example systemd unit. |

### Phase 6 — Reporting & QA ⏳ **PLANNED (Target: Release v0.5.0)**

| Task | Title                                        | Status | Description                                                                                                                                        |
| ---- | -------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 6.1  | feat(report): console table & JUnit XML      | ⏳     | Develop custom pytest reporter plugin that displays evaluation results in a formatted table and injects `<system-out>` in JUnit XML with comments. |
| 6.2  | test(integration): OpenAI o4-mini evaluation | ⏳     | Write integration tests against OpenAI `o4-mini` via PydanticAI agent; record snapshots and mock latencies.                                        |

### Phase 7 — Final Docs & Release ⏳ **PLANNED (Target: Release v1.0.0)**

| Task | Title                                   | Status | Description                                                                                           |
| ---- | --------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------- |
| 7.1  | docs(site): finalize MkDocs site        | 🚧     | Complete MkDocs pages: Quick-start, decorator vs fixture, CLI commands, REST API usage, MCP examples. |
| 7.2  | qa(coverage): enforce coverage gate     | ✅     | Configure CI to fail on coverage <80%; annotate intentional gaps with `# pragma: no cover`.          |
| 7.3  | release(v1.0.0): semantic-release setup | ✅     | Configure `semantic-release`, set up GitHub Actions for automatic versioning & PyPI publishing.      |

## 8. Current Implementation Status

### ✅ **Completed Components**
- **Core Architecture**: All foundational models, agents, and APIs implemented
- **Rule System**: Packaged `.mdc` prompt loading and management
- **Decorator API**: `@llm_eval` with full stdout/stderr capture
- **Fixture API**: Multi-check `llm_eval` fixture with summary reporting
- **History System**: JSON-based deduplication with hash-based skipping
- **CI/CD Pipeline**: GitHub Actions with comprehensive quality gates
- **Documentation**: MkDocs with Material theme, developer workflow guides
- **Quality Tools**: Pre-commit hooks, ruff formatting, mypy strict typing

### 🚧 **In Progress**
- **CLI Interface**: Entry point configured, commands partially implemented
- **Documentation**: Advanced usage examples and API references

### ⏳ **Planned**
- **REST API**: FastAPI backend with OpenAPI documentation
- **MCP Integration**: Model Context Protocol support for AI assistants
- **Advanced Reporting**: Console tables and enhanced JUnit XML output

## 9. Integration with Development Workflow

This PRD aligns with the established development documentation:

- **[Developer Workflow](developer-workflow.md)**: TDD cycle, quality gates, and feature development
- **[CI Debugging](ci-debugging.md)**: Local simulation and remote monitoring tools
- **[Technical Resume](resume.md)**: Detailed architecture and implementation status
- **[Contributing Guidelines](https://github.com/numerous-com/pytest-llm-validate/blob/main/CONTRIBUTING.md)**: Branching strategy and code standards

## 10. Legend

- ✅ **Completed**: Fully implemented and tested
- 🚧 **In Progress**: Currently being developed
- ⏳ **Planned**: Scheduled for future development

> **Branching Convention:** `feat/<ticket#>-short-desc`, `fix/<...>`, `docs/<...>`, `test/<...>`
> **Commit Message Format:** `type(scope): concise summary`

---

*PRD Version: 1.1 - Updated to reflect current implementation state (Phase 1-2 completed, Phase 3 in progress)*
