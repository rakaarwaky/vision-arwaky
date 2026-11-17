# DESIGN — CLI

> Output contract for the process surface. Renderers and CI consume the
> outcome vocabulary below to decide how to present a run and whether it passed.
> Condition: [ROADMAP.md](../../ROADMAP.md) (workspace) +
> [BACKLOG.md](BACKLOG.md).

## Design Overview

The CLI surface writes text to the terminal, so it has no palette. What it owns is the **outcome vocabulary** a caller branches on — the exit code and the JSON output envelope. The parser splits argv into a command namespace, the command handler resolves the domain container, and the output formatter renders the `CommandOutput` as JSON for the terminal.

## Design Requirements

### DS-CLIC-001: Outcome Vocabulary

| Variant | Use case | Token | Value |
|---------|----------|-------|-------|
| Success | Command completed without error | `exit_code` | `0` |
| Controlled error | Command failed with a structured error | `exit_code` | `1` |
| Parser error | Invalid arguments or unknown command | `exit_code` | `2` |

### DS-CLIC-002: Path Semantics

| Variant | Use case | Token | Value |
|---------|----------|-------|-------|
| Workspace init | Optional target directory | `target_dir` | `.` (current directory) |
| Image commands | Required image path | `--image` | user-supplied |
| Video commands | Required video path | `--video` | user-supplied |
| OCR language | Optional language code | `--lang` | `eng` |

### DS-CLIC-003: Output Shapes

| Variant | Use case | Token | Value |
|---------|----------|-------|-------|
| JSON envelope | All command results | `CommandOutput` | JSON string |
| Error object | Controlled failures | `error` key | message + context |
| Help text | Usage and command list | stdout | plain text |

### DS-CLIC-004: Report

| Variant | Use case | Token | Value |
|---------|----------|-------|-------|
| JSON output | Machine-readable results | `--json` flag | structured JSON |
| Human output | Terminal display | default | formatted text |

## Reference

| Artifact | Purpose | Link |
|----------|---------|------|
| BACKLOG.md | Backlog tracking | [BACKLOG.md](BACKLOG.md) |
| PRD.md | Product requirements | [PRD.md](../../PRD.md) |
| ROADMAP.md | Roadmap status | [ROADMAP.md](../../ROADMAP.md) |
| ARCHITECTURE.md | Layer contract | [ARCHITECTURE.md](../../ARCHITECTURE.md) |