# PDP University — ASDA Kurs Loyihasi Shartlari (P01 – P08)

**Kurs:** Advanced Software Design & Architecture (ASDA)  
**Manba platforma:** https://teaching.ultimerinc.com/  
**Loyiha papkasi:** `hotel-booking/` (Python 3.10+)

---

## Ketma-ketlik va umumiy ko'rinish

Har bir amaliy mashg'ulot (P01 dan P08 gacha) avvalgi bosqich ustiga quriladi va yagona `hotel-booking/` loyihasida mujassamlashgan:

| Bosqich | Rasmiy nomi | Arxitektura maqsadi | Yakuniy tekshiruv |
| :--- | :--- | :--- | :--- |
| **P01** | Kursga kirish va loyiha poydevori | Muammoni aniqlash, ko'lam, invariantlar, sifat talablari, lug'at | 15 ta banddan iborat to'liq hujjat (`docs/p01-project-baseline.md`) |
| **P02** | Operatsion tizim, yadro va jarayon sikli | Foydalanuvchi vs yadro rejimi, PID/PPID, bloklanuvchi I/O, chiqish kodlari (`7` → `0`) | `tools/p02_os_lab/{parent,child}.py`, `output/child-result.txt`, `docs/p02-os-lifecycle.md` |
| **P03** | Mehmonxona bron ilovasi: talablardan ilk kodgacha | Funksional talablar `R1–R5`, 5 ta UML diagramma, xotiradagi v1 kod va race condition | `main.py --demo` (9 ta aniq satr) + `--race` (ikkita bandlik) + 5 sahifali `diagrams.drawio` |
| **P04** | Kodni tozalash (Refactoring) va xatti-harakatni o'zgartirmaslik | Xatti-harakatni qulflovchi testlar, SOLID, `Protocol` DI, `R6` (xabar xatosi), SMS xabarnomasi | `python -m unittest -v` (8 ta yashil test), o'zgarmas demo va race natijasi, `Classes - after` UML |
| **P05** | Mehmonxonani chegaralangan kontekstlarga ajratish | Manfaatdorlar, o'lchanadigan sifat ssenariylari `S1–S6`, 18 ta lug'at so'zi, 4 ta kontekst | `docs/quality-scenarios.md`, `docs/contexts.md` (18 so'z, 8 qoida, 3 chegara), `Context map` UML |
| **P06** | Kontekstlarni chegaralari tekshiriladigan modullarga aylantirish | Modulli monolit (`rooms`, `reservations`, `payments`, `notifications`), `import-linter`, ADR-001 | 11 ta yashil tekshiruv (8 ta `unittest` + 3 ta `lint-imports` shartnomasi), ADR-001, `Modules` UML |
| **P07** | Sig'im hisobi va PostgreSQL bilan HTTP API | Sig'im hisobi, OpenAPI 3.1, FastAPI HTTP qatlami (`:5080`), SQLAlchemy + PostgreSQL 18 | 15 ta yashil tekshiruv (12 ta test + 3 shartnoma), Docker PostgreSQL, 7 ta curl tekshiruvi |
| **P08** | Bo'sh xonalarni qidirishni keshga olish va eskirish xavfi | `/stats` telemetriya, `tools/measure.py` (1000 ta qidiruv), Redis 8 cache-aside, versiyali tozalash, ADR-002 | 17 ta yashil tekshiruv (14 ta test + 3 shartnoma), Docker Redis, `docs/cache-experiment.md`, ADR-002 |

---

## P01 · Kursga kirish va loyiha poydevori (Project Baseline)

### Maqsad va ko'lam
Ilova kodini yozishdan oldin manfaatdor tomonlarning ehtiyojlarini, ekranda ko'rinadigan natijalarni va saqlanadigan ma'lumotlar holatini aniqlab olish.

### Talablar
1. **Diagnostika poydevori**:
   - Funksiya va sinf mas'uliyatiga doir misol;
   - SQL orqali ma'lumot izlash so'rovi;
   - Jarayon tugaganda operativ xotira (RAM) va doimiy xotira (Disk) farqi;
   - Shaxsiy o'rganish maqsadi.
2. **Manfaatdor tomonlar (Stakeholders)**:
   - **Mijoz (Alex/Emma)**: Bo'sh xonani ko'rish, bron so'rash, tasdiqni tekshirish (`Confirmed` yoki `Sold out`).
   - **Tashkilotchi (Claire)**: Tasdiqlangan buyurtmalar ro'yxatini me'yoridan ortiq band bo'lmasdan ko'rish.
   - **Qo'llab-quvvatlash xodimi (Daniel)**: ID orqali saqlangan bronni tekshirish.
   - **V1 ko'lami**: 20 ta raqamlanmagan sig'im, bitta mijozga 1 ta bron, to'lovsiz, bekor qilish/kutish ro'yxatisiz.
