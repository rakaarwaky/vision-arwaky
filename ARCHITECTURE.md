# Vision Arwaky AES Architecture

## 1. Purpose

Vision Arwaky follows a seven-layer **Agentic Engineering System (AES)** architecture. The design keeps domain concepts stable, exposes behavior through contracts, isolates technical adapters, and makes the complete dependency graph explicit at the application root.

The repository is a Python package. The architecture documents the conventions implemented under `modules/`; examples below use the current Python paths and filenames.

## 2. Repository organization

```text
vision-arwaky/
├── modules/
│   ├── root_cli_entry.py
│   ├── root_mcp_entry.py
│   ├── root_tui_entry.py
│   ├── root_composition_container.py
│   ├── shared/
│   │   ├── __init__.py
│   │   └── src/
│   │       ├── contract_*_protocol.py
│   │       ├── contract_*_aggregate.py
│   │       ├── taxonomy_*_vo.py
│   │       ├── taxonomy_*_error.py
│   │       ├── taxonomy_*_constant.py
│   │       └── utility_*.py
│   ├── image/
│   │   └── src/
│   │       ├── capabilities_*.py
│   │       ├── agent_image_orchestrator.py
│   │       └── root_image_container.py
│   ├── video/
│   │   └── src/
│   │       ├── capabilities_*.py
│   │       ├── agent_video_orchestrator.py
│   │       └── root_video_container.py
│   ├── opencv/
│   │   └── src/
│   │       ├── capabilities_*.py
│   │       └── root_opencv_container.py
│   ├── cli/
│   │   └── src/
│   │       ├── surface_cli_command.py
│   │       ├── surface_cli_controller.py
│   │       └── surface_tui_component.py
│   └── mcp/
│       └── src/
│           ├── surface_mcp_action.py
│           └── surface_mcp_controller.py
├── tests/
├── scripts/gates.sh
├── pyproject.toml
└── config.yaml
```

The project uses **vertical feature slices** for image, video, OpenCV, CLI, and MCP concerns. Layer identity is encoded in the filename prefix rather than represented by top-level `taxonomy/`, `contract/`, or `capabilities/` directories.

## 3. Layer model

| Layer | Filename prefix | Responsibility | May depend on |
|---|---|---|---|
| Taxonomy | `taxonomy_` | Value objects, entities, errors, events, and constants | Nothing outside taxonomy |
| Contract | `contract_` | Protocols and aggregate facades | Taxonomy and contracts |
| Utility | `utility_` | Stateless technical helpers | Taxonomy |
| Capabilities | `capabilities_` | Concrete processing and infrastructure adapters | Taxonomy, contract protocols, utility |
| Agent | `agent_` | Feature orchestration through injected ports | Taxonomy, contracts, utility |
| Surface | `surface_` | User-facing CLI, MCP, and TUI interaction | Taxonomy, aggregate contracts, utility where allowed |
| Root | `root_` | Composition containers and entry-point bootstrapping | All layers |

The intended dependency direction is bottom-up:

```text
taxonomy ──► contract protocols ──► capabilities ──► agent ──► surfaces ──► root
     └──────► utility ────────────────────────────────────────────────┘
```

An arrow means that the layer on the right may use the layer on the left. Root is the composition boundary and is the only layer allowed to assemble concrete implementations across the graph.

## 4. Naming conventions

Python source files use the following form:

```text
<prefix>_<concern>_<role>.py
```

Examples from the current codebase include:

```text
contract_image_processing_protocol.py
contract_registry_service_aggregate.py
capabilities_opencv_image_adapter.py
agent_video_orchestrator.py
surface_mcp_action.py
root_video_container.py
```

The standard suffix rules are:

| Prefix | Required suffix or convention |
|---|---|
| `taxonomy_` | `_vo`, `_entity`, `_error`, `_event`, or `_constant` |
| `contract_` | `_protocol` or `_aggregate` |
| `agent_` | `_orchestrator` |
| `root_` | `_entry` or `_container` |
| `capabilities_`, `utility_`, `surface_` | A descriptive role that matches the configured AES rules |

Package `__init__.py` files and the root entry modules are documented exceptions to the ordinary three-part filename rule.

## 5. Taxonomy layer

Taxonomy defines the stable language of the application. It contains data concepts and domain errors, not infrastructure or orchestration.

