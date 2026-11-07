# Hotel contexts

## Words

| Word | Meaning here | Name in our code |
|---|---|---|
| Stay | Check-in to check-out, half-open: 12–14 Nov = the nights of the 12th and 13th | `DateRange` |
| Reservation | Guest + room + stay + status, with an id such as R101 | `Reservation` |
| Confirmed | The room is promised to this guest for these nights | `ReservationStatus.CONFIRMED` |
| Guest | The person staying in or booking a room, identified by name and email (e.g. Maya) | `Guest` |
| Room | A physical room the hotel sells, such as R7 or R8 | `Room` |
| Room type | Category of a room, such as Standard or Deluxe | `Room.type` |
| Nightly price | How much one night in a given room type costs | not in code yet |
| Out of service | A room temporarily taken off sale (for example, R8 closed for repairs) | not in code yet |
| Cancelled | The promise is withdrawn; the reservation is kept and the nights are free again | `ReservationStatus.CANCELLED` |
| Book | Ask to reserve a free room for a stay and receive an id such as R101 | `BookingService.reserve` |
| Cancel | Mark an existing reservation as Cancelled so it stops blocking its room | `BookingService.cancel` |
| Free rooms | Rooms that have no Confirmed reservation sharing a night with the requested stay | `BookingService.find_free_rooms` |
| Deposit | 30% of the stay's price, taken when the guest books | not in code yet |
| Paid | The guest's deposit payment succeeded | not in code yet |
| Declined | The guest's deposit payment was refused by the card provider | not in code yet |
| Confirmation message | Email or SMS sent to tell the guest that a reservation was Confirmed | `NotificationSender.send_confirmation` |
| Sent | The confirmation email or SMS was delivered to the provider | not in code yet |
| Failed | Sending the confirmation email or SMS failed | not in code yet |

## Rooms

Job: knows which rooms the hotel sells.

| Word | Meaning here |
|---|---|
| Room | A sellable hotel room with its number, type, nightly price and availability state |
| Room type | Standard or Deluxe category determining room features and price |
| Nightly price | Price charged per night for this room type |
| Out of service | Room is closed for repairs or maintenance and cannot be sold |

Rules this context owns:
- A room that is out of service is not offered to guests.
- The nightly price depends on the room type (Deluxe costs more than Standard).

Needs from other contexts: nothing.
Tells other contexts: answers which rooms exist and their types (to Reservations) and nightly prices (to Payments, later).

## Reservations

Job: decides whether a guest gets a room for some nights, and keeps every reservation.

| Word | Meaning here |
|---|---|
| Stay | Check-in to check-out, half-open: 12–14 Nov = the nights of the 12th and 13th |
| Reservation | Guest + room number + stay + status, with an id such as R101 |
| Confirmed | The room is promised to this guest for these nights |
| Cancelled | The promise is withdrawn; the nights are free again |
| Guest | Name and email recorded on a reservation |
| Book | Check dates and overlap, save a Confirmed reservation, and return its id |
| Cancel | Withdraw a Confirmed reservation without deleting its record |
| Free rooms | Rooms from the catalog that have no Confirmed overlap on the requested stay |

Rules this context owns:
- A room never has two Confirmed reservations that share a night.
- Check-out must be after check-in.
- Cancelling a reservation frees its nights for new bookings.

Needs from other contexts: the list of rooms (Rooms), and deposit collection from P17 (Payments).
Tells other contexts: ReservationConfirmed (Notifications).

## Payments

Job: takes deposits and records whether they were paid.

| Word | Meaning here |
|---|---|
| Deposit | 30% of the stay's price, charged against a reservation id |
| Paid | Deposit charge succeeded and can later be refunded if needed |
| Declined | Deposit charge was rejected; no money was captured |

Rules this context owns:
- The deposit is 30% of the stay's price.
- Only a Paid deposit can be refunded.

Needs from other contexts: nightly room price when computing stay totals (Rooms, later).
Tells other contexts: answers Paid or Declined when asked to take a deposit (to Reservations, from P17).

## Notifications

Job: tells guests what happened, by email or SMS.

| Word | Meaning here |
|---|---|
| Confirmation message | Outbound email or SMS telling the guest their booking details |
| Sent | Provider accepted the message for delivery |
| Failed | Provider could not send the message; recorded for retry/reporting |

Rules this context owns:
- A failed message is recorded as Failed and never changes the reservation.

Needs from other contexts: nothing (it only receives the `ReservationConfirmed` event fields).
Tells other contexts: nothing.

## Same word, different meaning

| Word | Rooms | Reservations | Payments | Notifications |
|---|---|---|---|---|
| Status | In service / out of service | Confirmed / Cancelled | Paid / Declined | Sent / Failed |
| Room | R8: Deluxe, nightly price, out of service | Just the room number R8 on a reservation | Not used | Plain text in the message: "Room R8" |
| Cancel | Take a room off sale | Withdraw a reservation so its nights are free | Refund a Paid deposit | Not used |

If Notifications shared a single status field with Reservations and changed it to `Failed` when an email or SMS bounced, Maya would lose her `Confirmed` booking on R7 because of a mail failure, breaking rule R6.

## Rule owners

| Card | Rule | Owner | Why this owner |
|---|---|---|---|
| 1 | A room never has two Confirmed reservations that share a night. | Reservations | It keeps every reservation of the room, so it can check them all together. |
| 2 | Check-out must be after check-in. | Reservations | It owns the `Stay` (`DateRange`) value and validates dates before saving a reservation. |
| 3 | Cancelling a reservation frees its nights for new bookings. | Reservations | It owns reservation status (`Confirmed` / `Cancelled`) and overlap checks. |
| 4 | A room that is out of service is not offered to guests. | Rooms | Only Rooms keeps each room's in-service / out-of-service catalog state. |
| 5 | The nightly price depends on the room type (Deluxe costs more than Standard). | Rooms | Rooms owns room types and the catalog's nightly pricing table. |
| 6 | The deposit is 30% of the stay's price. | Payments | Money rules belong to Payments; it asks Rooms for the nightly price. |
| 7 | Only a Paid deposit can be refunded. | Payments | Payments alone records each deposit's payment status (`Paid` vs `Declined`). |
| 8 | A failed message is recorded as Failed and never changes the reservation. | Notifications | Notifications owns delivery status (`Sent` / `Failed`) and cannot touch Reservations' data (R6). |

## Between contexts

### Reservations → Notifications: ReservationConfirmed (event)

Sent when: a reservation is saved as Confirmed.

Fields:
- `reservationId`: R101
- `guestEmail`: maya@example.com
- `roomNumber`: R7
- `checkIn`: 2026-11-12
- `checkOut`: 2026-11-14

Reservations does not wait for an answer. A failed message never changes R101 (rule R6).

Never crosses: Reservations' list of reservations or the `Reservation` domain object. Notifications never reads it.

### Reservations → Rooms: which rooms exist? (question)

Sent when: Reservations checks which rooms the hotel sells (for free-room search or booking).

What Reservations sends: no parameters (`all()`).

The answer and its fields: a list of rooms, each carrying:
- `number`: R7, R8
- `type`: Standard, Deluxe

Never crosses: Rooms' internal catalog table or maintenance records; Reservations never modifies room data.

### Reservations → Payments: take a deposit (question, from P17)

Sent when: the booking saga (from P17) asks Payments to charge the guest's deposit for a reservation.

What Reservations sends:
- `reservationId`: R101
- `amount`: decimal deposit amount (e.g. `45.00`)

The answer and its fields:
- `status`: `Paid` or `Declined`

Never crosses: card details, payment provider credentials, or Payments' internal ledger rows.

