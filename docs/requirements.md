# Requirements: hotel booking app, version 1

Rooms: R7 (Standard), R8 (Deluxe). Dates are half-open: a booking 12–14 November
covers the nights of the 12th and 13th; the check-out day is not a night.

## R1 · Search

A guest or receptionist can list the rooms that are free for given dates.

Check: empty hotel, 12–14 November → R7, R8.

Proof: `Free rooms 12-14 Nov: R7, R8`

## R2 · Book

A guest or receptionist can book a free room. The app answers with a reservation id.

Check: Maya books R7 for 12–14 November → Accepted R101.

Proof: `Maya books R7 12-14 Nov: Accepted R101`

## R3 · No clash

A room never has two Confirmed bookings on the same night. Check-out must be after check-in.

Check: Omar asks for R7 on 13–15 → Unavailable. 15–15 → InvalidDates.

Proof: `Omar books R7 13-15 Nov: Unavailable`

More examples:

- Maya R7 12–14 → Confirmed (already booked)
- Omar R7 13–15 → Unavailable (night of the 13th)
- Nora R7 14–16 → Accepted (no shared night)
- R8 22–24 → Accepted (R8 is booked 20–22; no shared night)
- R8 21–23 → Unavailable (R8 is booked 20–22; night of the 21st)

## R4 · Cancel

A booking can be cancelled. It is kept as Cancelled and no longer blocks the room.

Check: Maya cancels R101 → R7 is free again for 12–14.

Proof: `Maya cancels R101: True`, then `Free rooms 12-14 Nov: R7, R8`

## R5 · View

A booking can be looked up by its id.

Check: R101 → Maya, R7, 12–14 November, Confirmed.

Proof: `View R101: Maya, R7, 12-14 Nov, Confirmed`
