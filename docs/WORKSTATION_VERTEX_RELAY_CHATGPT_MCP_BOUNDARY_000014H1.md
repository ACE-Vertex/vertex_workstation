# Vertex Workstation — 000014H1

## Cause

The 000014 verifier loaded `relay_mcp_core.py` with `importlib.util.module_from_spec`
and immediately called `spec.loader.exec_module(module)`.

`RelayRecord` is a `@dataclass` and the module uses postponed annotations.
On the user's Python/Anaconda runtime, `dataclasses` resolves annotation types
through `sys.modules[cls.__module__]`.

Because the dynamically created module had not been registered in `sys.modules`,
dataclass processing failed with:

`AttributeError: 'NoneType' object has no attribute '__dict__'`

## Fix

Before `exec_module`, register the module:

`sys.modules[spec.name] = module`

No Relay Core logic changes.
No MCP protocol changes.
No storage changes.
No FORGE/RAY changes.
No Workstation UI changes.
