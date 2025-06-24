#!/usr/bin/env python3
"""
CI Monitoring and Debugging Script for pytest-LLM-Validate
Provides real-time monitoring and debugging of GitHub Actions CI runs
"""

import json
import subprocess  # nosec B404
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"
    RESET = "\033[0m"


class CIMonitor:
    """Monitor and debug GitHub Actions CI runs."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).parent.parent
        self.log_dir = self.project_root / ".ci-debug-logs"
        self.log_dir.mkdir(exist_ok=True)

    def log(self, message: str, color: str = Colors.WHITE) -> None:
        """Log a message with color."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.RESET}")

    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.log(f"[INFO] {message}", Colors.BLUE)

    def log_success(self, message: str) -> None:
        """Log a success message."""
        self.log(f"[SUCCESS] {message}", Colors.GREEN)

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.log(f"[WARNING] {message}", Colors.YELLOW)

    def log_error(self, message: str) -> None:
        """Log an error message."""
        self.log(f"[ERROR] {message}", Colors.RED)

    def run_command(
        self, cmd: list[str], capture_output: bool = True
    ) -> dict[str, Any]:
        """Run a command and return the result."""
        try:
            result = subprocess.run(  # nosec B603
                cmd, capture_output=capture_output, text=True, cwd=self.project_root
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

    def check_gh_auth(self) -> bool:
        """Check if GitHub CLI is authenticated."""
        result = self.run_command(["gh", "auth", "status"])
        return bool(result["success"])

    def get_recent_runs(self, limit: int = 10) -> list[dict[str, Any]] | None:
        """Get recent CI runs."""
        if not self.check_gh_auth():
            self.log_warning("GitHub CLI not authenticated. Run: gh auth login")
            return None

        result = self.run_command(
            [
                "gh",
                "run",
                "list",
                "--limit",
                str(limit),
                "--json",
                "databaseId,headBranch,status,conclusion,createdAt,event,workflowName",
            ]
        )

        if result["success"]:
            try:
                parsed_result: list[dict[str, Any]] = json.loads(result["stdout"])
                return parsed_result
            except json.JSONDecodeError:
                self.log_error("Failed to parse CI runs JSON")
                return None
        else:
            self.log_error(f"Failed to get CI runs: {result['stderr']}")
            return None

    def get_run_details(self, run_id: str) -> dict[str, Any] | None:
        """Get detailed information about a specific CI run."""
        if not self.check_gh_auth():
            return None

        result = self.run_command(
            [
                "gh",
                "run",
                "view",
                run_id,
                "--json",
                "jobs,status,conclusion,createdAt,updatedAt",
            ]
        )

        if result["success"]:
            try:
                parsed_result: dict[str, Any] = json.loads(result["stdout"])
                return parsed_result
            except json.JSONDecodeError:
                self.log_error("Failed to parse run details JSON")
                return None
        else:
            self.log_error(f"Failed to get run details: {result['stderr']}")
            return None

    def get_job_logs(self, run_id: str, job_name: str) -> str | None:
        """Get logs for a specific job."""
        if not self.check_gh_auth():
            return None

        result = self.run_command(
            ["gh", "run", "view", run_id, "--log", "--job", job_name]
        )

        if result["success"]:
            return str(result["stdout"])
        else:
            self.log_error(f"Failed to get job logs: {result['stderr']}")
            return None

    def analyze_failure(self, run_id: str) -> None:
        """Analyze a failed CI run and provide debugging information."""
        self.log_info(f"Analyzing failed CI run: {run_id}")

        run_details = self.get_run_details(run_id)
        if not run_details:
            return

        self.log_info("Run Details:")
        print(f"  Status: {run_details.get('status', 'unknown')}")
        print(f"  Conclusion: {run_details.get('conclusion', 'unknown')}")
        print(f"  Created: {run_details.get('createdAt', 'unknown')}")
        print(f"  Updated: {run_details.get('updatedAt', 'unknown')}")
        print()

        failed_jobs = [
            job
            for job in run_details.get("jobs", [])
            if job.get("conclusion") == "failure"
        ]

        if failed_jobs:
            self.log_error(f"Found {len(failed_jobs)} failed job(s):")
            for job in failed_jobs:
                print(
                    f"  - {job.get('name', 'unknown')}: {job.get('conclusion', 'unknown')}"
                )

                # Get logs for failed job
                job_name = job.get("name", "")
                if job_name:
                    self.log_info(f"Getting logs for job: {job_name}")
                    logs = self.get_job_logs(run_id, job_name)
                    if logs:
                        log_file = (
                            self.log_dir
                            / f"failed-job-{job_name.replace(' ', '-')}-{run_id}.log"
                        )
                        log_file.write_text(logs)
                        self.log_success(f"Logs saved to: {log_file}")

                        # Analyze common failure patterns
                        self.analyze_logs(logs, job_name)
        else:
            self.log_warning("No failed jobs found, but run was not successful")

    def analyze_logs(self, logs: str, job_name: str) -> None:
        """Analyze logs for common failure patterns."""
        self.log_info(f"Analyzing logs for patterns in job: {job_name}")

        patterns = {
            "Coverage failure": [
                "Coverage failure",
                "total of .* is less than fail-under",
                "Required test coverage of .* not reached",
            ],
            "Type errors": ["error: ", "mypy", "type ignore", "incompatible type"],
            "Linting errors": ["ruff check", "E[0-9]+", "W[0-9]+", "F[0-9]+"],
            "Test failures": [
                "FAILED",
                "AssertionError",
                "test.*failed",
                "ERROR.*test",
            ],
            "Import errors": ["ImportError", "ModuleNotFoundError", "No module named"],
            "Build errors": [
                "build failed",
                "setup.py.*error",
                "wheel.*failed",
                "twine.*failed",
            ],
        }

        found_issues = []
        for issue_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern.lower() in logs.lower():
                    found_issues.append(issue_type)
                    break

        if found_issues:
            self.log_warning(
                f"Detected potential issues: {', '.join(set(found_issues))}"
            )

            # Provide specific debugging suggestions
            for issue in set(found_issues):
                self.suggest_fix(issue)
        else:
            self.log_info("No common failure patterns detected")

    def suggest_fix(self, issue_type: str) -> None:
        """Suggest fixes for common issues."""
        suggestions = {
            "Coverage failure": [
                "Run: pytest --cov=numerous.pytest_llm_validate --cov-report=html",
                "Check htmlcov/index.html for uncovered lines",
                "Add tests for uncovered code or adjust coverage threshold",
            ],
            "Type errors": [
                "Run: mypy . --show-error-codes",
                "Add type annotations for function parameters and returns",
                "Check for Any types and replace with specific types",
            ],
            "Linting errors": [
                "Run: ruff check . --fix",
                "Run: ruff format .",
                "Check .pre-commit-config.yaml for hook configuration",
            ],
            "Test failures": [
                "Run specific test: pytest tests/test_file.py::test_function -v",
                "Check test mocking and fixtures",
                "Run tests with --pdb for debugging",
            ],
            "Import errors": [
                "Check dependencies in pyproject.toml",
                "Run: pip install -e .[dev,test]",
                "Verify package structure and __init__.py files",
            ],
            "Build errors": [
                "Check pyproject.toml build-system configuration",
                "Run: python -m build --verbose",
                "Verify setuptools configuration",
            ],
        }

        if issue_type in suggestions:
            print(f"\n{Colors.CYAN}Suggested fixes for {issue_type}:{Colors.RESET}")
            for suggestion in suggestions[issue_type]:
                print(f"  • {suggestion}")
            print()

    def watch_runs(self, interval: int = 30) -> None:
        """Watch CI runs in real-time."""
        self.log_info(f"Watching CI runs (checking every {interval} seconds)...")
        self.log_info("Press Ctrl+C to stop watching")

        try:
            while True:
                runs = self.get_recent_runs(limit=5)
                if runs:
                    print(f"\n{Colors.WHITE}{'=' * 60}{Colors.RESET}")
                    print(f"{Colors.WHITE}Recent CI Runs (last 5):{Colors.RESET}")
                    print(f"{Colors.WHITE}{'=' * 60}{Colors.RESET}")

                    for run in runs:
                        status = run.get("status", "unknown")
                        conclusion = run.get("conclusion", "unknown")
                        branch = run.get("headBranch", "unknown")
                        workflow = run.get("workflowName", "unknown")
                        created = run.get("createdAt", "unknown")
                        run_id = run.get("databaseId", "unknown")

                        # Color code based on status
                        if conclusion == "success":
                            status_color = Colors.GREEN
                        elif conclusion == "failure":
                            status_color = Colors.RED
                        elif status == "in_progress":
                            status_color = Colors.YELLOW
                        else:
                            status_color = Colors.BLUE

                        print(f"{status_color}[{run_id}] {workflow} ({branch})")
                        print(f"  Status: {status} | Conclusion: {conclusion}")
                        print(f"  Created: {created}{Colors.RESET}")
                        print()

                time.sleep(interval)

        except KeyboardInterrupt:
            self.log_info("Stopped watching CI runs")

    def show_status(self) -> None:
        """Show current CI status."""
        self.log_info("Current CI Status")
        print("=" * 50)

        # Check authentication
        if self.check_gh_auth():
            self.log_success("✓ GitHub CLI authenticated")
        else:
            self.log_warning("✗ GitHub CLI not authenticated")
            print("  Run: gh auth login")
            return

        # Get recent runs
        runs = self.get_recent_runs(limit=5)
        if not runs:
            self.log_warning("No CI runs found")
            return

        print("\nRecent runs:")
        for i, run in enumerate(runs, 1):
            status = run.get("status", "unknown")
            conclusion = run.get("conclusion", "unknown")
            branch = run.get("headBranch", "unknown")
            workflow = run.get("workflowName", "unknown")
            run_id = run.get("databaseId", "unknown")

            if conclusion == "success":
                status_icon = "✓"
                color = Colors.GREEN
            elif conclusion == "failure":
                status_icon = "✗"
                color = Colors.RED
            elif status == "in_progress":
                status_icon = "⏳"
                color = Colors.YELLOW
            else:
                status_icon = "?"
                color = Colors.BLUE

            print(
                f"{color}{i}. {status_icon} [{run_id}] {workflow} ({branch}) - {conclusion}{Colors.RESET}"
            )

        # Check for recent failures
        recent_failures = [run for run in runs if run.get("conclusion") == "failure"]
        if recent_failures:
            print(f"\n{Colors.RED}Recent failures detected!{Colors.RESET}")
            print("Use 'python scripts/monitor-ci.py analyze <run-id>' to debug")


def main() -> None:
    """Main function to handle command line arguments."""
    monitor = CIMonitor()

    if len(sys.argv) < 2:
        print("Usage: python scripts/monitor-ci.py <command> [args]")
        print("\nCommands:")
        print("  status              - Show current CI status")
        print("  watch [interval]    - Watch CI runs in real-time")
        print("  analyze <run-id>    - Analyze a specific CI run")
        print("  logs <run-id> <job> - Get logs for a specific job")
        print("  auth                - Check GitHub CLI authentication")
        return

    command = sys.argv[1]

    if command == "status":
        monitor.show_status()

    elif command == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor.watch_runs(interval)

    elif command == "analyze":
        if len(sys.argv) < 3:
            monitor.log_error("Please provide a run ID")
            return
        run_id = sys.argv[2]
        monitor.analyze_failure(run_id)

    elif command == "logs":
        if len(sys.argv) < 4:
            monitor.log_error("Please provide run ID and job name")
            return
        run_id = sys.argv[2]
        job_name = sys.argv[3]
        logs = monitor.get_job_logs(run_id, job_name)
        if logs:
            print(logs)

    elif command == "auth":
        if monitor.check_gh_auth():
            monitor.log_success("GitHub CLI is authenticated")
        else:
            monitor.log_warning("GitHub CLI not authenticated")
            print("Run: gh auth login")

    else:
        monitor.log_error(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
