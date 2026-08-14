# AES Rules for Vision Arwaky

See [ARCHITECTURE.md](ARCHITECTURE.md) for the layer model and [lint_arwaky.config.yaml](lint_arwaky.config.yaml) for the machine-readable configuration used by the repository self-lint.

These rules describe the Python implementation under `modules/`. The linter configuration is authoritative when a future implementation detail changes.

## Rule summary

| Code | Name | Severity | Meaning |
|---|---|---|---|
| AES101 | Naming convention | High | Layer files use the configured prefix, concern, and role suffix. |
| AES102 | Suffix policy | High | Layer prefixes use only permitted suffixes. |
| AES201 | Forbidden import | Critical | Imports must respect the one-way AES dependency graph. |
| AES202 | Mandatory import | High | Required layer imports must be present when configured. |
| AES203 | Unused import | Medium | Imported symbols must be used in real file logic. |
| AES204 | Dummy import or bypass | High | Dummy functions, fake imports, and surface logic bypasses are forbidden. |
| AES205 | Circular import | Critical | Layer dependencies must not form a cycle. |
| AES301 | File maximum | High | A source file must remain below the configured line limit. |
| AES302 | File minimum | High | A non-exempt source file must contain meaningful content. |
| AES303 | Mandatory definition | High/Medium | Required implementation files must contain a real definition. |
| AES304 | Bypass comment | Critical | Suppression and unfinished-implementation patterns are forbidden. |
| AES305 | Duplication | Medium | Repeated code should be extracted into a shared utility or capability. |
| AES401 | Taxonomy role | High | Taxonomy modules must contain domain data and valid value-object usage. |
| AES402 | Contract role | High | Contract signatures must use taxonomy types and stable interfaces. |
| AES403 | Capabilities role | High/Medium | Capabilities must implement protocols without becoming orchestration hubs. |
| AES404 | Utility role | Medium | Utilities must remain stateless and technical. |
| AES405 | Agent role | Medium/High | Agents must orchestrate through ports and remain constructor-injected. |
| AES406 | Surface role | High | Surfaces must parse and delegate rather than contain domain workflows. |
| AES501–AES506 | Orphan checks | Low–High | Declared layers must be reachable through the composition graph. |

## 1. Naming rules

Python filenames follow this form:

```text
<prefix>_<concern>_<role>.py
```

The configured layer prefixes are `taxonomy_`, `contract_`, `utility_`, `capabilities_`, `agent_`, `surface_`, and `root_`. Standard examples are:

```text
contract_image_processing_protocol.py
capabilities_opencv_image_adapter.py
agent_video_orchestrator.py
surface_mcp_action.py
root_video_container.py
```

The standard role policies are:

| Prefix | Permitted role |
|---|---|
| `taxonomy_` | `vo`, `entity`, `error`, `event`, `constant` |
| `contract_` | `protocol`, `aggregate` |
| `agent_` | `orchestrator` |
| `root_` | `entry`, `container` |
| `capabilities_` | Configured capability role names; do not use taxonomy or contract suffixes |
| `utility_` | Configured technical role names; do not use taxonomy or contract suffixes |
| `surface_` | `command`, `controller`, `page`, `router`, `hook`, `store`, `action`, `screen`, `entry`, `component`, `view`, `layout` |

Package `__init__.py` files and the root entry modules are explicit exceptions.

## 2. Layer boundaries

The permitted direction is:

```text
taxonomy → contract / utility → capabilities → agent → surface → root
```

A layer may depend on the layers listed below it in the dependency graph, but it must not create a back-edge.

