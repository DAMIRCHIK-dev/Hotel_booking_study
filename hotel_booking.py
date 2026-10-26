"""P03 · Hotel booking app, version 1.

A small hotel with rooms R7 (Standard) and R8 (Deluxe). Guests book on the
website and a receptionist books for guests who phone or walk in. All bookings
go into one shared list, kept in memory.

Core rule: one room, one night, at most one guest. Dates are half-open:
a booking 12-14 Nov covers the nights of the 12th and 13th, so a new guest
can check in on the 14th.

Run:
    python hotel_booking.py          the demo (requirements R1-R5)
    python hotel_booking.py --race   two guests book the same room at once
"""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass
from datetime import date
from enum import Enum


@dataclass(frozen=True)
class DateRange:
    check_in: date
    check_out: date

    def is_valid(self) -> bool:
        return self.check_out > self.check_in

    def overlaps(self, other: DateRange) -> bool:
        # Half-open ranges: the check-out day is not a night.
        return self.check_in < other.check_out and other.check_in < self.check_out


@dataclass(frozen=True)
class Guest:
    name: str
    email: str


@dataclass(frozen=True)
class Room:
    number: str
    type: str


class ReservationStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


class Reservation:
    def __init__(self, id: str, guest: Guest, room: Room, stay: DateRange) -> None:
        self.id = id
        self.guest = guest
        self.room = room
        self.stay = stay
        self.status = ReservationStatus.CONFIRMED

    def blocks(self, room: Room, stay: DateRange) -> bool:
        return (
            self.status is ReservationStatus.CONFIRMED
            and self.room == room
            and self.stay.overlaps(stay)
        )

    def cancel(self) -> bool:
        # A cancelled reservation is kept, never deleted.
        if self.status is ReservationStatus.CANCELLED:
            return False
        self.status = ReservationStatus.CANCELLED
        return True


class ReservationStore:
    def __init__(self) -> None:
        self._rows: list[Reservation] = []

    def count(self) -> int:
        return len(self._rows)

    def has_overlap(self, room: Room, stay: DateRange) -> bool:
        return any(r.blocks(room, stay) for r in self._rows)

    def save(self, reservation: Reservation) -> None:
        self._rows.append(reservation)

    def find(self, id: str) -> Reservation | None:
        return next((r for r in self._rows if r.id == id), None)

    def count_confirmed(self, room: Room, stay: DateRange) -> int:
        return sum(1 for r in self._rows if r.blocks(room, stay))


class EmailSender:
    """Simulated: no real email, only a counter."""

    def __init__(self) -> None:
        self.sent = 0

    def send_confirmation(self, reservation: Reservation) -> None:
        self.sent += 1


@dataclass(frozen=True)
class BookingResult:
    outcome: str
    reservation_id: str | None = None

    def __str__(self) -> str:
        if self.reservation_id is None:
            return self.outcome
        return f"{self.outcome} {self.reservation_id}"


class BookingService:
    def __init__(
        self,
        rooms: list[Room],
        store: ReservationStore,
        email: EmailSender,
        slow_step_seconds: float = 0,
    ) -> None:
        self.rooms = rooms
        self.store = store
        self.email = email
        self.slow_step_seconds = slow_step_seconds

    def find_free_rooms(self, stay: DateRange) -> list[Room]:
        return [room for room in self.rooms if not self.store.has_overlap(room, stay)]

    def reserve(self, guest: Guest, room: Room, stay: DateRange) -> BookingResult:
        if not stay.is_valid():
            return BookingResult("InvalidDates")
        if self.store.has_overlap(room, stay):
            return BookingResult("Unavailable")
        # Simulates slow work between the check and the save (used by --race).
        time.sleep(self.slow_step_seconds)
        reservation = Reservation(f"R{101 + self.store.count()}", guest, room, stay)
        self.store.save(reservation)
        self.email.send_confirmation(reservation)
        return BookingResult("Accepted", reservation.id)

    def cancel(self, id: str) -> bool:
        reservation = self.store.find(id)
        if reservation is None:
            return False
        return reservation.cancel()

    def view(self, id: str) -> Reservation | None:
        return self.store.find(id)


R7 = Room("R7", "Standard")
R8 = Room("R8", "Deluxe")

MAYA = Guest("Maya", "maya@example.com")
OMAR = Guest("Omar", "omar@example.com")
NORA = Guest("Nora", "nora@example.com")


def nov(a: int, b: int) -> DateRange:
    return DateRange(date(2026, 11, a), date(2026, 11, b))


def names(rooms: list[Room]) -> str:
    return ", ".join(room.number for room in rooms)


def run_demo() -> None:
    email = EmailSender()
    service = BookingService([R7, R8], ReservationStore(), email)

    print(f"Free rooms 12-14 Nov: {names(service.find_free_rooms(nov(12, 14)))}")
    print(f"Maya books R7 12-14 Nov: {service.reserve(MAYA, R7, nov(12, 14))}")

    r = service.view("R101")
    print(
        f"View R101: {r.guest.name}, {r.room.number}, "
        f"{r.stay.check_in.day}-{r.stay.check_out.day} Nov, {r.status.value}"
    )

    print(f"Omar books R7 13-15 Nov: {service.reserve(OMAR, R7, nov(13, 15))}")
    print(f"Nora books R7 14-16 Nov: {service.reserve(NORA, R7, nov(14, 16))}")
    print(f"Omar books R8 15-15 Nov: {service.reserve(OMAR, R8, nov(15, 15))}")
    print(f"Free rooms 12-14 Nov: {names(service.find_free_rooms(nov(12, 14)))}")
    print(f"Maya cancels R101: {service.cancel('R101')}")
    print(f"Free rooms 12-14 Nov: {names(service.find_free_rooms(nov(12, 14)))}")
    print(f"Confirmation emails sent: {email.sent}")


def run_race() -> None:
    store = ReservationStore()
    service = BookingService([R7, R8], store, EmailSender(), slow_step_seconds=0.5)
    stay = nov(12, 14)
    results: dict[str, BookingResult] = {}

    def book(guest: Guest) -> None:
        results[guest.name] = service.reserve(guest, R7, stay)

    print("Maya and Omar both book R7 for 12-14 Nov at the same moment...")
    maya = threading.Thread(target=book, args=(MAYA,))
    omar = threading.Thread(target=book, args=(OMAR,))
    maya.start()
    time.sleep(0.1)
    omar.start()
    maya.join()
    omar.join()

    confirmed = store.count_confirmed(R7, stay)
    print(f"Maya: {results['Maya']}")
    print(f"Omar: {results['Omar']}")
    print(f"Confirmed reservations for R7 on 12-14 Nov: {confirmed}")
    # No lock on purpose: the race is fixed later in the database (P09).
    if confirmed > 1:
        print("Double booking! Both requests checked before either one saved.")
    else:
        print("Only one guest has R7.")


if __name__ == "__main__":
    run_race() if "--race" in sys.argv else run_demo()
