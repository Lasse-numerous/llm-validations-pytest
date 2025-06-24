# CI Debugging Guide

This guide explains how to debug GitHub Actions CI failures for pytest-LLM-Validate.

## Overview

**All validation runs automatically via pre-commit hooks:**
- `git commit` → Quick validation (ruff, mypy, quick tests, commit format)
- `git push` → Full validation (complete test suite with coverage, mirrors CI exactly)

**The debugging script is only needed when GitHub Actions CI fails after you push.**

## When to Use CI Debugging

You should use CI debugging when:

1. Your local `git push` succeeded (pre-push hooks passed)
2. But GitHub Actions CI failed in the cloud
3. You need to understand why the cloud CI failed

## Using the Debug Script

```bash
# Run the CI debugging script
./scripts/debug-ci.sh
```

This script provides GitHub CLI commands for debugging CI failures:

```bash
# Common debugging commands shown by the script:
gh run list --workflow=ci.yml    # List recent CI runs
gh run watch                     # Watch the latest run live
gh run view --log                # View detailed failure logs
gh workflow run ci.yml           # Manually trigger a new CI run
```

## Typical CI Debugging Workflow

1. **Push your changes** (local validation passes):
   ```bash
   git push origin your-branch
   # ✅ Pre-push hooks pass - full test suite with coverage runs locally
   ```

2. **GitHub Actions CI fails** (check GitHub Actions tab)

3. **Run the debug script**:
   ```bash
   ./scripts/debug-ci.sh
   ```

4. **View the failure logs**:
   ```bash
   gh run view --log
   ```

5. **Fix the issue locally** and push again:
   ```bash
   # Fix the issue
   git add .
   git commit -m "fix(ci): address GitHub Actions failure"
   git push origin your-branch
   # Pre-push validation runs again, then CI runs again
   ```

## Common CI Issues

### Environment Differences

Even though pre-push hooks mirror CI exactly, sometimes there are environment differences:

- **Python version**: CI runs on Python 3.12 and 3.13, you might be using different version
- **Dependencies**: CI installs fresh dependencies, you might have different versions cached
- **OS differences**: CI runs on Ubuntu, you might be on Mac/Windows

### Debugging Commands

```bash
# List all recent CI runs
gh run list --workflow=ci.yml

# Watch a specific run live
gh run watch [RUN_ID]

# View logs for a specific run
gh run view [RUN_ID] --log

# View logs for the latest run
gh run view --log

# Trigger a new CI run manually
gh workflow run ci.yml --ref your-branch
```

### GitHub CLI Setup

If you don't have GitHub CLI installed:

```bash
# Install GitHub CLI (choose your platform)
# Mac:
brew install gh

# Ubuntu/Debian:
sudo apt install gh

# Or download from: https://cli.github.com/

# Authenticate
gh auth login
```

## Pre-commit vs CI Relationship

**Pre-commit mirrors CI exactly:**
- Same commands
- Same dependencies
- Same coverage thresholds
- Same pytest configuration

**The only differences should be:**
- Environment (local vs GitHub Actions)
- Python version (if you're not using 3.12/3.13)
- Fresh dependency installation in CI

## Troubleshooting

### "No workflow runs found"

If you see this when running `gh run list`:
- Make sure you're in the correct repository directory
- Check that you have pushed commits recently
- Verify the workflow file exists at `.github/workflows/ci.yml`

### "gh: command not found"

Install GitHub CLI:
```bash
# Mac
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
winget install GitHub.cli
```

### Authentication Issues

```bash
# Re-authenticate with GitHub
gh auth login

# Check current authentication
gh auth status
```

## Manual CI Triggering

You can manually trigger CI for debugging:

```bash
# Trigger CI on current branch
gh workflow run ci.yml

# Trigger CI on specific branch
gh workflow run ci.yml --ref your-branch-name
```

## Related Documentation

- [Developer Workflow Guide](developer-workflow.md) - Complete development process
- [Contributing Guidelines](https://github.com/numerous-com/pytest-llm-validate/blob/main/CONTRIBUTING.md) - Contribution guidelines
- [CI Fix Summary](https://github.com/numerous-com/pytest-llm-validate/blob/main/CI_FIX_SUMMARY.md) - Historical CI fixes and learnings
