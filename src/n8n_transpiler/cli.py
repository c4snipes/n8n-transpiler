"""Command-line entry point for `n8n2py`."""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path

import typer

from n8n_transpiler import __version__

app = typer.Typer(
    name="n8n2py",
    help="Convert n8n workflow JSON exports into standalone Python scripts.",
    no_args_is_help=True,
    add_completion=False,
)


class Layout(str, Enum):
    """Output layout for the generated workflow."""

    flat = "flat"
    package = "package"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"n8n2py {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: ARG001
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """n8n2py: transpile n8n workflows to Python."""


@app.command()
def compile(  # noqa: A001
    input: str = typer.Argument(  # noqa: A002
        ...,
        help="Path to an n8n workflow JSON file, or '-' to read from stdin.",
    ),
    out: Path = typer.Option(
        Path("./out"),
        "-o",
        "--out",
        help="Output directory for generated files.",
    ),
    layout: Layout = typer.Option(
        Layout.flat,
        "--layout",
        help="Output layout: flat (single file) or package (one module per node).",
    ),
    allow_stubs: bool = typer.Option(
        False,
        "--allow-stubs",
        help="Emit NotImplementedError stubs for unsupported nodes instead of failing.",
    ),
    no_runner: bool = typer.Option(
        False,
        "--no-runner",
        help="Do not emit run.py reference runner.",
    ),
    no_env_example: bool = typer.Option(
        False,
        "--no-env-example",
        help="Do not emit .env.example.",
    ),
    no_format: bool = typer.Option(
        False,
        "--no-format",
        help="Skip ruff formatting of generated output.",
    ),
) -> None:
    """Compile an n8n workflow JSON into Python."""
    typer.echo(
        f"compile: input={input} out={out} layout={layout.value} "
        f"allow_stubs={allow_stubs} no_runner={no_runner} "
        f"no_env_example={no_env_example} no_format={no_format}",
        err=True,
    )
    typer.echo("compile: not yet implemented (Phase 3)", err=True)
    raise typer.Exit(code=1)


@app.command()
def pull(
    workflow_id: str = typer.Argument(..., help="n8n workflow ID to fetch."),
    base_url: str = typer.Option(..., "--base-url", help="n8n instance base URL."),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="N8N_API_KEY",
        help="n8n API key (or set N8N_API_KEY).",
    ),
    out: Path = typer.Option(
        Path("workflow.json"),
        "-o",
        "--out",
        help="Output file for fetched workflow JSON.",
    ),
) -> None:
    """Fetch a workflow JSON from a running n8n instance."""
    typer.echo(
        f"pull: workflow_id={workflow_id} base_url={base_url} "
        f"api_key={'***' if api_key else None} out={out}",
        err=True,
    )
    typer.echo("pull: not yet implemented (Phase 9)", err=True)
    raise typer.Exit(code=1)


@app.command()
def validate(
    input: str = typer.Argument(  # noqa: A002
        ...,
        help="Path to an n8n workflow JSON file, or '-' to read from stdin.",
    ),
) -> None:
    """Parse a workflow and report compile-readiness without generating code."""
    typer.echo(f"validate: input={input}", err=True)
    typer.echo("validate: not yet implemented (Phase 2)", err=True)
    raise typer.Exit(code=1)


if __name__ == "__main__":
    sys.exit(app() or 0)
