# P01 · Project Baseline: Booking Domain & Architectural Foundations

## 1. Diagnostic Starting Point

- **Programming example (`programming`)**: `check_capacity(concert_id) -> bool` checks whether confirmed reservations are fewer than total capacity. Classes such as `Reservation(id, customer, status)` bundle booking data with behavior such as `cancel()`.
- **SQL starting point (`sql`)**:
  ```sql
  SELECT id, concert_id, status
  FROM bookings
  WHERE customer_email = 'alex@example.com' AND status = 'Confirmed';
  ```
- **Computer starting point (`computer`)**: Unsaved working variables live in volatile process RAM; when the application process exits or crashes, all in-memory state disappears unless already flushed to durable storage.
- **Personal learning goal (`goal`)**: How can a booking service guarantee zero double-bookings when two customers submit overlapping requests for the last available place at the exact same millisecond?

---

## 2. People, Needs and First-Version Scope (`stakeholders`)

| Person / Role | Action | Required Result |
|---|---|---|
| **Customer (Alex, Emma)** | Checks availability, clicks *Book*, and checks *My bookings* | Receives an honest `Confirmed` reference (e.g., `B42`) or `Sold out`; can always re-read the saved result later. |
| **Organiser (Claire)** | Opens Friday's confirmed booking list | Sees an accurate saved list whose confirmed count never exceeds capacity (`20`). |
| **Support worker (Daniel)** | Looks up a customer's booking inquiry | Verifies from saved records whether a confirmed reservation exists and what reference it holds. |

**First-version scope**:
- **Included now**: View availability, request one booking, and look up saved booking status (`20` unnumbered places per concert, `1` ticket per customer).
- **Excluded from v1**: Online payment/deposits, self-service cancellations, numbered seating, and automated waiting lists.

---

## 3. Unresolved Policies (`questions`)

1. **Cancellation policy** *(Owner: Claire)*: If cancellations are added later, how close to the event may a customer cancel, and does a cancelled place return immediately to general availability?
2. **Waiting-list policy** *(Owner: Claire)*: When capacity reaches 20, should rejected customers be queued in order or simply check availability again later?
3. **Tickets per customer** *(Owner: Claire)*: Will future events allow group bookings (e.g., up to 4 tickets), or remain strictly 1 per customer?

---

## 4. Three Functional Needs (`needs`)

### F1 · Check Availability
- **Starting situation**: Friday's concert has capacity `20` and `19` confirmed bookings saved.
- **Action**: Alex opens Friday's concert availability screen.
- **Visible result**: Screen displays `1 ticket available` (`Book` enabled).
- **Saved-data change**: None (read-only query; confirmed count remains `19`).

### F2 · Book a Place
- **Starting situation**: Friday's concert has `19` confirmed bookings; Alex has no existing booking for Friday.
- **Action**: Alex clicks `Book`.
- **Visible result**: Screen displays `Confirmed · Reference B42`.
- **Saved-data change**: One new record (`B42`, `Alex`, `Friday`, `Confirmed`) is saved; confirmed count becomes `20`.

### F3 · Check Saved Status (*My Bookings*)
- **Starting situation**: `B42` is saved as `Confirmed`, even if Alex's mobile connection dropped before the booking response arrived.
- **Action**: Alex opens *My bookings*.
- **Visible result**: Screen lists `Friday Concert — B42 — Confirmed`.
- **Saved-data change**: None (re-opening *My bookings* creates no duplicate booking).

---

## 5. Invariant Booking Rules (`rules`)

1. **Capacity Rule (No Overselling)**: Confirmed bookings for a concert must never exceed its capacity (`20`).
   - *Sold-out worked example*: Start with `20` confirmed bookings for Friday (`capacity = 20`). Customer Emma clicks `Book`. Visible result: `Sold out`. Saved-data result: no new booking is saved, and the confirmed count stays at `20`.
2. **One-Booking-Per-Customer Rule (Idempotency)**: Each customer may hold at most one confirmed booking per concert. If Alex clicks `Book` twice because the network is slow, the second request returns his existing `Confirmed` reference (`B42`) without saving a second booking.

---

## 6. Three Checkable Quality Concerns (`quality`)

