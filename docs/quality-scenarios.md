# Quality scenarios

## Stakeholders

| Who | What they care about |
|---|---|
| Guest | Finds a free room quickly; never loses a booking |
| Receptionist | Never promises one room twice; can cancel at the desk |
| Hotel manager (domain expert) | Knows the rules; wants deposits and SMS soon |
| Development team | Can change one area without breaking the others |
| Email/SMS and payment providers | Outside systems that can be slow or down |

## S3 · Availability: a failed message keeps the booking

| Part | S3 |
|---|---|
| Source | The email provider |
| Stimulus | It stops answering |
| Environment | For 10 minutes, during normal bookings |
| Artifact | BookingService.reserve and EmailSender |
| Response | Every valid booking is still Accepted and saved; the failed message is reported |
| Measure | 0 lost bookings; every failed message is counted |
| Checked in | P04 (R6 test, done) and P10 |

## S1 · Performance: free-room search stays fast

| Part | S1 |
|---|---|
| Source | 200 guests |
| Stimulus | They search free rooms for 12–14 Nov |
| Environment | Within one minute, normal operation |
| Artifact | The free-room search in BookingService (find_free_rooms) |
| Response | Correct free rooms are returned |
| Measure | p95 response ≤ 1 second |
| Checked in | P08 (cache), P23 (load test) |

## S2 · Data integrity: no double booking

| Part | S2 |
|---|---|
| Source | 100 pairs of guests |
| Stimulus | Each pair books the same room and nights at the same moment |
| Environment | Concurrent requests, normal operation |
| Artifact | BookingService.reserve and reservation storage (ReservationStore) |
| Response | Exactly one Confirmed reservation per pair; the other request is rejected |
| Measure | 0 double bookings |
| Checked in | P09 |

## S4 · Security: guests see only their own reservations

| Part | S4 |
|---|---|
| Source | A guest |
| Stimulus | Tries 100 times to read another guest's reservation |
| Environment | Normal operation, guest is signed in |
| Artifact | Reservation read access (ownership check) |
| Response | Access is denied every time |
| Measure | 0 reservations shown to the wrong guest |
| Checked in | P21 |

## S5 · Modifiability: SMS is added without editing BookingService

| Part | S5 |
|---|---|
| Source | The hotel manager |
| Stimulus | The hotel adds SMS confirmations |
| Environment | Development time |
| Artifact | Notification senders (EmailSender and the new SMS sender) |
| Response | SMS is added as a new sender; BookingService is not edited |
| Measure | BookingService not edited; at most 2 files change |
| Checked in | P04 (SMS sender, done) |

## S6 · Sustainability: the search uses less energy

| Part | S6 |
|---|---|
| Source | The development team |
| Stimulus | The same 1,000 searches run before and after a change |
| Environment | Same load and same data before and after |
| Artifact | The free-room search in BookingService (find_free_rooms) |
| Response | The search uses less energy after the change |
| Measure | At least 20% fewer watt-hours per 1,000 completed searches |
| Checked in | P08, P24 |