3. **Funksional ehtiyojlar**:
   - Bo'sh joyni tekshirish, bron qilish, holatni tekshirish (Start, Action, Visible Result, Saved-Data Result).
4. **Invariant qoidalar**:
   - **Sig'im qoidasi**: Tasdiqlangan buyurtmalar soni sig'imdan (20) oshib ketmaydi. Joy to'lganda `Sold out` qaytariladi.
   - **Dublikat/Idempotentlik qoidasi**: Bir mijozga faqat bitta tasdiqlangan bron ruxsat etiladi.
5. **Sifat xavotirlari**:
   - Email tizimi ishlamay qolsa ham bron yo'qolmasligi;
   - Bir vaqtda oxirgi o'ringa so'rov tushganda ortiqcha bron qilinmasligi;
   - Tarmoq uzilganda ma'lumotning tiklanishi.
6. **Kontekst eskizi va lug'at**:
   - Tizimlar va foydalanuvchilar o'rtasidagi xabarlar ko'rsatilgan diagramma.
   - 5 ta asosiy atama: *Capacity*, *Stay*, *Confirmed booking*, *Sold out*, *Cancellation*.

---

## P02 · Operatsion tizim, yadro va jarayon hayot sikli

### Talablar
1. **Ishga tushuvchi skriptlar (`tools/p02_os_lab/parent.py` va `child.py`)**:
   - `parent.py` bolalar jarayonini (`child.py`) unbuffered holatda ishga tushiradi va uning chiqish kodini kutadi.
   - `child.py` o'zining PID va PPID sini chiqaradi, CPU siklini hisoblaydi, `input(...)` orqali bloklanuvchi holatga o'tadi (bunda tashqi vositalar yordamida jarayon o'lchanadi), natijani `output/child-result.txt` ga yozadi va belgilangan chiqish kodi bilan tugaydi.
2. **Eksperiment**:
   - `EXIT_CODE` ni `7` dan `0` ga o'zgartirib, ota jarayon buni qanday qabul qilishi va diskdagi fayl saqlanib qolishini tekshirish.
3. **`docs/p02-os-lifecycle.md`**:
   - 8 ta bo'lim: `environment`, `boundary`, `inspection`, `lifecycle`, `comparison` (POSIX fork/exec vs Windows CreateProcess), `experiment`, `adr`, `reflection`.

---

## P03 · Mehmonxona bron ilovasi: talablardan birinchi kodgacha

### Funksional talablar (`docs/requirements.md`)
- **R1 · Qidiruv**: Berilgan oraliq bo'yicha bo'sh xonalarni chiqarish (`[check_in, check_out)` yarim ochiq oraliq).
- **R2 · Bron qilish**: Bo'sh xonani band qilish va rezervatsiya ID qaytarish (`Accepted R101`).
- **R3 · To'qnashuvga yo'l qo'ymaslik**: Bitta xonani bir vaqtda ikkita tasdiqlangan buyurtmaga berib bo'lmaydi. `check_out > check_in` bo'lishi shart.
- **R4 · Bekor qilish**: Bekor qilinganda status `Cancelled` bo'ladi (ma'lumot o'chirilmaydi) va xona yana bo'shaydi. Ikkinchi marta bekor qilish `False` qaytaradi.
- **R5 · Ko'rish**: Rezervatsiyani ID orqali ma'lumotlarini ko'rish.

### Talab qilingan natijalar
- **UML diagrammalar (`docs/diagrams.drawio`)**: 5 ta sahifa (`Use cases`, `Classes`, `Sequence - book`, `Sequence - cancel`, `Activity - book`).
- **Dizayn qaydlari (`docs/design-notes.md`)**: Nega oldin dizayn qilinishi, metodlarning to'g'ri sinflarga joylashishi va check-then-act poygasi.
- **Ishga tushuvchi kod**: 9 satrli toza demo va `--race` orqali poyga sharoitida ikkita buyurtma yuzaga kelishini ko'rsatish.

---

## P04 · Kodni refaktoring qilish va xatti-harakatni buzmaslik

### Talablar
1. **Modullarga ajratish**:
   - `hotel_booking/domain.py`: `DateRange`, `Guest`, `Room`, `ReservationStatus`, `Reservation`.
   - `hotel_booking/stores.py`: `ReservationStore` (`Protocol`), `InMemoryReservationStore`.
   - `hotel_booking/notifications.py`: `NotificationSender` (`Protocol`), `EmailNotificationSender`, `SmsNotificationSender`.
   - `hotel_booking/booking.py`: `BookingResult`, `BookingService` faqat protokollarga bog'lanadi (Dependency Inversion).
2. **Yangi talab `R6 · Xabar yuborishdagi xato`**:
   - Agar tasdiq xabari yuborilmay qolsa, bron saqlanib qoladi (`Accepted`) va xatolik `notification_failed=True` shaklida bildiriladi.
3. **8 ta Unit Test (`test_booking_service.py`)**:
   - Barcha ssenariylar va R6 qoidasi avtomatlashtirilgan testlar bilan tekshiriladi.
4. **UML**:
   - `Classes - after` sahifasi qo'shiladi.

---

## P05 · Bounded Contexts (Chegaralangan kontekstlar)

### Talablar
1. **`docs/quality-scenarios.md`**:
   - 6 ta aniq o'lchanadigan sifat ssenariysi: `S1` (unumdorlik), `S2` (ma'lumot butunligi), `S3` (ishonchlilik), `S4` (xavfsizlik), `S5` (modifikatsiya qilinuvchanlik), `S6` (barqarorlik).
