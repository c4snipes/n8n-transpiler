"""Smoke tests for the CLI scaffold."""

from __future__ import annotations

from typer.testing import CliRunner

from n8n_transpiler import __version__
from n8n_transpiler.cli import app

runner = CliRunner()


def test_version_flag_prints_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_help_lists_subcommands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    out = result.stdout
    assert "compile" in out
    assert "pull" in out
    assert "validate" in out


def test_compile_subcommand_is_wired_but_unimplemented() -> None:
    result = runner.invoke(app, ["compile", "nonexistent.json"])
    # Phase 1 stub returns exit code 1.
    assert result.exit_code == 1
    assert "not yet implemented" in (result.stderr or "")


def test_pull_subcommand_is_wired_but_unimplemented() -> None:
    result = runner.invoke(app, ["pull", "abc123", "--base-url", "https://x"])
    assert result.exit_code == 1


def test_validate_subcommand_is_wired_but_unimplemented() -> None:
    result = runner.invoke(app, ["validate", "nonexistent.json"])
    assert result.exit_code == 1
