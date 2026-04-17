"""n8n-transpiler: convert n8n workflow JSON to standalone Python."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("n8n-transpiler")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
