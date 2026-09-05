# Vertex Workstation — 000015H3

## Evidence result

H2 proved the earlier environment diagnosis.

The old isolated runtime was Python 3.9.13.

H2 selected:

`Python 3.14.4`

and rebuilt the isolated venv.

It then installed:

`mcp 1.29.1`

successfully from public PyPI.

The real MCP protocol verifier then reached:

- `MCP_INITIALIZE=PASS`
- `MCP_LIST_TOOLS=PASS`
- `MCP_STATUS_CALL=PASS`

So the MCP runtime and protocol path are already functioning.

## Exact remaining failure

After the successful protocol test, Python attempted to delete the temporary
SQLite database directory.

Windows returned:

`PermissionError: [WinError 32]`

for `relay.db`.

This is a shutdown/temporary-file cleanup race, not an MCP protocol failure.

## H3 fix

The runtime verifier now:

1. creates the temp directory explicitly with `mkdtemp`
2. stops the MCP server process tree on Windows using `taskkill /T /F`
3. waits for process termination
4. retries temporary directory deletion with backoff
5. if Windows still delays the SQLite handle release, records
   `MCP_TEMP_CLEANUP=DEFERRED_WINDOWS_LOCK`
   instead of converting a successful protocol test into a false MCP failure

The actual protocol gates remain mandatory.

A failed MCP initialize, tool list, or status call still fails verification.

## Scope

Verifier lifecycle only.

No MCP server protocol changes.
No Relay schema changes.
No SQLite production-store changes.
No Workstation UI changes.
No FORGE/RAY changes.