| Concern | Condition / Stimulus | Required Outcome | Proposed Check & Target |
|---|---|---|---|
| **Q1 · Data Integrity under Concurrency** | Alex and Emma submit overlapping `Book` requests when `19/20` places are taken. | Exactly one request is `Confirmed` (`20/20`) and the other receives `Sold out`. | Concurrent request test; target: `0` over-allocations (`count <= 20`). |
| **Q2 · Availability on Email Failure** | The external email provider stops responding while bookings are being made. | Valid bookings remain saved as `Confirmed` (`Booking confirmed. Email pending`); email delivery is retried separately. | Fault-injection test with failing sender; target: `0` lost confirmed bookings. |
| **Q3 · Accessibility & Recoverability** | A keyboard-only customer submits `Book`, or a customer loses network reply mid-request. | Customer can reach `Book` via keyboard, read the status announcement, and verify saved state in *My bookings* within *target: to agree (e.g., ≤ 2 s)*. | Keyboard navigation walkthrough + simulated dropped-response test. |

---

## 7. Context Sketch (`sketch`)

```text
[Customer (Alex/Emma)]
   │  1. Check availability / Book / View My bookings (HTTP)
   ▼
┌──────────────────────────────────────┐
│           Ticket / Booking App       │─── 3. Send confirmation ──► [Email Provider]
│  (Booking rules · Saved store · API) │◄── 4. Sent / Error ────────
└──────────────────────────────────────┘
   ▲                                ▲
   │ 2a. View confirmed list        │ 2b. Lookup booking reference
[Organiser (Claire)]         [Support Worker (Daniel)]
```

---

## 8. Five Business Terms (`glossary`)

| Term | Definition |
|---|---|
| **Concert** | A scheduled event with a fixed ticket capacity against which customers request bookings. |
| **Capacity** | The maximum number of `Confirmed` bookings allowed for one concert (`20` in v1). |
| **Confirmed booking** | A saved reservation record promising one place at a concert to one customer, identified by a booking reference (`B42`). |
| **Sold out** | The state where confirmed bookings equal capacity (`20`); new booking requests are refused and save nothing. |
| **Cancellation** | Withdrawing a previously confirmed booking so it no longer counts toward capacity *(excluded from v1; introduced in P03 R4 for hotel stays)*. |

---

## 9. Team Responsibilities & Tool-Access Checklist (`roles`, `tools`)

### Team Responsibilities
- **Author / Drafter**: Drafted scope, functional needs `F1–F3`, invariant rules, and context sketch.
- **Reviewer / Checker**: Verified consistency of *Confirmed* and *Sold out* across glossary, rules, and saved-data outcomes.

### Tool-Access Checklist
| Tool | Status | Owner | Next Action |
|---|---|---|---|
| Code Editor (PyCharm / VS Code) | Available | Damir | Ready for Python & Markdown editing |
| Git CLI | Available | Damir | Track incremental commits in `hotel-booking` |
| Python 3.10+ & `.venv` | Available | Damir | Used from P02 onward |
| Docker Desktop (PostgreSQL & Redis) | Available | Damir | Needed from P07 (`postgres:18`) and P08 (`redis:8`) |

---

## 10. Peer Feedback & Limits (`review`)

- **Before feedback**: *"When Friday is full, show Sold out."*
- **Peer feedback**: State explicitly whether anything is written to storage and what happens to the total confirmed count.
- **After feedback**: *"When Friday has 20 confirmed bookings, show `Sold out`, save no new booking, and keep the confirmed count at 20."*
- **Evidence label**: `Simulated` / `Proposed` — this baseline is a reviewed specification and paper trace, not yet an observed test on a running database.

---

## 11. Individual Reflection (`reflection`)

- **Contribution**: Drafted the capacity invariant, sold-out worked example, and email-failure quality concern, and verified that visible screen messages match saved-data rules.
- **Rule explained in own words**: Showing `Sold out` is only honest if the application also writes zero new records and keeps confirmed bookings at `20`; otherwise stored state violates the capacity invariant even if the UI hides it.
- **Current uncertainty**: How two overlapping threads/requests both reading `19` can be prevented from both writing `20` and `21`.
- **Next learning goal (for P02)**: Observe how the operating system runs a Python process, holds working memory in user space, and persists files across process termination.