| Layer | Allowed dependencies | Forbidden examples |
|---|---|---|
| Taxonomy | Taxonomy | Contracts, utilities, capabilities, agents, surfaces, root |
| Utility | Taxonomy and standard library | Contracts, capabilities, agents, surfaces, root |
| Contract protocol | Taxonomy and contract types | Capabilities, agents, surfaces, root |
| Contract aggregate | Taxonomy and contract types | Capabilities, agents, surfaces, root |
| Capabilities | Taxonomy, contract protocols, utility | Agents, surfaces, root |
| Agent | Taxonomy, contracts, utility | Capabilities, surfaces, root |
| Smart surface | Taxonomy, aggregate contracts, approved utility | Capabilities, agent, protocol contracts, root |
| Root | All layers | Business logic and UI parsing |

## 3. Taxonomy rules

Taxonomy is the domain vocabulary. Value objects validate values at boundaries and are passed into contracts instead of allowing unchecked primitive values to spread through the graph.

Taxonomy modules must not perform I/O, call external tools, construct adapters, or coordinate feature workflows. Constant modules contain module-level constants only.

## 4. Contract rules

Contracts define stable behavior. Protocols describe capability ports, while aggregate contracts provide a surface-facing facade for feature execution.

`RegistryServiceAggregate` is a pure facade. Implementations must not reintroduce singleton access, `importlib` service discovery, static factories, or direct capability exposure. Concrete implementations are wired in the root composition container.

## 5. Utility rules

Utilities are stateless technical helpers. They may normalize paths, handle configuration, resolve system tools, or safely bridge execution contexts. They must not make domain decisions, own feature state, or implement a contract.

If a helper needs persistent state or a feature-specific policy, it belongs in a capability or agent rather than in a utility module.

## 6. Capabilities rules

Capabilities implement concrete behavior behind contract protocols. They may adapt OpenCV, FFmpeg, Tesseract, native VLMs, or external VLM endpoints.

Capabilities must not import surfaces, agents, or root. They must not become orchestration containers or define duplicate domain models. Shared technical mechanics belong in utilities.

## 7. Agent rules

Agents coordinate multiple capabilities through constructor-injected ports. The current feature orchestrators are `ImageOrchestrator` and `VideoOrchestrator`.

Agents must not import concrete capability modules, create static factories, discover services dynamically, or contain the composition root. Their logic is limited to sequencing, branching, translation, error handling, and coordination.

## 8. Surface rules

Surfaces are interaction boundaries. They parse CLI/MCP/TUI input, construct validated values when needed, delegate through the aggregate facade, and format output.

A surface must not call capability implementations directly, perform domain calculations, or reimplement orchestration. The MCP surface currently exposes `vision_execute`, `vision_list_commands`, `vision_help`, `vision_status`, and `vision_cancel`.

## 9. Root rules

Root modules assemble concrete implementations and inject them into contracts, agents, and surfaces. They may instantiate adapters and create containers, but they must not contain feature business logic or user-interface parsing.

The main composition modules are:

- `modules/root_composition_container.py`
- `modules/image/src/root_image_container.py`
- `modules/video/src/root_video_container.py`
- `modules/opencv/src/root_opencv_container.py`
- `modules/root_cli_entry.py`
- `modules/root_mcp_entry.py`
- `modules/root_tui_entry.py`

## 10. Quality and bypass rules

The self-lint rejects unfinished or suppressive patterns, including `TODO`, `FIXME`, `HACK`, `XXX`, broad `type: ignore`, dummy mandatory-import functions, and surface calls that bypass the aggregate boundary. Use explicit types and real error handling instead.

Keep files within the configured size limit, avoid duplicate blocks, and ensure every declared protocol, capability, agent, and surface is wired into the reachable application graph.

## 11. Verification commands

Run the repository's local gate script before opening a PR:

```bash
bash scripts/gates.sh
```

The equivalent individual checks are:

```bash
uv run ruff format --check modules/ tests/
uv run ruff check modules/ tests/
uv run mypy modules/
uv run python3 -m pytest tests/ -q
uv build
lint-arwaky-cli scan .
```

A valid change should finish with zero self-lint violations and a passing test suite. Update related documentation whenever a layer, entry point, command, or dependency rule changes.
