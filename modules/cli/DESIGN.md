# DESIGN — CLI

## Brand & Style

### Colors

| Role | Value | Use |
|------|-------|-----|
| Base surface | terminal default | The pane background. |
| Primary accent | cyan | Active selection and command names. |
| Secondary accent | gray | Inactive rows and help text. |
| Tertiary accent | yellow | A warning the user must act on. |

### Typography

| Level | Weight | Use |
|-------|--------|-----|
| Section | bold | Pane and command-group titles. |
| Body | normal | Command rows and parameters. |
| Muted | dim | Path hints and defaults. |

## Components

### Command surface

| Part | Role |
|------|------|
| Parser | Splits argv into domain, command, and options. |
| Handler | Binds command names to `execute_in_process` calls. |
| Output formatter | Renders the JSON `CommandOutput` for the terminal. |

### TUI pane

| Part | Role |
|------|------|
| Title row | Names the active surface mode. |
| Body | Lists the rows the pane owns. |
| Status row | Reports counts and errors. |

### Row

| Part | Role |
|------|------|
| Label | The command name. |
| Detail | The parameters and defaults. |

## Reference

- PRD.md — what the product does and why
- ARCHITECTURE.md — the layer contract this design follows
- FRD.md — the requirements the interface serves