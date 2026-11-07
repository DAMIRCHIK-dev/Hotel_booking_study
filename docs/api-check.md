# API check: seven requests against PostgreSQL

Start from an empty database, then start the app in a second terminal:

```text
docker compose down -v
docker compose up -d
```

Run each request from the hotel-booking folder. curl.exe prints the body, then the status code.
Write ✓ after a request when your answer is exactly the expected one.

## 1. Search 12–14 Nov: R7 and R8 are free ✓

```text
curl.exe -s -w "\n%{http_code}\n" "http://localhost:5080/rooms/availability?checkIn=2026-11-12&checkOut=2026-11-14"
```

Expected:

```text
{"checkIn":"2026-11-12","checkOut":"2026-11-14","rooms":[{"number":"R7","type":"Standard"},{"number":"R8","type":"Deluxe"}],"next":null}
200
```

## 2. Maya books R7 for 12–14 Nov ✓

```text
curl.exe -s -w "\n%{http_code}\n" -X POST -H "Content-Type: application/json" --data "@docs/requests/maya-r7.json" http://localhost:5080/reservations
```

Expected:

```text
{"id":"R101","status":"Confirmed","notificationFailed":false}
201
```

## 3. Omar asks for R7 for 13–15 Nov: the night of the 13th is Maya’s ✓

```text
curl.exe -s -w "\n%{http_code}\n" -X POST -H "Content-Type: application/json" --data "@docs/requests/omar-r7.json" http://localhost:5080/reservations
```

Expected:

```text
{"title":"Unavailable","status":409,"detail":"The room is booked for at least one night of this stay."}
409
```

## 4. Omar asks for R8 for 15–15 Nov: no night at all ✓

```text
curl.exe -s -w "\n%{http_code}\n" -X POST -H "Content-Type: application/json" --data "@docs/requests/omar-r8.json" http://localhost:5080/reservations
```

Expected:

```text
{"title":"InvalidDates","status":400,"detail":"checkOut must be after checkIn."}
400
```

## 5. Search 12–14 Nov again: only R8 is free ✓

```text
curl.exe -s -w "\n%{http_code}\n" "http://localhost:5080/rooms/availability?checkIn=2026-11-12&checkOut=2026-11-14"
```

Expected:

```text
{"checkIn":"2026-11-12","checkOut":"2026-11-14","rooms":[{"number":"R8","type":"Deluxe"}],"next":null}
200
```

## 6. Cancel R101 ✓

```text
curl.exe -s -w "\n%{http_code}\n" -X DELETE http://localhost:5080/reservations/R101
```

Expected:

```text
204
```

## 7. Cancel R101 a second time ✓

```text
curl.exe -s -w "\n%{http_code}\n" -X DELETE http://localhost:5080/reservations/R101
```

Expected:

```text
{"title":"NotFound","status":404,"detail":"There is no confirmed reservation R101."}
404
```

## Restart check: the booking survives

## 8. Maya books R7 for 12–14 Nov again ✓

```text
curl.exe -s -w "\n%{http_code}\n" -X POST -H "Content-Type: application/json" --data "@docs/requests/maya-r7.json" http://localhost:5080/reservations
```

Expected:

```text
{"id":"R102","status":"Confirmed","notificationFailed":false}
201
```

## 9. Stop the app (Ctrl+C in its terminal) and start it again ✓

## 10. After the restart, search 12–14 Nov: R7 is still booked ✓

```text
curl.exe -s -w "\n%{http_code}\n" "http://localhost:5080/rooms/availability?checkIn=2026-11-12&checkOut=2026-11-14"
```

Expected:

```text
{"checkIn":"2026-11-12","checkOut":"2026-11-14","rooms":[{"number":"R8","type":"Deluxe"}],"next":null}
200
```

R7 is still booked after the restart: the reservation lives in PostgreSQL, not in the app's memory.

