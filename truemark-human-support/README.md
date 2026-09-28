# True Mark Human Support Escalation

This is a retained UI/service boundary for governed human escalation. It is not an automated assistant and it does not answer customer questions with an inference engine.

## Behavior

- Hidden by default.
- Opened only after an authorized escalation case exists.
- Shows a clearly identified human-operated channel.
- Sends customer messages to a scoped case.
- Never receives unrestricted Sanctum access, encryption keys, unrelated projects, or private notes.

## Service endpoints

- `POST /api/escalations` creates a scoped case.
- `GET /api/escalations/{case_id}` returns case status without message history.
- `POST /api/escalations/{case_id}/messages` queues a message for a human agent.
- `POST /api/escalations/{case_id}/close` closes a case.

The old prototype knowledge graph and automated response modules are retained only as historical files and are not imported by the escalation service.
