#!/bin/bash
# CI Debugging Tools
# NOTE: All validation runs automatically via .pre-commit-config.yaml
# This script provides GitHub CLI commands for debugging CI failures

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

print_usage() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "      GitHub Actions CI Debugging"
    echo "=============================================="
    echo -e "${NC}"

    log_warning "NOTE: All validation runs automatically via pre-commit hooks!"
    echo "  → git commit: ruff, mypy, quick tests, conventional commits"
    echo "  → git push: full test suite with coverage (mirrors GitHub Actions)"
    echo ""
    log_info "This script is for debugging CI failures only"
    echo ""
}

main() {
    print_usage
    debug_ci
}

main "$@"
