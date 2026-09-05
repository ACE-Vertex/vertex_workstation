# Vertex Workstation — Foundation 000001H1

## Exact failure

Foundation 000001 static verification passed.

Build then failed in TypeScript parsing:

- `src/buildIdentity.ts(1,32): error TS1127: Invalid character`
- repeated invalid-character / comma errors on line 1

The npm install itself completed successfully and reported 0 vulnerabilities.

## Root cause

The 000001 Python build generator was itself embedded in a raw Python string.
It wrote the literal two characters `\n` into `src/buildIdentity.ts` instead
of actual line-feed characters.

The resulting TypeScript file therefore became one malformed line containing
literal backslash characters.

## H1 fix

Replace only:

`scripts/build_workstation_foundation_000001.py`

with a corrected build generator that writes `src/buildIdentity.ts` as UTF-8
bytes containing real LF newlines.

The hotfix also fails closed if a literal `\n` byte sequence remains.

## Scope

No React component architecture change.
No CSS change.
No Ownership Contract change.
No Presentation Port change.
No Layout Grid change.
No Vertex Works change.

After successful build, runtime visual acceptance remains mandatory.
