# Vertex Workstation — 000015H2

## Evidence diagnosis

000015H1 reached the real runtime bootstrap and failed while installing the
official Python MCP SDK.

Observed:

- `ModuleNotFoundError: No module named 'mcp'`
- `Could not find a version that satisfies the requirement mcp<2,>=1.22`
- `No matching distribution found`

The verification process itself is running through the machine's Anaconda
Python path elsewhere in Evidence. The official MCP Python SDK requires
Python 3.10 or newer.

The pip error can also be caused by a configured package index that does not
contain `mcp`.

## H2 fix

The MCP setup no longer trusts whatever executable the bare `python` command
resolves to.

It probes for compatible CPython 3.10+ runtimes, preferring:

- Python 3.12
- Python 3.11
- Python 3.13
- Python 3.10
- Python 3.14

It checks the Windows Python Launcher first, then named commands and standard
installation locations.

If the existing isolated Vertex MCP venv was created with an incompatible
Python, it is removed and rebuilt.

Dependency installation uses the venv Python and:

`pip --isolated --index-url https://pypi.org/simple`

so global Anaconda/user pip index configuration cannot silently redirect the
private Vertex MCP runtime.

## Safety

No system Python is modified.
No global package install.
Only:

`%LOCALAPPDATA%\VertexWorkstation\runtimes\relay_mcp_v1`

is rebuilt when necessary.

If no Python 3.10+ runtime exists, H2 fails explicitly with that diagnosis
instead of reporting a misleading MCP package failure.
