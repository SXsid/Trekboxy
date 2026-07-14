# HimTrek — Trekking Management Application

HimTrek is a web-based Trekking Management Application that connects **Admins**, **Trek Staff**, and **Trekkers** on one platform.

- **Admin** — creates treks, assigns staff, manages users and bookings
- **Staff** — manages their assigned treks and views participant lists
- **Trekker** — browses, books, and tracks their trek history

---

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis running locally (`sudo systemctl start redis-server`) or a remote URL in `.env`

---

## Environment Variables

Create `.env` at the **project root** (next to `backend/` and `frontend/`):

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

REDIS_URL=redis://localhost:6379/

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password        # Gmail App Password, not your login password
MAIL_DEFAULT_SENDER=your-gmail@gmail.com

ADMIN_EMAIL=admin@himtrek.com
ADMIN_PASSWORD=admin123
ADMIN_USERNAME=admin
```

---

## Running Locally

You need **4 terminals**.

### Terminal 1 — Flask API (port 5000)

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Linux/Mac

pip install -r requirements.txt
python run.py
```

The first run automatically creates the SQLite database and seeds the admin account.

### Terminal 2 — Celery Worker (processes background tasks)

```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

### Terminal 3 — Celery Beat (periodic task scheduler)

```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery beat --loglevel=info
```

> **Note:** Celery Beat creates a `celerybeat-schedule` file in the `backend/` folder. This is a small local database it uses to track when each periodic task last ran. It is not your application database — it is safe to delete it if you want to reset the schedule.

### Terminal 4 — Vue Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Project Structure

```
Trekking-Management-Application---V2/
├── .env                        ← environment variables (never commit this)
├── backend/
│   ├── app.py                  ← Flask app factory
│   ├── config.py               ← reads config from environment
│   ├── extensions.py           ← db, jwt, mail, redis, celery instances
│   ├── celery_worker.py        ← Celery entry point
│   ├── run.py                  ← starts the Flask dev server
│   ├── seed.py                 ← creates initial admin account
│   ├── requirements.txt
│   ├── models/                 ← User, Trek, Booking, TaskOutbox
│   ├── api/                    ← Flask Blueprints (auth, treks, bookings, admin, staff)
│   ├── tasks/                  ← Celery tasks (reminders, reports, exports)
│   └── helper/                 ← decorators, cache utils
└── frontend/
    ├── index.html
    ├── vite.config.js          ← proxy config
    └── src/
        ├── main.js             ← app entry
        ├── router.js           ← routes + auth guards
        ├── api.js              ← Axios with JWT interceptor
        ├── store/auth.js       ← Pinia auth store
        ├── App.vue
        ├── components/Navbar.vue
        └── views/
            ├── Landing.vue, Login.vue, Register.vue
            ├── admin/
            ├── staff/
            └── trekker/
```

---

## Background Jobs

| Job                    | Trigger                       | What it does                                                |
| ---------------------- | ----------------------------- | ----------------------------------------------------------- |
| `send_daily_reminders` | Every day at 8:00 AM          | Emails trekkers whose trek starts within 3 days             |
| `send_monthly_report`  | 1st of every month at 9:00 AM | Emails the admin an HTML activity summary                   |
| `export_bookings_csv`  | On user request               | Generates and emails a CSV of the trekker's booking history |
| `process_outbox`       | Every 30 seconds              | Dispatches any PENDING tasks from the TaskOutbox table      |
