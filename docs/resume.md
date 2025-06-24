# Project Resume: pytest-LLM-Validate

## Project Overview

**pytest-LLM-Validate** is a pytest plugin that enables AI-driven qualitative testing by integrating Large Language Models into the testing workflow. The project aims to bridge the gap between traditional automated testing and qualitative evaluation criteria.

## Technical Architecture

### Core Components

1. **Rule System**: Packaged `.mdc` (Markdown-Cursor) files containing LLM prompts
2. **Evaluation APIs**: Decorator (`@llm_eval`) and fixture-based (`llm_eval()`) interfaces
3. **Agent Integration**: PydanticAI-powered evaluation with OpenAI o4-mini
4. **Multi-Interface Support**: Core library → CLI → REST API → MCP integration

### Technology Stack

- **Language**: Python 3.12+ (CI tested on 3.12 & 3.13)
- **AI Framework**: PydanticAI with OpenAI integration
- **Testing**: pytest ecosystem with 100% coverage requirement
- **Code Quality**: ruff (format + lint) + mypy (strict mode)
- **Web Framework**: FastAPI for REST API
- **CLI Framework**: Click for command-line interface
- **Documentation**: MkDocs with Material theme
- **CI/CD**: GitHub Actions + semantic-release

## Development Status

**Current Phase**: Phase 1 - Repository & Toolchain Foundation (v0.1.0-rc1)

### Completed Tasks
- [x] Repository scaffolding with pyproject.toml
- [x] Package structure setup
- [x] Initial README and documentation
- [x] Contributing guidelines and workflow

### Upcoming Phases
- **Phase 2**: Core library implementation (loader, decorator, fixture APIs)
- **Phase 3**: CLI interface development
- **Phase 4**: FastAPI REST backend
- **Phase 5**: MCP (Model Context Protocol) integration
- **Phase 6**: Advanced reporting and QA
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
- **Coverage**: 100% test coverage (enforced)
- **Typing**: mypy strict mode (no `Any` types allowed)
- **Style**: ruff formatting + comprehensive linting
- **Testing**: TDD approach with pytest

### Release Management
- **Versioning**: Semantic versioning with conventional commits
- **Automation**: GitHub Actions for CI/CD pipeline
- **Distribution**: Automated PyPI publishing via semantic-release

## Project Goals

### Short-term (v1.0.0)
- Complete core functionality implementation
- Establish stable API contracts
- Comprehensive documentation and examples
- Production-ready CI/CD pipeline

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
- **Quality First**: 100% test coverage, strict typing, comprehensive linting
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

- [PydanticAI Documentation](https://ai.pydantic.dev/install/)
- [pytest Plugin Development](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Semantic Release](https://semantic-release.gitbook.io/)
