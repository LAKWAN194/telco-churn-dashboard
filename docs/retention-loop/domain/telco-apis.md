# Telco APIs: USSD, SMS and carrier billing

The gateway in `ussd-gateway/` simulates an operator platform, so its API should
look like a real one. These notes summarise **Ideamart**, the developer platform
run by hSenid Mobile on Sri Lankan networks, from the API reference hSenid
publishes on GitHub ([references.md](../references.md)). Read the originals before
designing; the details below are a summary taken on 16 October 2026.

## USSD: short sessions, keypress by keypress

The subscriber dials a code (for example `*141#`). The platform opens a session
and **POSTs each keypress to your callback URL**. You do not reply with the next
screen in that HTTP response. You send it in a **separate** `POST /ussd/send`
call, and the callback only acknowledges receipt.

| `ussdOperation` | Set by | Meaning |
| --- | --- | --- |
| `mo-init` | Platform | The subscriber dialled your code: a session starts |
| `mo-cont` | Platform | The subscriber replied within the session |
| `mt-init` | Your app | Your app starts a session (often not permitted) |
| `mt-cont` | Your app | The next screen; keep the session open |
| `mt-fin` | Your app | The final screen; **ends the session** |

A normal exchange:

```
subscriber dials *141#
  → platform POSTs your callback:   mo-init, sessionId = S, message = "*141#"
  → you POST /ussd/send:            mt-cont, sessionId = S, message = "1. Balance\n2. Bundles"
subscriber presses 2
  → platform POSTs your callback:   mo-cont, sessionId = S, message = "2"
  → you POST /ussd/send:            mt-fin,  sessionId = S, message = "..."
```

Facts that shape the design:

- **Echo the `sessionId` you were given.** The platform owns it.
- **Sessions are short** (tens of seconds) and **you must reply fast.** Anything
  slow (charging, a model call) is deferred, and the result goes out by SMS.
- **Session state lives on your side**, keyed by `sessionId`, with a time-to-live.
  The platform sends the keypress, not the path that led to it.
- Addresses look like `tel:94771234567` and may be masked (hashed).
- Results carry `statusCode` and `statusDetail` (`S1000` is success). Check those,
  not just the HTTP status.

## SMS

| Service | Direction | Where |
| --- | --- | --- |
| Send (MT, mobile-terminated) | App → subscriber | `POST /sms/send` |
| Receive (MO, mobile-originated) | Subscriber → app | Your MO callback URL |
| Delivery report | Platform → app | Your delivery-report callback URL |

`destinationAddresses` is an array, and a request to several numbers can partly
succeed, so per-recipient results come back separately. Over-length messages are
split by the platform.

## Charging as a service (carrier billing)

A **direct debit** (`POST /caas/direct/debit`) reduces a prepaid balance or adds to
a postpaid bill. hSenid's reference states five rules, summarised:

1. The amount is agreed and shown to the subscriber **before** they accept.
2. **`externalTrxId` is the idempotency key.** Create it once, store it before the
   call, and reuse it on every retry of the same charge.
3. **Never retry with a fresh `externalTrxId`:** a timeout does not mean the charge
   failed. Retry with the same ID, or reconcile.
4. Never charge on the strength of an unauthenticated request (a USSD keypress
   alone is not authorisation).
5. Every charge is traceable: who, what, when, how much, which ID, and what the
   subscriber saw before agreeing.

These are the same ideas as the payment switch project (idempotency keys, safe
retries, reconciliation), applied to a telco.

## One-time passwords

Ideamart offers OTP and subscription services too. For this project an OTP is an
SMS code the self-care app asks for at login. The design questions (length,
lifetime, attempts, lock-out, and rate limits per number and per IP) are ADR-004.
Store a hash of the code, never the code itself.

## How the simulator uses this

The gateway plays **both** sides in one service, in separate packages:

- `platform`: the operator. It opens sessions when a "phone" dials, calls the
  menu's callback, and delivers screens back to the phone.
- `menu`: your app's side, where the **kernel** (the menu state machine) lives.

Whether they stay in one service is ADR-001. Keep the message shapes close to
Ideamart's, so the menu could be pointed at the real platform with little change.
