# Contributing to pytest-LLM-Validate

First off, thank you for considering contributing to pytest-LLM-Validate! It's people like you that make such projects successful.

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [support@numerous.ai](mailto:support@numerous.ai).

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for pytest-LLM-Validate. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for pytest-LLM-Validate, including completely new features and minor improvements to existing functionality.

### Your First Code Contribution

Unsure where to begin contributing to pytest-LLM-Validate? You can start by looking through `good first issue` and `help wanted` issues.

### Pull Requests

The process described here has several goals:
- Maintain pytest-LLM-Validate's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible pytest-LLM-Validate
- Enable a sustainable system for pytest-LLM-Validate's maintainers to review contributions

## Development Workflow

### Branching Strategy

We use a feature-branch workflow. All development for new features, bug fixes, or documentation should happen in branches based off `main`.

Branch naming convention:
- `feat/<ticket#>-short-desc` for new features (e.g., `feat/1.1-scaffold-repo`)
- `fix/<ticket#>-short-desc` for bug fixes (e.g., `fix/2.3-resolve-npe`)
- `docs/<ticket#>-short-desc` for documentation changes (e.g., `docs/1.2-contributing`)
- `test/<ticket#>-short-desc` for test-related changes (e.g., `test/1.4-red-skeleton`)
- `chore/<ticket#>-short-desc` for maintenance tasks (e.g., `chore/1.3-setup-ci`)

### Committing Changes

Please follow these commit message conventions. We use this to auto-generate changelogs and manage releases.

Commit message format: `type(scope): concise summary`

Allowed `type` values:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- `ci`: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
- `chore`: Other changes that don't modify `src` or `test` files
- `revert`: Reverts a previous commit

The `scope` should be the name of the module affected (as perceived by the person reading the changelog generated from commit messages).

Example: `feat(loader): add support for .yaml rule files`

### Pull Request (PR) Guidelines

- **Title:** Your PR title should follow the commit message format (e.g., `feat(core): implement new evaluation strategy`).
- **Link to Issue:** If your PR addresses an existing issue, please include `Closes #<issue_number>` or `Fixes #<issue_number>` in the PR description.
- **Description:** Provide a clear and concise description of the changes. Explain the "why" behind your changes.
- **Tests:** Ensure that all new code is covered by tests. PRs that decrease test coverage will not be merged. All tests must pass in CI.
- **Squash and Merge:** We use squash and merge for all PRs into `main`. This keeps our commit history clean and readable. Ensure your PR has a clear and descriptive title, as this will become the commit message.

Thank you for your contribution!
