# n8n-transpiler — Implementation Plan

**Overall Progress:** `0%`

## Context

Greenfield Python project at `/Users/colesnipes/Documents/GitHub/n8n-transpiler/` (currently empty except `README.md` + `.git/`). The tool — CLI command **`n8n2py`**, PyPI package **`n8n-transpiler`** — converts n8n workflow JSON exports into standalone, human-readable Python scripts. Two primary journeys: (1) **prototyping accelerator** — eject visual workflows to Python for hand-editing; (2) **audit / review** — produce diffable Python for code review and compliance. Both demand idiomatic output over mechanical fidelity. Output has zero n8n runtime dependency.

## Decisions (confirmed)

1. **Use cases**: prototyping accelerator + audit/review
2. **Output layout**: flat single-file by default; `--layout=package` flag for large workflows
3. **Input sources**: JSON file (primary) + stdin + `pull` from n8n REST API
4. **Data model**: flatten to `dict` when possible, fall back to `list[dict]` when aggregation/iteration demands it
5. **Expressions**: ship a Python-only subset translator; use `py-mini-racer` JS oracle in tests only
6. **MVP nodes (12)**: Set, If, Switch, Merge, Code, NoOp, Stop And Error, Wait, HTTP Request, Webhook trigger, Schedule trigger, Manual trigger
7. **Unsupported nodes**: hard-fail by default; `--allow-stubs` emits `NotImplementedError` stubs
8. **Triggers**: pure function + reference `run.py` (FastAPI for webhook, loop for schedule, one-shot for manual)
9. **Credentials**: env-var default + optional `credentials: dict` override; types None / Basic / Header / API Key / Bearer
10. **`continueOnFail`**: ignored in v1 — always fail fast
11. **Code node**: body run through expression translator; non-translatable parts become prominent TODO markers
12. **Naming**: PyPI `n8n-transpiler`, CLI `n8n2py`
13. **Stack**: Python 3.11+, `uv`, `typer`, `pydantic` v2, stdlib `ast`, `httpx`, `python-dotenv`, optional `fastapi`+`uvicorn`, test-only `py-mini-racer`

## Tasks

- [ ] 🟥 **Phase 1: Project scaffold**
  - [ ] 🟥 Initialize `uv` project, write `pyproject.toml` (Python 3.11+, dev/test extras)
  - [ ] 🟥 Create `src/n8n_transpiler/` package skeleton with empty modules: `parse.py`, `ir.py`, `expr.py`, `codegen/__init__.py`, `runner.py`, `cli.py`
  - [ ] 🟥 Add `typer` CLI entry point with `compile`, `pull`, `validate` no-op stubs
  - [ ] 🟥 Configure `ruff` (lint + format), `pytest`, basic `tests/` layout
  - [ ] 🟥 Wire console script `n8n2py = n8n_transpiler.cli:app` in `pyproject.toml`
  - [ ] 🟥 Add CI-friendly `make test` / `make lint` targets (Makefile)

- [ ] 🟥 **Phase 2: IR + parser (no codegen yet)**
  - [ ] 🟥 Define pydantic v2 models in `ir.py`: `Workflow`, `Node` (with `id`, `name`, `kind: NodeKind`, `parameters`, `credentials`, `position`), `Connection`, `NodeKind` (StrEnum of MVP types + `UNSUPPORTED`)
  - [ ] 🟥 Implement `parse.load_workflow(source)` accepting `Path | str | TextIO` (stdin via `-`)
  - [ ] 🟥 Implement `parse.workflow_to_ir(spec)` mapping raw n8n JSON to `Workflow` IR; sanitize node names to valid Python identifiers (with collision handling)
  - [ ] 🟥 Implement `validate` CLI command — parse + IR build, print compile-readiness report (supported nodes, unsupported nodes, expression count, mode hints)
  - [ ] 🟥 Add fixture n8n JSONs in `tests/fixtures/` (one per supported node) collected from real exports
  - [ ] 🟥 Unit tests for parser + IR construction across all fixtures

