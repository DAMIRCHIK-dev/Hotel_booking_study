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
