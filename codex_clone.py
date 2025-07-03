import subprocess
import sys
import os
from typing import Optional

try:
    from autogen import AssistantAgent, UserProxyAgent
except ImportError:  # runtime dependency check
    raise SystemExit("Please install the 'autogen' package before running this script.")


def git_pull(repo_path: str) -> None:
    """Fetch the latest changes in the repository."""
    subprocess.run(["git", "pull"], cwd=repo_path, check=True)


def show_diff(repo_path: str, old_rev: str, new_rev: str) -> str:
    """Return a git diff between two revisions."""
    diff = subprocess.check_output([
        "git", "diff", f"{old_rev}..{new_rev}"
    ], cwd=repo_path, text=True)
    return diff


def create_pr_message(repo_path: str, branch_name: str) -> str:
    """Create a simple PR message using the latest commits."""
    log = subprocess.check_output([
        "git", "log", "-1", "--pretty=format:%B"
    ], cwd=repo_path, text=True)
    return f"PR from branch {branch_name}\n\n" + log


def run_agent_task(task: str, repo_path: str = ".") -> Optional[str]:
    """Run an AutoGen agent on the given task."""
    # Pull latest changes first
    git_pull(repo_path)
    
    # Create agents
    assistant = AssistantAgent("assistant")
    user = UserProxyAgent("user", code_execution_config={"work_dir": repo_path})

    user.initiate_chat(assistant, message=task)
    # After chat ends, return git diff from last commit if any
    try:
        current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path, text=True).strip()
        previous = subprocess.check_output(["git", "rev-parse", "HEAD~1"], cwd=repo_path, text=True).strip()
        return show_diff(repo_path, previous, current)
    except subprocess.CalledProcessError:
        return None


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY environment variable not set.")

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python codex_clone.py '<task description>'")

    task_description = sys.argv[1]
    diff = run_agent_task(task_description)
    if diff:
        print("\nDiff after task:\n")
        print(diff)
    else:
        print("No changes detected.")