- [ ] 🟥 **Phase 3: Minimal codegen — HTTP Request + Set + Manual trigger**
  - [ ] 🟥 Implement `codegen/_walker.py` — IR walker producing `ast.Module`; topological sort over connections
  - [ ] 🟥 Implement `codegen/nodes/manual.py` — emits `def workflow(trigger_data, credentials)` skeleton
  - [ ] 🟥 Implement `codegen/nodes/set.py` — emits dict-update statements for Set/Edit Fields
  - [ ] 🟥 Implement `codegen/nodes/http_request.py` (no auth yet) — emits `httpx.Client().request(...)` call returning `response.json()`
  - [ ] 🟥 Implement data-mode inference: per-node `single | list` mode determined by topology + node kind
  - [ ] 🟥 Implement `codegen/emit.py` — `ast.unparse()` + optional shell-out to `ruff format` for final formatting
  - [ ] 🟥 Wire `compile` CLI command (flat layout only at this point)
  - [ ] 🟥 Golden snapshot tests via `syrupy` for the minimal node set

- [ ] 🟥 **Phase 4: Conditionals — If, Switch, Merge**
  - [ ] 🟥 `codegen/nodes/if_.py` — emits `if/else` against translated condition expression
  - [ ] 🟥 `codegen/nodes/switch.py` — emits `match` statement (Python 3.11+) over routing expression
  - [ ] 🟥 `codegen/nodes/merge.py` — emits list-mode collection, triggers list-mode propagation downstream
  - [ ] 🟥 Update mode-inference: post-`If`/`Switch` joins → list mode unless single-branch reachable
  - [ ] 🟥 Golden snapshot tests for conditionals

- [ ] 🟥 **Phase 5: Expression translator + JS oracle test infrastructure**
  - [ ] 🟥 Define expression IR in `expr/ir.py`: `PathAccess`, `NodeRef`, `Literal`, `BinaryOp`, `UnaryOp`, `Call`, `Conditional`, `Unsupported`
  - [ ] 🟥 Handwritten recursive-descent parser in `expr/parser.py` for the documented subset
  - [ ] 🟥 Implement `expr/translate.py` — expression IR → Python `ast.expr`
  - [ ] 🟥 Implement TODO marker rendering for `Unsupported` (preserves original JS as a comment, raises at runtime if reached)
  - [ ] 🟥 Add `py-mini-racer` to test extras only
  - [ ] 🟥 Build oracle test harness `tests/oracle/test_expressions.py` — for each (expression, sample-input) tuple, run JS via mini-racer + Python via translator, assert equivalence
  - [ ] 🟥 Refactor `Set`/`If`/`Switch`/`HTTP Request` codegen to use translator for any expression-bearing parameter

- [ ] 🟥 **Phase 6: Webhook + Schedule triggers + reference runner**
  - [ ] 🟥 `codegen/nodes/webhook.py` — emits parameter destructuring from `trigger_data` matching configured webhook fields
  - [ ] 🟥 `codegen/nodes/schedule.py` — records interval/cron in IR, no inline emission
  - [ ] 🟥 `runner.py` — emits `run.py` tailored to trigger kind:
    - Manual/Schedule → `python run.py` (one-shot), `python run.py --loop` (interval loop)
    - Webhook → minimal `fastapi` app on configured path/method
  - [ ] 🟥 Emit `crontab.example` for Schedule triggers
  - [ ] 🟥 Mark `fastapi` + `uvicorn` as optional extras in generated `requirements.txt`
  - [ ] 🟥 E2E test: transpile a webhook fixture, start the runner, POST to it, assert response

- [ ] 🟥 **Phase 7: Credentials (5 types)**
  - [ ] 🟥 Map n8n credential types to Python: None, HTTP Basic, HTTP Header Auth, API Key (header/query), Bearer Token
  - [ ] 🟥 Generate `_load_credentials_from_env()` helper that reads `os.environ` keyed by sanitized credential name
  - [ ] 🟥 Make generated `workflow()` signature accept optional `credentials: dict | None = None`; fall back to env loader when omitted
  - [ ] 🟥 Emit `.env.example` listing every required env var with empty values + comment showing credential type/source node
  - [ ] 🟥 Update `HTTP Request` codegen to wire credentials into `httpx` calls
  - [ ] 🟥 E2E test against `httpbin.org/basic-auth/...` and `httpbin.org/bearer`

