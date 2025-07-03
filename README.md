# chatdbt

This repository demonstrates a minimal "Codex" style workflow using [AutoGen](https://pypi.org/project/autogen/). The `codex_clone.py` script pulls the latest project version with Git, runs an agent on a user provided task, and shows the resulting diff so you can create a pull request.

## Setup

```bash
pip install -r requirements.txt
```

Set the `OPENAI_API_KEY` environment variable before running the script.

## Example

```bash
python codex_clone.py "create a new dbt model for analyzing the performance of campaigns"
```

When the agent finishes, the script prints the git diff between the last two commits. Push your changes and open a PR as desired.
