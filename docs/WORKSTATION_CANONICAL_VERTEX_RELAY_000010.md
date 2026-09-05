# Vertex Workstation — CANONICAL + Vertex Relay 000010

## Mission

Implement the next Workstation content foundation:

1. CANONICAL Registry page
2. shared Vertex Relay transport concept
3. Vertex Relay integration into Architecture Contract

## CANONICAL layout

Matches the established Workstation content layout:

- left: card list
- right: selected concept detail/editor

No floating windows.

## Card rules

Cards show:

- meaningful category icon when a semantic mapping exists
- formal English name
- abbreviation beside the formal name
- summary
- status / importance / optional flavor badge
- small delete control in the card lower-right area

No oversized action buttons.

## Detail fields

Right-side labels are Japanese by default:

- 正式名称
- 略称
- 状態
- 重要度
- 適用範囲
- カテゴリ
- 概要
- 機能
- 詳細説明
- 由来
- 別名
- 関連概念
- Flavor Badge
- 採用者
- 備考

Values remain Canonical semantic values such as ADOPTED or CRITICAL.

## Persistence

First pass uses localStorage:

`vertex.canonical.registry.v1`

This keeps the page useful immediately without introducing a new database
dependency.

## Vertex Relay

Shared core envelope:

`vertex-relay/1`

Supported domain types:

- CANONICAL
- ARCHITECTURE_CONTRACT

First transport:

- COPY RELAY -> clipboard
- RECEIVE -> paste relay JSON -> validate -> Human ACCEPT / REJECT

RECEIVE never auto-applies a relay without Human ACCEPT.

Hyper Agent / Vertex Core direct transport can replace the clipboard transport
later without changing the domain envelope.

## Architecture Contract integration

Architecture Contract now contains the same docked Vertex Relay lane.

A new Architecture Contract card named `Vertex Relay` documents the shared
policy.

## Scope

No FORGE runtime behavior changes.
No RAY runtime behavior changes.
No legacy vertex_works mutation.
No floating windows.

Runtime visual acceptance required.
