# P03 design notes

## Why design before code

Low-level design decides which classes exist, what data each one keeps and what
methods it has, and which class calls which, before writing code.

## Where the methods live

- `Cancel()` lives in `Reservation` because cancelling changes the reservation's own status.
- `HasOverlap()` lives in `ReservationStore` because only the store can see all reservations.

## Activity traces

1. **Omar, R7, 13–15 Nov** (Maya has 12–14):
   Check-out after check-in? **Yes**. A Confirmed booking shares a night? **Yes**, the 13th.
   Ends at "Unavailable · save nothing".
2. **Nora, R7, 14–16 Nov**:
   Check-out after check-in? **Yes**. A Confirmed booking shares a night? **No** (no shared night).
   Saved, email sent, ends at "Accepted + reservation id" (R102).
3. **Omar, R8, 15–15 Nov**:
   Check-out after check-in? **No**.
   Ends at "InvalidDates · save nothing".

## Prediction

Nora R7 14-16 Nov: Accepted R102, because her first night (14th) is Maya's check-out day.

## The race

Prediction: R7 will get 2 Confirmed reservations.

Both requests ran `HasOverlap` before either one called `Save`, so both saw an empty
store and both were accepted. The problem is between the `store.has_overlap(...)` check
and `store.save(...)` in `reserve()`: a check-then-act race condition.

# P04 design notes

## Refactoring

Refactoring changes how the code is organised internally while keeping its external behaviour completely unchanged.

Must stay the same:

- All 6 tests from Step 2 still pass after every move.
- The demo output prints the exact same nine lines as in P03.
- The race demo still prints `Double booking!`: refactoring does not fix bugs.

## What our code breaks

- `BookingService` asks for concrete `ReservationStore` (D: dependency inversion).
  In P07 we would have to edit `BookingService` just to switch to PostgreSQL.
- `BookingService` asks for concrete `EmailSender` (D and O: dependency inversion and open/closed).
  Adding SMS confirmations or testing a failing mail server would force us to edit `BookingService`, and keeping all nine classes in one file breaks single responsibility (S).

## Proof

- Tests: 6 of 6 Step 2 tests passed after refactoring, and 8 of 8 tests pass after adding R6 and SMS (`Ran 8 tests ... OK`).
- Demo: prints the exact same nine lines as P03.
- Race: still double-booked (`Confirmed reservations for R7 on 12-14 Nov: 2` / `Double booking!`).

# P06 design notes

## Before

- Tests: 8 passing (`Ran 8 tests ... OK`).
- Demo: prints the nine expected lines.
- Race: still double-booked (`Double booking! Both requests checked before either one saved.`).

## Modules

| Module | Public contract (others may use) | Internal code (only the module, the wiring and the tests) |
|---|---|---|
| Rooms | `Room`, `RoomCatalog` | `InMemoryRoomCatalog` |
| Reservations | `BookingService`, `BookingResult`, `Reservation`, `DateRange`, `Guest`, `ReservationStatus`, `ReservationStore` | `InMemoryReservationStore` |
| Payments | `PaymentStatus`, `PaymentService` | `SimulatedPaymentService` |
| Notifications | `Confirmation`, `NotificationSender` | `EmailNotificationSender`, `SmsNotificationSender` |

## Architecture rules

1. **Reservations uses only the public contracts of other modules**: `BookingService` may use the `Notifications` and `Rooms` public contracts, never their `internal` modules (such as `EmailNotificationSender`).
2. **Rooms does not depend on any other module**: `Rooms` knows nothing about reservations, payments, or notifications.
3. **Payments and Notifications do not depend on Reservations**: dependency arrows point one way, from `Reservations` outwards, preventing cycles.

## Broken on purpose

Rule `"Reservations uses only the public contracts of other modules"` failed (`Contracts: 2 kept, 1 broken.`), naming `hotel_booking.reservations.booking -> hotel_booking.notifications.internal (l.8)`.

## After

- Tests: 8 passing (`Ran 8 tests ... OK`) plus 3 kept `import-linter` contracts (`Contracts: 3 kept, 0 broken.`) = 11 green checks.
- Demo: prints the exact same nine lines as before.
- Race: still double-booked (`Double booking! Both requests checked before either one saved.`).

# P07 design notes

## API decisions

1. **Cursor pagination order**: Free rooms are returned in lexicographical (text) order of `room.number` (`R10` comes before `R7`), and the `after` cursor filters by text comparison (`room.number > after`).
2. **Error comparison key**: Clients compare `title` (`Unavailable`, `InvalidDates`, `UnknownRoom`, `InvalidRequest`, `NotFound`) in RFC 9457 `application/problem+json` responses; `detail` is human-readable prose and may change.
3. **Room type extensibility**: `Room.type` is catalog data loaded from the `rooms` table (`Standard`, `Deluxe`, etc.), not a fixed enum in the OpenAPI contract, so adding a new room type requires no API schema break.

## API tests

- `GET /rooms/availability?checkIn=2026-11-12&checkOut=2026-11-14` → `200` with `R7` (`Standard`), `R8` (`Deluxe`), and `"next":null`.
- `POST /reservations` (Maya R7 12–14 Nov) then `POST /reservations` (Omar R7 13–15 Nov) → `201` (`{"id":"R101","status":"Confirmed","notificationFailed":false}`), then `409` (`Unavailable`).
- `POST /reservations` with `checkIn == checkOut` (`2026-11-15` to `2026-11-15`) → `400` (`InvalidDates`, `application/problem+json`).
- `DELETE /reservations/R101` twice → `204`, then `404` (`NotFound`).

## After

- Checks: 15 green checks (`12` unittest tests = `8` service + `4` API, plus `3` kept `import-linter` contracts).
- Seven answers: all 7 requests in `docs/api-check.md` return the exact expected status codes and JSON bodies.
- Restart check: `R102` (`Confirmed`) and `R101` (`Cancelled`) persist in PostgreSQL across app restarts (`R7` remains booked, only `R8` is free).

# P08 design notes

## Cache rule

Booking (`POST /reservations`) and cancelling (`DELETE /reservations/{id}`) never read the cache: PostgreSQL is the sole source of truth, and Redis only holds disposable copies of search answers.

## After

- Checks: 17 green checks (`14` unittest tests = `8` service + `6` API, plus `3` kept `import-linter` contracts).
- Two measurements (`tools/measure.py`, 1,000 searches): without cache `2,000` DB queries (`2.5 ms` avg, `3.5 ms` p95); with cache-aside (`TTL 30 s`) `2` DB queries and `999` cache hits (`0.9 ms` avg, `1.2 ms` p95).
- Stale result and fix: before invalidation, a search within 30 s of Maya booking `R7` returned a stale `R7, R8` list (though Omar's clash still got `409 Unavailable` from PostgreSQL); raising `availability:version` after accepted `POST` and `204` `DELETE` makes the next search immediately return only `R8`.
