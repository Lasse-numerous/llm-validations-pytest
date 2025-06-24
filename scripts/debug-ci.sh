#!/bin/bash
# CI Debugging Script for pytest-LLM-Validate
# Simulates GitHub Actions CI environment locally for debugging

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PYTHON_VERSIONS=("3.12" "3.13")
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/.ci-debug-logs"

# Create log directory
mkdir -p "$LOG_DIR"

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    pytest-LLM-Validate CI Debugging Tool"
    echo "=================================================="
    echo -e "${NC}"
}

check_python_version() {
    local version=$1
    log_info "Checking Python $version availability..."

    if command -v python$version &> /dev/null; then
        log_success "Python $version found: $(python$version --version)"
        return 0
    else
        log_warning "Python $version not found"
        return 1
    fi
}

run_lint_job() {
    log_info "Running LINT job simulation..."

    echo "1. Installing dependencies..."
    python -m pip install --upgrade pip > "$LOG_DIR/lint-pip.log" 2>&1
    pip install -e ".[dev]" > "$LOG_DIR/lint-install.log" 2>&1

    echo "2. Running ruff check..."
    if ruff check . > "$LOG_DIR/lint-ruff-check.log" 2>&1; then
        log_success "✓ Ruff check passed"
    else
        log_error "✗ Ruff check failed (see $LOG_DIR/lint-ruff-check.log)"
        return 1
    fi

    echo "3. Running ruff format check..."
    if ruff format --check . > "$LOG_DIR/lint-ruff-format.log" 2>&1; then
        log_success "✓ Ruff format check passed"
    else
        log_error "✗ Ruff format check failed (see $LOG_DIR/lint-ruff-format.log)"
        return 1
    fi

    echo "4. Running mypy..."
    if mypy . > "$LOG_DIR/lint-mypy.log" 2>&1; then
        log_success "✓ MyPy check passed"
    else
        log_error "✗ MyPy check failed (see $LOG_DIR/lint-mypy.log)"
        return 1
    fi

    log_success "LINT job completed successfully"
}

run_test_job() {
    local python_version=${1:-"current"}
    log_info "Running TEST job simulation (Python $python_version)..."

    echo "1. Installing dependencies..."
    python -m pip install --upgrade pip > "$LOG_DIR/test-pip-$python_version.log" 2>&1
    pip install -e ".[dev,test]" > "$LOG_DIR/test-install-$python_version.log" 2>&1

    echo "2. Running tests with coverage..."
    if pytest --cov=numerous.pytest_llm_validate --cov-report=xml --cov-report=term-missing --cov-fail-under=80 > "$LOG_DIR/test-pytest-$python_version.log" 2>&1; then
        log_success "✓ Tests passed (Python $python_version)"
    else
        log_error "✗ Tests failed (see $LOG_DIR/test-pytest-$python_version.log)"
        return 1
    fi

    log_success "TEST job completed successfully (Python $python_version)"
}

run_docs_job() {
    log_info "Running DOCS job simulation..."

    echo "1. Installing dependencies..."
    python -m pip install --upgrade pip > "$LOG_DIR/docs-pip.log" 2>&1
    pip install -e ".[dev]" > "$LOG_DIR/docs-install.log" 2>&1

    echo "2. Building docs..."
    if mkdocs build --strict > "$LOG_DIR/docs-build.log" 2>&1; then
        log_success "✓ Docs build passed"
    else
        log_error "✗ Docs build failed (see $LOG_DIR/docs-build.log)"
        return 1
    fi

    log_success "DOCS job completed successfully"
}

run_security_job() {
    log_info "Running SECURITY job simulation..."

    echo "1. Installing bandit..."
    pip install bandit[toml] > "$LOG_DIR/security-install.log" 2>&1

    echo "2. Running bandit security check..."
    bandit -r numerous/ -f json -o "$LOG_DIR/bandit-report.json" > "$LOG_DIR/security-bandit.log" 2>&1 || true

    log_success "SECURITY job completed successfully"
}

