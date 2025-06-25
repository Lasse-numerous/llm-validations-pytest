# Project Resume: pytest-LLM-Validate

## Project Overview

**pytest-LLM-Validate** is a pytest plugin that enables AI-driven qualitative testing by integrating Large Language Models into the testing workflow. The project aims to bridge the gap between traditional automated testing and qualitative evaluation criteria.

> **📋 For complete product specification and development roadmap, see [Product Requirements Document](product-requirements.md)**

## Technical Architecture

### Core Components

1. **Rule System**: Packaged `.mdc` (Markdown-Cursor) files containing LLM prompts
2. **Evaluation APIs**: Decorator (`@llm_eval`) and fixture-based (`llm_eval()`) interfaces
3. **Agent Integration**: PydanticAI-powered evaluation with OpenAI o4-mini
4. **Multi-Interface Support**: Core library → CLI → REST API → MCP integration

### Technology Stack

- **Language**: Python 3.12+ (CI tested on 3.12 & 3.13)
- **AI Framework**: PydanticAI with OpenAI integration
- **Testing**: pytest ecosystem with 80% coverage requirement
- **Code Quality**: ruff (format + lint) + mypy (strict mode)
- **Web Framework**: FastAPI for REST API
- **CLI Framework**: Click for command-line interface
- **Documentation**: MkDocs with Material theme
- **CI/CD**: GitHub Actions + semantic-release

## Development Status

**Current Version**: v0.1.0-rc1
**Current Phase**: Phase 3 - CLI Interface Development (Target: v0.2.0)

### ✅ Phase 1 - Repository & Toolchain Foundation (COMPLETED)
- [x] Repository scaffolding with pyproject.toml
- [x] Package structure setup (`numerous.pytest_llm_validate`)
- [x] Initial README and documentation
- [x] Contributing guidelines and workflow
- [x] CI/CD with GitHub Actions (Python 3.12 & 3.13 matrix)
- [x] Pre-commit hooks with ruff, mypy, bandit
- [x] MkDocs documentation system with Material theme

### ✅ Phase 2 - Core Library & Evaluation APIs (COMPLETED)
- [x] **Rule Loader** (`loader.py`): Packaged `.mdc` prompt management
- [x] **Decorator API** (`decorator.py`): `@llm_eval` with stdout/stderr capture
- [x] **Fixture API** (`fixture.py`): Multi-check `llm_eval` fixture
- [x] **History System** (`history.py`): JSON-based deduplication with hash-based skipping
- [x] **Data Models** (`models.py`): Pydantic models for requests/responses
- [x] **Agent Integration** (`agent.py`): PydanticAI-powered LLM evaluation
- [x] **Plugin System** (`plugin.py`): pytest plugin registration and configuration

### 🚧 Phase 3 - CLI Interface (IN PROGRESS)
- [x] CLI entry point configuration (`pytest-llm-mcp` command)
- [x] Click framework integration
- [ ] Core CLI commands implementation (`run`, `generate`, `reference`)
- [ ] FastAPI serve command with health endpoint

### ⏳ Upcoming Phases
- **Phase 4**: FastAPI REST backend with OpenAPI documentation
- **Phase 5**: MCP (Model Context Protocol) integration for AI assistants
- **Phase 6**: Advanced reporting (console tables, enhanced JUnit XML)
- **Phase 7**: Documentation finalization and v1.0.0 release

## Key Design Decisions

### 1. PydanticAI Integration
- **Rationale**: Leverages Pydantic's type safety and validation
- **Benefits**: Structured LLM responses, built-in retry logic, comprehensive monitoring
- **Implementation**: Using slim install with OpenAI-specific dependencies

### 2. Dual API Design
- **Decorator API**: Simple, annotation-based for single evaluations
- **Fixture API**: Flexible, object-based for complex multi-check scenarios
- **Rationale**: Covers both simple and advanced use cases with minimal learning curve