Typical examples are `BackendType`, `ModelName`, `AnalysisPrompt`, `BoundingBox`, `FilePath`, and `CommandName` in `modules/shared/src/taxonomy_vision_models_vo.py`.

Taxonomy rules are:

1. Value objects validate and carry domain values.
2. Taxonomy does not import capabilities, agents, surfaces, or root modules.
3. Domain types should be used at boundaries instead of passing unvalidated primitives through the system.
4. Constants remain module-level constants and do not contain application behavior.

## 6. Contract layer

Contracts expose stable interfaces without revealing implementations. The repository uses Python protocols for capability ports and an aggregate facade for surface-to-agent access.

Examples include:

- `contract_image_processing_protocol.py` for image and OCR operations.
- `contract_ffmpeg_video_protocol.py` and related video protocols for media operations.
- `contract_registry_service_aggregate.py` for the surface-facing aggregate facade.

`RegistryServiceAggregate` is a pure contract facade. It does not use a singleton, dynamic import discovery, or a static service factory. Concrete wiring belongs in the root composition container.

## 7. Utility layer

Utilities contain stateless, reusable mechanics. They may normalize paths, execute safe technical helpers, handle configuration, or bridge synchronous and asynchronous execution. They must not define business workflows or implement contracts.

Current examples include `utility_async_runner.py`, `utility_config_handler.py`, and `utility_system_utils.py`.

## 8. Capabilities layer

Capabilities implement concrete operations behind contract protocols. They include image processing, OCR, OpenCV analysis, FFmpeg integration, object tracking, and video analysis.

Capabilities must not import surfaces, agents, or root. When several capabilities need shared technical mechanics, extract that mechanic into a utility rather than creating a capability-to-capability dependency.

## 9. Agent layer

Agents coordinate capabilities through injected contract ports. The current feature orchestrators are:

- `ImageOrchestrator` in `modules/image/src/agent_image_orchestrator.py`.
- `VideoOrchestrator` in `modules/video/src/agent_video_orchestrator.py`.

Agents use constructor injection. They do not import concrete capabilities, create static service factories, or own the composition graph. Their responsibility is sequencing, branching, error handling, and translating capability results into command output.

## 10. Surface layer

Surfaces translate external interaction into aggregate calls. The CLI, MCP, and TUI surfaces should parse input, build taxonomy value objects where appropriate, delegate through the injected aggregate, and present results.

The smart surfaces are command and controller modules. They may use taxonomy, aggregate contracts, and approved utilities. Surfaces must not construct capabilities, import capability implementations directly, or contain domain orchestration.

The MCP surface registers the five public tools `vision_execute`, `vision_list_commands`, `vision_help`, `vision_status`, and `vision_cancel`. The CLI surface exposes the image, video, and test commands documented in [README.md](README.md).

## 11. Root layer and composition

The root layer owns application assembly. `root_composition_container.py` builds the shared graph and returns the `RootDispatcher`; feature containers build the image, video, and OpenCV subgraphs.

The entry points perform only bootstrap work:

```python
from modules.root_composition_container import build


def main() -> None:
    dispatcher = build()
    # Inject the dispatcher into the selected surface.
```

Root may instantiate adapters and connect protocols to implementations. It must not contain domain decisions, user-interface parsing, or feature-specific business logic.

## 12. Verification

Run the same checks locally that the repository's CI workflow runs:

```bash
bash scripts/gates.sh
```

The gates are:

| Gate | Command or behavior |
|---|---|
| Format | `uv run ruff format --check modules/ tests/` |
| Lint | `uv run ruff check modules/ tests/` |
| Type checking | `uv run mypy modules/` |
| Tests | `uv run python3 -m pytest tests/ -q` |
| Package build | `uv build` |
| Architecture self-lint | `lint-arwaky-cli scan .` with zero violations |

CI runs the test matrix on Python 3.12 and 3.13 and installs the system packages required by OpenCV, Tesseract, and FFmpeg.

## 13. Change checklist

Before adding or moving a module, confirm that:

1. The filename uses the correct layer prefix and role suffix.
2. Imports point only toward permitted lower layers.
3. Capability implementations satisfy a contract protocol.
4. Agents receive their ports through constructors.
5. Surfaces delegate through an aggregate rather than concrete services.
6. The root container owns concrete wiring.
7. `bash scripts/gates.sh` passes with zero self-lint violations.
8. Related documentation and command examples match the current entry points.
