# Hospital Feedback System API

A FastAPI backend for a QR-code-driven patient feedback system: a patient
scans a QR code posted in a hospital department, answers a short survey, and
hospital admins review and respond to the feedback.

## Two auth schemes

- **Admins** authenticate with a JWT (RS256), obtained via `POST /auth/login`
  and sent as `Authorization: Bearer <token>`.
- **Patients** never have a password. Scanning a department's QR code
  (`POST /qr-scan/{token}`) creates an anonymous patient record and returns a
  one-time **session token**, sent back as the `X-Session-Token` header on
  every subsequent call (submitting answers, checking survey progress).

## Endpoint security at a glance

| Area | Public | Requires admin JWT | Requires patient session |
|---|---|---|---|
| `POST /auth/register` | only when no admin exists yet | after that, requires `super_admin` | — |
| `POST /auth/login` | yes (rate-limited) | — | — |
| `GET /departments`, `GET /feedback-categories`, `GET /questions` | yes (read-only, so a patient can render the survey before authenticating) | — | — |
| `POST /qr-scan/{token}` | yes (rate-limited) | — | — |
| Writes to departments / categories / questions / admins | — | yes | — |
| `POST /feedback-responses`, `GET /feedback-responses/me`, `GET /survey-progress/me`, `GET /patients/me` | — | — | yes |
| `GET /patients`, `GET /feedback-responses`, `GET /survey-progress/{id}`, `GET /qr-scans`, `/admin-replies/*` | — | yes | — |

Notable choices:
- **Bootstrap-then-lock registration.** `POST /auth/register` is only public
  while the `admin` table is empty (so a fresh deployment can create its
  first account). Every admin after that must be created by a `super_admin`
  via `POST /admins`.
- **Server-assigned identity on every write.** `patient_id` on a feedback
  answer and `admin_id` on a reply are taken from the authenticated
  session/token, never from the request body — a patient can't submit as
  someone else, an admin can't attribute a reply to a colleague.
- **Asymmetric JWTs.** Admin tokens are signed RS256 with a private key the
  API holds and verified with the matching public key; the algorithm list is
  pinned so a token can't downgrade itself to `none` or a symmetric alg.
- **Opaque, hashed patient sessions.** The QR-scan endpoint hands the patient
  a random 256-bit token; only its SHA-256 hash is stored, so a database
  leak can't be replayed as a live session.
- **QR tokens aren't leaked in listings.** `GET /departments` (public) never
  includes `qr_code_token`; an admin fetches it explicitly via
  `GET /departments/{id}/qr-token`, and can rotate it if a poster is
  compromised.
- **Rate limiting** on `POST /auth/login` and `POST /qr-scan/{token}` (the
  only two endpoints reachable without any token).
- **Passwords**: bcrypt-hashed, 12+ character minimum enforced at the schema
  level, and login takes the same code path (and roughly the same time) for
  an unknown email as for a wrong password.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn hospital_feedback_system.main:app --reload
```

The checked-in `.env` runs against a local SQLite file (`dev.db`) with tables
auto-created — nothing else to set up. Open `http://localhost:8000/docs` for
interactive API docs, and `POST /auth/register` to create your first
(super_admin) account.

### Running against Postgres

Set `DATABASE_URL` (see `.env.example`), leave `AUTO_CREATE_TABLES` unset
(default `false`), and manage the schema with Alembic instead:

```bash
alembic upgrade head
```

### JWT keys

The repo ships a keypair in `keys/` so the app runs out of the box — **treat
it as a dev-only placeholder** and generate your own before deploying
anywhere real:

```bash
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

On platforms where you can't commit key files (e.g. Heroku), set the
`PRIVATE_KEY` / `PUBLIC_KEY` env vars to the PEM text directly instead of
`PRIVATE_KEY_PATH` / `PUBLIC_KEY_PATH`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests run against a throwaway SQLite file and a freshly generated RSA
keypair (never the checked-in one) — see `tests/conftest.py`. Each test gets
a clean schema. `tests/test_admin.py` covers auth/registration lockdown and
role-based access; `tests/test_feedback.py` covers the QR-scan → answer →
progress flow and patient/admin data isolation.

## Project layout

```
hospital_feedback_system/
  core/       security (JWTs, hashing, opaque tokens), rate limiting, deps
  models/     SQLAlchemy models
  schemas/    Pydantic request/response models
  repositories/  thin CRUD wrappers per model
  services/   business logic (validation, survey progress, etc.)
  routers/    HTTP layer — this is where auth is enforced per endpoint
alembic/      migrations
tests/        pytest suite (SQLite + throwaway keys, no external services)
```