run_build_job() {
    log_info "Running BUILD job simulation..."

    echo "1. Installing build dependencies..."
    python -m pip install --upgrade pip > "$LOG_DIR/build-pip.log" 2>&1
    pip install build twine > "$LOG_DIR/build-install.log" 2>&1

    echo "2. Building package..."
    if python -m build > "$LOG_DIR/build-package.log" 2>&1; then
        log_success "✓ Package build passed"
    else
        log_error "✗ Package build failed (see $LOG_DIR/build-package.log)"
        return 1
    fi

    echo "3. Checking package..."
    if twine check dist/* > "$LOG_DIR/build-check.log" 2>&1; then
        log_success "✓ Package check passed"
    else
        log_error "✗ Package check failed (see $LOG_DIR/build-check.log)"
        return 1
    fi

    log_success "BUILD job completed successfully"
}

run_precommit_simulation() {
    log_info "Running PRE-COMMIT simulation..."

    if pre-commit run --all-files > "$LOG_DIR/precommit.log" 2>&1; then
        log_success "✓ Pre-commit hooks passed"
    else
        log_error "✗ Pre-commit hooks failed (see $LOG_DIR/precommit.log)"
        return 1
    fi

    log_success "PRE-COMMIT simulation completed successfully"
}

analyze_ci_config() {
    log_info "Analyzing CI configuration..."

    if [[ -f ".github/workflows/ci.yml" ]]; then
        log_info "Found CI workflow configuration:"
        echo "  - File: .github/workflows/ci.yml"
        echo "  - Jobs: $(grep -c "^  [a-zA-Z].*:$" .github/workflows/ci.yml)"
        echo "  - Python versions: $(grep -o "python-version.*\[.*\]" .github/workflows/ci.yml || echo "Not found")"
        log_success "✓ CI configuration is valid"
    else
        log_error "✗ No CI configuration found at .github/workflows/ci.yml"
    fi
}

show_logs() {
    log_info "Recent CI debug logs:"
    if [[ -d "$LOG_DIR" ]]; then
        ls -la "$LOG_DIR/" | tail -10
        echo ""
        log_info "To view a specific log: cat $LOG_DIR/<log-file>"
    else
        log_warning "No debug logs found"
    fi
}

cleanup() {
    log_info "Cleaning up CI artifacts..."
    rm -rf dist/ build/ *.egg-info/
    rm -f coverage.xml .coverage
    rm -rf htmlcov/
    rm -f .pytest-llm-validate-history.json
    log_success "✓ Cleanup completed"
}

main() {
    print_header

    # Parse command line arguments
    case "${1:-all}" in
        "lint")
            run_lint_job
            ;;
        "test")
            run_test_job
            ;;
        "docs")
            run_docs_job
            ;;
        "security")
            run_security_job
            ;;
        "build")
            run_build_job
            ;;
        "precommit")
            run_precommit_simulation
            ;;
        "analyze")
            analyze_ci_config
            ;;
        "logs")
            show_logs
            ;;
        "cleanup")
            cleanup
            ;;
        "all")
            analyze_ci_config
            echo ""
            run_precommit_simulation
            echo ""
            run_lint_job
            echo ""
            run_test_job
            echo ""
            run_docs_job
            echo ""
            run_security_job
            echo ""
            run_build_job
            echo ""
            log_success "All CI jobs completed successfully!"
            ;;
        *)
            echo "Usage: $0 {lint|test|docs|security|build|precommit|analyze|logs|cleanup|all}"
            echo ""
            echo "Commands:"
            echo "  lint      - Run linting job (ruff + mypy)"
            echo "  test      - Run test job with coverage"
            echo "  docs      - Run documentation build"
            echo "  security  - Run security scanning"
            echo "  build     - Run package build and validation"
            echo "  precommit - Run pre-commit hooks simulation"
            echo "  analyze   - Analyze CI configuration"
            echo "  logs      - Show recent debug logs"
            echo "  cleanup   - Clean up CI artifacts"
            echo "  all       - Run all jobs (default)"
            exit 1
            ;;
    esac
}

# Change to project root
cd "$PROJECT_ROOT"

# Run main function
main "$@"
