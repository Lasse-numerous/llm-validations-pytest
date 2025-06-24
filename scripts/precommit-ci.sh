#!/bin/bash
# Pre-commit Development Tools
# PRE-PUSH: Validate local changes with CI mirroring
# POST-PUSH: Debug GitHub Actions CI with GitHub CLI tools

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



run_full_tests() {
    log_info "Running full test suite (CI mirror for pre-commit validation)..."
    
    log_warning "IMPORTANT: This validates LOCAL changes before push"
    echo "  → Mirrors GitHub Actions CI commands as closely as possible"
    echo "  → Use this before 'git push' to catch issues early"

    if command -v pytest >/dev/null 2>&1; then
        local pytest_version=$(pytest --version 2>/dev/null | head -1 || echo "unknown")
        log_info "Running mirrored GitHub Actions test command... (${pytest_version})"

        # Show test files being discovered
        local test_files=$(find tests/ -name "test_*.py" 2>/dev/null | wc -l || echo "0")
        echo "  → Discovered ${test_files} test files"
        echo "  → Command: pytest --cov=numerous.pytest_llm_validate --cov-report=xml --cov-report=term-missing"
        echo "  → This mirrors .github/workflows/ci.yml test command"

        # Run the same command as GitHub Actions CI
        if pytest --cov=numerous.pytest_llm_validate --cov-report=xml --cov-report=term-missing 2>&1; then
            log_success "✓ Pre-commit CI validation passed"
            echo "  → Local changes should pass GitHub Actions CI"
        else
            log_error "✗ Pre-commit CI validation failed"
            echo ""
            log_error "These failures will cause GitHub Actions CI to fail!"
            log_info "Fix the issues above before pushing"
            return 1
        fi
    else
        log_warning "Pytest not found, skipping tests"
    fi
}

debug_ci() {
    log_info "GitHub Actions CI debugging tools..."
    
    # Check if GitHub CLI is available
    if ! command -v gh >/dev/null 2>&1; then
        log_error "GitHub CLI (gh) not found!"
        echo "  → Install with: brew install gh (macOS) or apt install gh (Ubuntu)"
        echo "  → Or download from: https://cli.github.com/"
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
    echo "  → Trigger new CI run: gh workflow run ci.yml"
    echo ""
    
    log_info "Recent CI runs:"
    if gh run list --workflow=ci.yml --limit=5 2>/dev/null; then
        echo ""
        log_info "Use 'gh run view <run-id> --log' to see detailed logs"
    else
        log_warning "Could not fetch recent runs"
    fi
}

validate_commit_messages() {
    log_info "Validating recent commit messages..."

    # Define allowed types and scopes
    local allowed_types="feat fix docs style refactor perf test build ci chore revert"
    local allowed_scopes="core test docs ci build feat fix perf style refactor chore config scripts api cli web data security deps"

    # Check only the current commit (HEAD) for pre-push validation
    local commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    local check_count=1

    if [ "$check_count" -eq 0 ]; then
        log_warning "No commits found to validate"
        return 0
    fi

    echo "  → Checking current commit message (HEAD)"

    local invalid_commits=0
    for i in $(seq 0 $((check_count - 1))); do
        local commit_msg=$(git log --format=%s -n 1 HEAD~$i 2>/dev/null)
        local commit_hash=$(git log --format=%h -n 1 HEAD~$i 2>/dev/null)

        # Check if message matches conventional commit pattern: type(scope): description
        if echo "$commit_msg" | grep -qE '^[a-z]+\([^)]+\): .+'; then
            # Extract type (everything before the first parenthesis)
            local type="${commit_msg%%(*}"
            # Extract scope (everything between parentheses)
            local temp="${commit_msg#*(}"
            local scope="${temp%%)*}"

            # Check if type is allowed
            local type_valid=false
            for allowed_type in $allowed_types; do
                if [[ "$type" == "$allowed_type" ]]; then
                    type_valid=true
                    break
                fi
            done

            # Check if scope is allowed
            local scope_valid=false
            for allowed_scope in $allowed_scopes; do
                if [[ "$scope" == "$allowed_scope" ]]; then
                    scope_valid=true
                    break
                fi
            done

            if [[ "$type_valid" == true && "$scope_valid" == true ]]; then
                echo "    ✓ ${commit_hash}: ${type}(${scope}) - Valid"
            elif [[ "$type_valid" == false ]]; then
                echo "    ✗ ${commit_hash}: Invalid type '${type}'"
                echo "      Allowed types: ${allowed_types}"
                invalid_commits=$((invalid_commits + 1))
            else
                echo "    ✗ ${commit_hash}: Invalid scope '${scope}'"
                echo "      Allowed scopes: ${allowed_scopes}"
                invalid_commits=$((invalid_commits + 1))
            fi
        else
            echo "    ✗ ${commit_hash}: Invalid format"
            echo "      Expected: type(scope): description"
            echo "      Got: ${commit_msg}"
            invalid_commits=$((invalid_commits + 1))
        fi
    done

    if [ "$invalid_commits" -eq 0 ]; then
        log_success "✓ All commit messages follow conventional format"
    else
        log_error "✗ ${invalid_commits} commit message(s) don't follow conventional format"
        echo ""
        echo "  Required format: type(scope): description"
        echo "  Valid types: ${allowed_types}"
        echo "  Valid scopes: ${allowed_scopes}"
        echo ""
        echo "  Examples:"
        echo "    feat(core): add new authentication system"
        echo "    fix(test): resolve failing unit tests"
        echo "    docs(api): update endpoint documentation"
        echo "    chore(deps): update dependencies"
        return 1
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
    echo "      Pre-commit Development Tools"
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
            echo ""
            validate_commit_messages
            print_validation_summary "lint"
            ;;
        "test")
            run_quick_tests
            echo ""
            validate_commit_messages
            print_validation_summary "test"
            ;;
        "all")
            run_lint_checks
            echo ""
            run_full_tests
            echo ""
            validate_commit_messages
            print_validation_summary "comprehensive"
            ;;
        "commit-check")
            validate_commit_messages
            print_validation_summary "commit-validation"
            ;;
        "full-test")
            run_full_tests
            echo ""
            validate_commit_messages
            print_validation_summary "full-test"
            ;;
        "debug-ci")
            debug_ci
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Usage: $0 {lint|test|all|full-test|commit-check|debug-ci}"
            echo ""
            echo "PRE-COMMIT COMMANDS (validate local changes before push):"
            echo "  lint        - Run linting checks + commit validation"
            echo "  test        - Run quick tests + commit validation"
            echo "  all         - Run linting + full tests + commit validation (recommended)"
            echo "  full-test   - Run full test suite with coverage (mirrors GitHub Actions)"
            echo "  commit-check - Run only commit message validation"
            echo ""
            echo "POST-PUSH COMMANDS (debug GitHub Actions CI):"
            echo "  debug-ci    - Show GitHub CLI commands to watch/debug CI runs"
            echo ""
            echo "WORKFLOW:"
            echo "  1. Make changes locally"
            echo "  2. Run: ./scripts/precommit-ci.sh all"
            echo "  3. Fix any issues found"
            echo "  4. Push: git push"
            echo "  5. If CI fails: ./scripts/precommit-ci.sh debug-ci"
            exit 1
            ;;
    esac
}

main "$@"
