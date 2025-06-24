#!/bin/bash
# Manual Development Tools
# NOTE: All validation now runs automatically via .pre-commit-config.yaml
# This script is for manual execution and debugging only

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

print_info() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "      Manual Development Tools"
    echo "=============================================="
    echo -e "${NC}"

    log_warning "NOTE: Pre-commit validation now runs automatically!"
    echo "  → On commit: ruff, mypy, quick tests, conventional commits"
    echo "  → On push: full test suite with coverage"
    echo "  → This script is for manual execution only"
    echo ""
}

run_manual_lint() {
    log_info "Running manual linting..."
    echo "  → Same as automatic pre-commit hooks"

    if command -v ruff >/dev/null 2>&1; then
        log_info "Running ruff..."
        ruff check . --fix
        ruff format .
        log_success "✓ Ruff completed"
    else
        log_error "Ruff not found"
        return 1
    fi

    if command -v mypy >/dev/null 2>&1; then
        log_info "Running mypy..."
        mypy .
        log_success "✓ MyPy completed"
    else
        log_error "MyPy not found"
        return 1
    fi
}

run_manual_tests() {
    local test_type="${1:-quick}"

    if [ "$test_type" = "quick" ]; then
        log_info "Running quick tests (same as commit hooks)..."
        pytest --tb=short -q --no-cov --override-ini=addopts= tests/
        log_success "✓ Quick tests completed"
    elif [ "$test_type" = "full" ]; then
        log_info "Running full tests with coverage (same as pre-push hooks)..."
        pytest --cov=numerous.pytest_llm_validate --cov-report=xml --cov-report=term-missing
        log_success "✓ Full tests completed"
    else
        log_error "Unknown test type: $test_type"
        echo "  → Use 'quick' or 'full'"
        return 1
    fi
}

debug_ci() {
    log_info "GitHub Actions CI debugging tools..."

    # Check if GitHub CLI is available
    if ! command -v gh >/dev/null 2>&1; then
        log_error "GitHub CLI (gh) not found!"
        echo "  → Install with: brew install gh (macOS) or apt install gh (Ubuntu)"
        return 1
    fi

    # Check if user is authenticated
    if ! gh auth status >/dev/null 2>&1; then
        log_error "Not authenticated with GitHub CLI!"
        echo "  → Run: gh auth login"
        return 1
    fi

    log_info "Available CI debugging commands:"
    echo "  → Watch latest CI run: gh run watch"
    echo "  → List recent runs: gh run list --workflow=ci.yml"
    echo "  → View latest run logs: gh run view --log"
    echo "  → Trigger manual CI run: gh workflow run ci.yml"
    echo ""

    log_info "Recent CI runs:"
    if gh run list --workflow=ci.yml --limit=5 2>/dev/null; then
        echo ""
        log_info "Use 'gh run view <run-id> --log' to see detailed logs"
    else
        log_warning "Could not fetch recent runs"
    fi
}

main() {
    print_info

    local command="${1:-help}"
    case "$command" in
        "lint")
            run_manual_lint
            ;;
        "test")
            run_manual_tests quick
            ;;
        "test-full")
            run_manual_tests full
            ;;
        "debug-ci")
            debug_ci
            ;;
        "help"|*)
            echo "MANUAL COMMANDS (for debugging and manual execution):"
            echo "  lint        - Run ruff + mypy manually"
            echo "  test        - Run quick tests manually"
            echo "  test-full   - Run full tests with coverage manually"
            echo "  debug-ci    - Show GitHub CLI commands for CI debugging"
            echo ""
            echo "AUTOMATIC VALIDATION (no commands needed):"
            echo "  git commit  - Automatically runs: ruff, mypy, quick tests, commit validation"
            echo "  git push    - Automatically runs: full test suite with coverage"
            echo ""
            echo "WORKFLOW:"
            echo "  1. Make changes locally"
            echo "  2. git commit (automatic validation runs)"
            echo "  3. git push (automatic full tests run)"
            echo "  4. If CI fails: ./scripts/precommit-ci.sh debug-ci"

            if [ "$command" != "help" ]; then
                exit 1
            fi
            ;;
    esac
}

main "$@"
