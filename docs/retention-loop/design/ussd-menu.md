# The kernel: USSD menu state machine

The one module you write entirely by hand. It lives in
`ussd-gateway/src/main/java/io/github/lakwan194/telco/ussd/menu/`, and
`KernelIsolationTest` keeps it free of Spring, Redis and reactive code, so it is
pure logic you can test exhaustively and draw from memory. Read
[domain/telco-apis.md](../domain/telco-apis.md) first.

Status: **not started** (week 2). Decision it depends on: ADR-002.

## Screens

| Screen | Text shown (fits one USSD screen) | Valid inputs | Next screen per input |
| --- | --- | --- | --- |
| | | | |

## Diagram

```mermaid
stateDiagram-v2
    %% Draw every screen and transition, including the ones that end the session.
```

## Rules to decide

<!-- Invalid input: repeat the screen with an error, or end? How many retries?
     "0" for back, "00" for home? What ends a session (mt-fin)?
     What the subscriber sees when a slow action is deferred to SMS. -->

## The kernel's API

<!-- What goes in (current state, input) and what comes out (next state, screen text,
     continue or end, side effects to request). Keep side effects out of the kernel:
     it returns a description of what should happen, and the caller does it. -->

## Tests

- Every screen is reachable from the start.
- Every input on every screen leads somewhere defined (no gaps in the table).
- Every path can end; nothing loops forever.
- No screen's text exceeds the length one USSD screen can show (check the limit).
- Invalid input never crashes; it follows your rule above.

## Done when

- [ ] Every row of the screens table has a test
- [ ] You can draw the diagram and walk through the code on a whiteboard, without notes