- [ ] 🟥 **Phase 8: Remaining MVP nodes — Code, NoOp, Stop And Error, Wait**
  - [ ] 🟥 `codegen/nodes/code.py` — feed Code-node body through expression translator; emit function that runs translatable bits + a `raise RuntimeError("untranslated TODO ...")` for any `Unsupported` segment
  - [ ] 🟥 `codegen/nodes/noop.py` — pass-through identity
  - [ ] 🟥 `codegen/nodes/stop_and_error.py` — `raise RuntimeError(translated_message)`
  - [ ] 🟥 `codegen/nodes/wait.py` — `time.sleep(seconds)` for fixed delays; emit ISO-time wait helper for date-target waits
  - [ ] 🟥 Golden + e2e tests

- [ ] 🟥 **Phase 9: `--layout=package`, `pull` subcommand, stdin input**
  - [ ] 🟥 Implement `codegen/layout.py` switching between `flat` and `package` writers; package mode emits `workflow/__init__.py`, `workflow/_orchestrator.py`, `workflow/nodes/*.py`
  - [ ] 🟥 Implement `pull` CLI command — `httpx` request to `<base-url>/api/v1/workflows/<id>` with `X-N8N-API-KEY` header, write JSON to disk
  - [ ] 🟥 Wire stdin input (`-` argument) through `parse.load_workflow`
  - [ ] 🟥 `--allow-stubs` flag wiring: replace unsupported-node hard-fail with stub emission
  - [ ] 🟥 Hard-fail error messages: list every unsupported node by `name` + `type` + n8n type identifier
  - [ ] 🟥 Tests for layout switching, pull (mocked via `respx`), stdin path

- [ ] 🟥 **Phase 10: Polish + release prep**
  - [ ] 🟥 Run `ruff format` over all generated outputs (configurable on/off)
  - [ ] 🟥 Comprehensive `README.md`: install, quickstart, supported nodes table, expression subset reference, troubleshooting
  - [ ] 🟥 `docs/` folder: `unsupported-nodes.md`, `expression-subset.md`, `architecture.md`
  - [ ] 🟥 `--version` flag, `--help` text review
  - [ ] 🟥 Verify exit codes: 0 success, 1 bad input, 2 unsupported nodes, 3 TODO markers present
  - [ ] 🟥 Tag `v0.1.0`, document publish workflow (do not auto-publish)

## Important Implementation Details

- **Pipeline boundary**: keep parse / IR / expression-translate / codegen as four independent passes. The IR is the contract. Adding a new node = one IR shape + one emitter; no parser changes.
- **Identifier sanitization**: n8n node names are arbitrary strings; map to `snake_case` Python identifiers, suffix with `_N` on collision. Original name preserved as a comment header on the emitted function.
- **Topological order**: codegen walks nodes in topological order over connections. Cycles (rare in n8n) → hard-fail with clear error.
- **Mode inference algorithm**: simple two-pass. Pass 1: assign initial mode per trigger. Pass 2: propagate downstream — `Merge`, post-branch joins, and any node consuming a list-mode output → list mode. Otherwise single mode.
- **Expression subset**: handwritten recursive-descent parser (no `pyjsparser` dependency). Subset is small enough that hand-rolling is cleaner and gives precise control over what falls into `Unsupported`.
- **TODO markers** must be impossible to ignore at runtime — emit a `raise RuntimeError("TODO: manual translation required for expression: ...")` rather than a silent comment.
- **JS oracle** lives only in `tests/oracle/`; never imported from `src/`. Generated code has zero JS dependency.
- **`ast.unparse` style**: pass output through `ruff format` shell-out for consistent style; gate behind `--no-format` flag for environments without `ruff`.
- **Credential env-var naming**: `<CREDENTIAL_TYPE>_<SANITIZED_NAME>_<FIELD>` (e.g., `HTTP_BASIC_AUTH_MY_API_USER`, `..._PASSWORD`) — documented in `.env.example` with source-node comments.
- **Hard-fail clarity**: every fatal compile error names the offending node (`name` + `type`) and points to docs.