2. **`docs/contexts.md`**:
   - 18 ta yagona til (ubiquitous language) atamasi;
   - 4 ta kontekst: `Rooms`, `Reservations`, `Payments`, `Notifications`;
   - "Bir xil so'z, har xil ma'no" tahlili (`Room`, `Status`, `Cancel`);
   - 8 ta qoidaning egalari va kontekstlararo 3 ta chegara ma'lumotlar almashinuvi.
3. **UML**:
   - `Context map` sahifasi.

---

## P06 · Modulli monolit va qat'iy import chegaralari

### Talablar
1. **4 ta alohida subpaket (`hotel_booking/`)**:
   - Har bir kontekst (`rooms`, `reservations`, `payments`, `notifications`) o'zining ommaviy interfeysini `__init__.py` orqali taqdim etadi, ichki amalga oshirish esa `internal.py` da yashiriladi.
2. **`pyproject.toml` va `import-linter`**:
   - 3 ta me'moriy shartnoma o'rnatiladi:
     1. Reservations faqat boshqa modullarning ommaviy shartnomalariga murojaat qiladi.
     2. Rooms hech qanday boshqa modulga bog'lanmaydi.
     3. Payments va Notifications Reservations ga bog'lanmaydi.
3. **ADR-001**:
   - `docs/adr-001-modular-monolith.md` me'moriy qaror hujjati.
4. **UML**:
   - `Modules` sahifasi.

---

## P07 · Sig'im hisobi va PostgreSQL bilan HTTP API

### Talablar
1. **Sig'im hisobi va L04**:
   - `docs/l04-notes.md` va `docs/capacity.md` (eng yuqori yuklama `3.33/s`, ma'lumotlar hajmi va o'lchovlar).
2. **PostgreSQL Docker muhiti**:
   - `docker-compose.yml` va `db/init.sql` (kontekstlararo foreign key yo'q, `rooms` va `reservations` alohida jadvallar).
3. **OpenAPI 3.1 spetsifikatsiyasi**:
   - `docs/openapi.yaml` (`GET /rooms/availability`, `POST /reservations`, `DELETE /reservations/{id}`, RFC 9457 xatolik formati).
4. **FastAPI va SQLAlchemy**:
   - `hotel_booking/api.py`, `PostgresRoomCatalog`, `PostgresReservationStore`.
5. **API testlari**:
   - `test_api.py` (4 ta test). Jami 15 ta yashil tekshiruv (12 ta test + 3 ta linter shartnomasi).

---

## P08 · Redis kesh, o'lchash va kesh eskirish xavfi

### Talablar
1. **Telemetriya va hisoblagichlar**:
   - `GET /stats` oxirgi nuqtasi (`searches`, `databaseQueries`, `cacheHits`, `cacheMisses`).
2. **Redis 8 kesh-aside**:
   - `docker-compose.yml` ga Redis 8 qo'shish;
   - `hotel_booking/api_cache.py`: `AvailabilityCache` (TTL = 30s, versiyali kalit `availability:version`).
   - Yangi bron yoki bekor qilish sodir bo'lganda kesh darhol yangilanadi/eskirtiriladi (`cache.invalidate()`).
3. **O'lchov vositasi (`tools/measure.py`)**:
   - 1000 ta ketma-ket qidiruv so'rovi yuborib, o'rtacha va p95 vaqtlarini hisoblash.
4. **ADR-002 va hisobot**:
   - `docs/cache-experiment.md` va `docs/adr-002-cache-availability.md`.
5. **Yakuniy testlar**:
   - 14 ta `unittest` va 3 ta `import-linter` shartnomasi — jami **17 ta yashil tekshiruv**.
