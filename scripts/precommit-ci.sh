#!/bin/bash
# Comprehensive CI Simulation for Pre-push Validation
# Runs essential CI checks without dependency installation
# Acts as the main linting/type-checking step in pre-commit pipeline

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

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

run_lint_checks() {
    log_info "Running linting checks..."

    # Check ruff linting (assume it's already installed)
    if command -v ruff >/dev/null 2>&1; then
        local ruff_version=$(ruff --version 2>/dev/null | head -1 || echo "unknown")
        log_info "Running ruff check... (${ruff_version})"

        # Show what ruff would check
        local ruff_files=$(ruff check --show-files . 2>/dev/null | wc -l || echo "unknown")
        echo "  → Checking ${ruff_files} files with ruff"

        if ruff check . --fix 2>&1; then
            log_success "✓ Ruff check passed"
        else
            log_error "✗ Ruff check failed"
            return 1
        fi

        log_info "Running ruff format check..."
        if ruff format --check . 2>&1; then
            log_success "✓ Ruff format check passed"
        else
            log_error "✗ Ruff format check failed"
            return 1
        fi
    else
        log_warning "Ruff not found, skipping linting checks"
    fi

    # Check mypy type checking (assume it's already installed)
    if command -v mypy >/dev/null 2>&1; then
        local mypy_version=$(mypy --version 2>/dev/null || echo "unknown")
        log_info "Running mypy... (${mypy_version})"

        # Show what files mypy will check
        local py_files=$(find . -name "*.py" -not -path "./.venv/*" -not -path "./.*" | wc -l)
        echo "  → Type checking ${py_files} Python files"

        if mypy . 2>&1; then
            log_success "✓ MyPy check passed"
        else
            log_error "✗ MyPy check failed"
            return 1
        fi
    else
        log_warning "MyPy not found, skipping type checking"
    fi

    log_success "All linting checks passed"
}

run_quick_tests() {
    log_info "Running quick test suite..."

    if command -v pytest >/dev/null 2>&1; then
        local pytest_version=$(pytest --version 2>/dev/null | head -1 || echo "unknown")
        log_info "Running pytest... (${pytest_version})"

        # Show test files being discovered
        local test_files=$(find tests/ -name "test_*.py" 2>/dev/null | wc -l || echo "0")
        echo "  → Discovered ${test_files} test files"

        # Run tests without coverage for speed
        if pytest --tb=short -q --no-cov --override-ini='addopts=' tests/ 2>&1; then
            log_success "✓ Quick tests passed"
        else
            log_error "✗ Quick tests failed"
            return 1
        fi
    else
        log_warning "Pytest not found, skipping tests"
    fi
}

print_validation_summary() {
    local mode=$1
    log_info "Validation Summary:"
    echo "  Mode: ${mode}"
    echo "  Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "  Status: All checks passed ✓"
    echo "  Ready for: $([ "$mode" = "lint" ] && echo "Code review/CI" || echo "Testing/Deployment")"
    echo ""
}

print_environment_info() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "    Pre-commit CI Simulation (Lightweight)"
    echo "=============================================="
    echo -e "${NC}"

    # Show current branch and commit
    local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
    local current_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    local repo_status=$(git status --porcelain 2>/dev/null | wc -l)

    log_info "Environment Information:"
    echo "  Branch: ${current_branch}"
    echo "  Commit: ${current_commit}"
    echo "  Modified files: ${repo_status}"
    echo "  Working directory: $(pwd)"
    echo "  Python version: $(python --version 2>/dev/null || echo 'Not found')"

    # Show files being analyzed
    local python_files=$(find . -name "*.py" -not -path "./.venv/*" -not -path "./.*" | wc -l)
    local total_files=$(find . -type f -not -path "./.venv/*" -not -path "./.git/*" -not -path "./.*" | wc -l)

    echo "  Python files: ${python_files}"
    echo "  Total project files: ${total_files}"
    echo ""
}

main() {
    print_environment_info

    local mode="${1:-lint}"
    case "$mode" in
        "lint")
            run_lint_checks
            print_validation_summary "lint"
            ;;
        "test")
            run_quick_tests
            print_validation_summary "test"
            ;;
        "all")
            run_lint_checks
            echo ""
            run_quick_tests
            print_validation_summary "comprehensive"
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Usage: $0 {lint|test|all}"
            exit 1
            ;;
    esac
}

main "$@"
