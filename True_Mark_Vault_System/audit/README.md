# Vault audit stream

`events.jsonl` is the append-only local audit stream for authoritative Vault mutations.

Each event contains:

- the event identity, subject, actor, and event payload;
- a complete ISS timestamp envelope, including `iss_time_ns`, Epoch, Standard, Julian, and ISS displays;
- `previous_event_hash` and `event_hash` for sequential tamper evidence.

ISS supplies the canonical time. The Vault owns the event record and remains the authority for what was committed, sealed, or otherwise recorded. Display timestamps never replace `iss_time_ns`.

The stream is created on the first audited mutation at:

```text
True_Mark_Vault_System/audit/events.jsonl
```
