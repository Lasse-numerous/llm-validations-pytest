#!/bin/bash
# Lightweight CI Simulation for Pre-commit Hooks
# Runs essential CI checks without dependency installation

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
        log_info "Running ruff check..."
        if ruff check .; then
            log_success "✓ Ruff check passed"
        else
            log_error "✗ Ruff check failed"
            return 1
        fi

        log_info "Running ruff format check..."
        if ruff format --check .; then
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
        log_info "Running mypy..."
        if mypy .; then
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
        # Run tests without coverage for speed
        if pytest --tb=short -q --no-cov --override-ini='addopts=' tests/; then
            log_success "✓ Quick tests passed"
        else
            log_error "✗ Quick tests failed"
            return 1
        fi
    else
        log_warning "Pytest not found, skipping tests"
    fi
}

main() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "    Pre-commit CI Simulation (Lightweight)"
    echo "=============================================="
    echo -e "${NC}"

    case "${1:-lint}" in
        "lint")
            run_lint_checks
            ;;
        "test")
            run_quick_tests
            ;;
        "all")
            run_lint_checks
            echo ""
            run_quick_tests
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Usage: $0 {lint|test|all}"
            exit 1
            ;;
    esac
}

main "$@"