### 3. Multi-Interface Architecture
- **Core Library**: Shared business logic and evaluation engine
- **Progressive Wrappers**: CLI → REST → MCP for different integration needs
- **Benefits**: Code reuse, consistent behavior, flexible deployment options

### 4. Built-in Rule System
- **Approach**: Internal `.mdc` files as packaged resources
- **User Experience**: No rule authoring required, focus on test writing
- **Extensibility**: Cursor-compatible format for AI assistant integration

## Quality Standards

### Code Quality
- **Coverage**: 80% test coverage (enforced in CI)
- **Typing**: mypy strict mode (no `Any` types allowed)
- **Style**: ruff formatting + comprehensive linting
- **Testing**: TDD approach with pytest

### Release Management
- **Versioning**: Semantic versioning with conventional commits
- **Automation**: GitHub Actions for CI/CD pipeline
- **Distribution**: Automated PyPI publishing via semantic-release

## Current Implementation Highlights

### Completed Core Features
- **🎯 Smart Deduplication**: Hash-based caching prevents redundant LLM API calls
- **📋 Rule Management**: Automatic loading of packaged `.mdc` prompt templates
- **🔄 Dual APIs**: Both `@llm_eval` decorator and `llm_eval()` fixture fully functional
- **📊 Comprehensive Testing**: Full test suite with 80%+ coverage
- **🛠️ Developer Experience**: Pre-commit hooks, CI debugging tools, comprehensive docs

### Integration with Development Ecosystem
- **Cursor AI Compatibility**: Built-in `.mdc` rules work seamlessly with Cursor AI
- **pytest Integration**: Native pytest plugin with standard fixture patterns
- **CI/CD Ready**: GitHub Actions workflows with quality gates
- **Documentation First**: MkDocs with comprehensive developer guides

## Project Goals

### Short-term (v1.0.0)
- Complete CLI interface implementation
- Establish stable API contracts
- Production-ready CI/CD pipeline
- Comprehensive documentation and examples

### Long-term Vision
- Industry-standard tool for qualitative testing
- Integration with major AI development workflows
- Extension ecosystem for domain-specific rules
- Enterprise-grade monitoring and reporting

## Maintainer Information

### Primary Contact
**Organization**: Numerous
**Repository**: https://github.com/numerous-com/pytest-llm-validate
**Documentation**: https://pytest-llm-validate.readthedocs.io/

### Development Philosophy
- **Quality First**: 80% test coverage, strict typing, comprehensive linting
- **User-Centric**: Minimal boilerplate, intuitive APIs, clear documentation
- **AI-Native**: Built for LLM integration from the ground up
- **Open Source**: MIT licensed, community-driven development

### Key Constraints
- **Python Version**: 3.12+ (modern Python features)
- **Dependencies**: Minimal, well-maintained packages only
- **Performance**: Efficient deduplication, background LLM calls
- **Compatibility**: Works with existing pytest workflows

## Technical Debt & Considerations

### Known Limitations
- **LLM Dependency**: Requires external API access (OpenAI)
- **Cost Implications**: API usage costs for extensive test suites
- **Response Variability**: Non-deterministic LLM responses

### Mitigation Strategies
- **Caching**: Aggressive deduplication to minimize API calls
- **Mocking**: Comprehensive test mocking for development
- **Fallback**: Graceful degradation when API unavailable
- **Monitoring**: Integration with Logfire for observability

## References

- **[Product Requirements Document](product-requirements.md)** - Complete specification and roadmap
- **[Developer Workflow](developer-workflow.md)** - Development practices and guidelines
- **[CI Debugging](ci-debugging.md)** - Debugging tools and techniques
- **[PydanticAI Documentation](https://ai.pydantic.dev/install/)** - AI framework integration
- **[pytest Plugin Development](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)** - Plugin architecture
- **[MCP Specification](https://modelcontextprotocol.io/)** - Model Context Protocol
- **[Semantic Release](https://semantic-release.gitbook.io/)** - Automated versioning
