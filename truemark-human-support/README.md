# True Mark Human Support Escalation

This is a retained UI boundary for governed human escalation. It is not an automated assistant and it does not answer customer questions with an inference engine.

The production API is integrated into the main True Mark backend at `http://localhost:13001/api/escalations`. The companion FastAPI file is only a deprecated adapter and deliberately does not create, retrieve, message, or close cases.

## Behavior

- Hidden by default.
- Opened only after an authorized escalation case exists.
- Shows a clearly identified human-operated channel.
- Sends customer messages to a scoped case.
- Never receives unrestricted Sanctum access, encryption keys, unrelated projects, or private notes.

## Service endpoints

- `POST /api/escalations` creates a scoped case through the main backend.
- `GET /api/escalations/{case_id}` returns the authenticated owner's case status.
- `POST /api/escalations/{case_id}/messages` queues a message for a human agent.
- `POST /api/escalations/{case_id}/close` closes an owner's case or an admin-managed case.
- `POST /api/escalations/{case_id}/assign` assigns an authenticated admin's case to an agent.

The old prototype knowledge graph and automated response modules are retained only as historical files and are not imported by the escalation service.
