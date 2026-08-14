---
name: setup-ci-quality-gates
description: Maintain the Python CI quality gates, AES self-lint, review integrations, and gated auto-merge workflow used by Vision Arwaky.
metadata:
  tags: [ci, github-actions, quality-gates, code-review, coderabbit, codacy, cubic, repowise, python, self-lint, architecture, aes]
  triggers:
    - "setup ci"
    - "quality gates"
    - "ci pipeline"
    - "code review bot"
    - "architecture enforcement"
    - "self-lint"
---

# CI Quality Gates for Vision Arwaky

The repository uses GitHub Actions to enforce formatting, linting, type checking, package building, tests, and AES self-lint. The workflow is defined in `.github/workflows/test.yml`; the local equivalent is `scripts/gates.sh`.

## CI jobs

| Job | Command or behavior | Purpose |
|---|---|---|
| Format | `uv run ruff format --check modules/ tests/` | Ensure stable Python formatting |
| Lint | `uv run ruff check modules/ tests/` and `uv run mypy modules/` | Catch style, correctness, and typing problems |
| Build | `uv build` | Verify the package can be built |
| Tests | pytest on Python 3.12 and 3.13 | Verify runtime behavior with OpenCV, Tesseract, and FFmpeg |
| Self-lint | `lint-arwaky-cli scan .` with `Total: 0` | Enforce AES architecture and quality rules |

The test jobs install `libgl1`, `tesseract-ocr`, and `ffmpeg`, generate media fixtures, and run `tests/`. The self-lint job downloads the repository's pre-built linter binary and treats a nonzero violation count as a failure.

## Local verification

From the repository root:

```bash
uv sync
sudo apt-get update
sudo apt-get install -y libgl1 tesseract-ocr ffmpeg
uv pip install ruff mypy pytest
bash scripts/gates.sh
uv build
```

The gate script runs the same format, lint, Mypy, pytest, and self-lint checks used by CI. The package build is a separate CI gate and should be run before a release or packaging change.

## AES self-lint

The self-lint command is:

```bash
lint-arwaky-cli scan .
```

The authoritative result is `Total: 0`. Do not replace this with the removed `lint-arwaky-cli check`, `lint-arwaky-cli ci`, or `lint-arwaky-cli external` commands.

When a violation appears, inspect the layer prefix and dependency direction first. The current AES direction is:

```text
taxonomy → contract / utility → capabilities → agent → surface → root
```

The repository's rules are documented in [RULES_AES.md](../../../RULES_AES.md), and the machine-readable configuration is [lint_arwaky.config.yaml](../../../lint_arwaky.config.yaml).

## Auto-merge workflow

`.github/workflows/auto-merge.yml` enables squash auto-merge for a non-draft PR targeting `main`. The workflow passes the repository explicitly because the runner does not check out the repository before invoking the GitHub CLI:

```yaml
- name: Enable auto-merge (squash)
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    PR_NUMBER: ${{ github.event.pull_request.number }}
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: |
    gh pr merge "$PR_NUMBER" \
      --repo "$GITHUB_REPOSITORY" \
      --auto --squash \
      --subject "$PR_TITLE"
```

Use environment variables for PR metadata. Do not interpolate a title directly into shell source. The workflow must not silently ignore a failed merge request.

## Review integrations

Codacy, CodeRabbit, cubic, and Repowise are external review integrations. Their check names and availability depend on repository configuration. Treat the repository's CI jobs as the source of truth for formatting, linting, build, tests, and self-lint; use external review output to address introduced findings without weakening the code gates.

If Codacy flags a subprocess call, prefer an in-process API or an explicit, validated command boundary. If Repowise reports dead files or stale documentation, compare the finding with the current package entry points and update the documentation or configuration rather than suppressing the signal.

## Change checklist

Before opening a PR:

- Run `bash scripts/gates.sh`.
- Run `uv build` for packaging or dependency changes.
- Confirm that the self-lint count is zero.
- Update `README.md`, `ARCHITECTURE.md`, `RULES_AES.md`, `SKILL.md`, or `MIGRATION_PYTHON.md` when commands, paths, entry points, or layer rules change.
- Review `.github/workflows/test.yml` and `.github/workflows/auto-merge.yml` when CI behavior changes.
- Never use a suppression comment to hide a new architecture or typing issue.