## File-level Changes (key insertion points)

- **Add**
  - `pyproject.toml` — package metadata, deps, console script, ruff/pytest config
  - `Makefile` — `test`, `lint`, `format`, `install` targets
  - `src/n8n_transpiler/__init__.py` — exports `compile_workflow` for library use
  - `src/n8n_transpiler/cli.py` — `typer` app, subcommands `compile` / `pull` / `validate`
  - `src/n8n_transpiler/parse.py` — JSON loading (file/stdin/api), n8n shape → IR mapping
  - `src/n8n_transpiler/ir.py` — pydantic models: `Workflow`, `Node`, `Connection`, `NodeKind`
  - `src/n8n_transpiler/expr/__init__.py` — re-exports
  - `src/n8n_transpiler/expr/ir.py` — expression IR
  - `src/n8n_transpiler/expr/parser.py` — recursive-descent parser for subset
  - `src/n8n_transpiler/expr/translate.py` — expression IR → `ast.expr`
  - `src/n8n_transpiler/codegen/__init__.py` — entry: `compile_workflow(ir, layout) -> dict[str, str]`
  - `src/n8n_transpiler/codegen/_walker.py` — topo sort + per-node dispatch
  - `src/n8n_transpiler/codegen/_mode.py` — single/list mode inference
  - `src/n8n_transpiler/codegen/emit.py` — `ast.unparse` + optional ruff formatting
  - `src/n8n_transpiler/codegen/layout.py` — flat vs. package writers
  - `src/n8n_transpiler/codegen/nodes/{manual,webhook,schedule,set,if_,switch,merge,code,noop,stop_and_error,wait,http_request}.py` — one emitter per supported node
  - `src/n8n_transpiler/runner.py` — `run.py` + `crontab.example` generators
  - `src/n8n_transpiler/credentials.py` — credential type → env-var naming + httpx wiring helpers
  - `tests/fixtures/<node>.json` — one minimal n8n export per supported node + a few realistic combinations
  - `tests/golden/` — `syrupy` snapshots
  - `tests/oracle/test_expressions.py` — JS-vs-Python equivalence harness
  - `tests/e2e/test_http.py` — `respx` + `httpbin.org` smoke tests
  - `docs/{unsupported-nodes,expression-subset,architecture}.md`

- **Modify**
  - `README.md` — replace stub with full quickstart, supported-nodes table, expression subset reference, examples

- **Keep** (unchanged)
  - `.git/` — repository metadata

## Verification Plan

End-to-end smoke test (run by hand after Phase 8):

1. Build a small real n8n workflow combining: Manual trigger → HTTP Request (`https://httpbin.org/json`) → Set (extract a field) → If (check value) → HTTP Request (POST to `https://httpbin.org/post`).
2. Export it from n8n as JSON.
3. `n8n2py compile workflow.json -o ./out`
4. `cd out && python -m venv .venv && .venv/bin/pip install -r requirements.txt`
5. `.venv/bin/python run.py` — assert it completes successfully and the printed final state matches expectations.
6. `git diff` the generated `workflow.py` against a hand-written reference — verify it reads cleanly enough that a human reviewer would accept it.

After Phase 6: repeat for a Webhook fixture, hitting `run.py`'s FastAPI server with `curl`. After Phase 7: repeat with credentialed HTTP requests against `httpbin.org/basic-auth/...`.

Automated coverage continuously verified by: per-node unit tests, oracle equivalence tests for expressions, golden snapshots for codegen stability, and `respx`-mocked e2e tests.

## Progress Calculations

- Total phases: 10
- Completed: 0
- Overall Progress: `0%`
