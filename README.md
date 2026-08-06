# Personal Portfolio Website (Flask + MongoDB + Vercel)

A full-stack personal portfolio: Flask backend, MongoDB for storing your
profile/projects/contact messages, deployed serverlessly on Vercel.

## Project structure

```
portfolio/
├── api/
│   └── index.py          # Flask app (Vercel serverless entrypoint)
├── templates/             # Jinja2 HTML templates
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── seed_db.py             # One-time script to load your data into MongoDB
├── requirements.txt
├── vercel.json             # Vercel build/routing config
├── .env.example
└── .gitignore
```

## 1. Set up MongoDB (free tier is fine)

1. Create a free cluster at https://www.mongodb.com/cloud/atlas
2. Add a database user and allow network access from anywhere (0.0.0.0/0)
   for simplicity, or Vercel's IP ranges for tighter security.
3. Copy your connection string — it looks like:
   `mongodb+srv://<user>:<password>@<cluster>/?retryWrites=true&w=majority`

## 2. Configure locally

```bash
cd portfolio
cp .env.example .env
# edit .env and paste your MONGODB_URI, set a SECRET_KEY
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python seed_db.py          # loads your profile + sample projects into MongoDB
python api/index.py        # runs at http://localhost:5000
```

Edit `seed_db.py` with your real name, bio, skills, and projects before
running it — that's the single source of truth for your content.

## 3. Push to GitHub

```bash
git init
git add .
git commit -m "Initial portfolio"
git branch -M main
git remote add origin https://github.com/<you>/portfolio.git
git push -u origin main
```

## 4. Deploy on Vercel

**Option A — Vercel dashboard**
1. Go to https://vercel.com/new and import your GitHub repo.
2. Framework preset: "Other" (Vercel auto-detects the Python builder from
   `vercel.json`).
3. Under **Environment Variables**, add:
   - `MONGODB_URI` = your Atlas connection string
   - `DB_NAME` = `portfolio_db`
   - `SECRET_KEY` = any random string
4. Click **Deploy**.

**Option B — Vercel CLI**
```bash
npm install -g vercel
vercel login
vercel                 # first deploy, follow prompts
vercel env add MONGODB_URI
vercel env add DB_NAME
vercel env add SECRET_KEY
vercel --prod
```

## 5. Verify it's live

- `/` — home page with your bio + featured projects
- `/projects` — full project list (pulled from MongoDB)
- `/about` — bio and skills
- `/contact` — form that writes messages into the `messages` collection
- `/healthz` — quick check that the DB connection is working
- `/api/projects` — raw JSON of your projects collection

## Notes on how it's wired for Vercel

- Vercel's Python runtime expects a WSGI app object named `app` — that's
  exported from `api/index.py`.
- `vercel.json` routes all non-static requests to that one function and
  serves `/static/*` directly.
- The app is written to **not crash** if `MONGODB_URI` is missing or the
  cluster is unreachable — it falls back to placeholder content so you can
  always see the site rendering, and `/healthz` tells you the real DB status.

## Customizing content

All real content (name, bio, skills, projects, links) lives in MongoDB.
Update it either by re-running `seed_db.py` after editing it, or by
connecting directly with MongoDB Compass / `mongosh` and editing the
`profile` and `projects` collections.
