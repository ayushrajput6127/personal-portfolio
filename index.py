import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME", "portfolio_db")

# ---- MongoDB connection (lazy, so the app can still boot without it) ----
client = None
db = None

def get_db():
    """Return a cached MongoDB database handle, connecting on first use."""
    global client, db
    if db is None:
        if not MONGODB_URI:
            raise RuntimeError(
                "MONGODB_URI is not set. Add it to your .env file locally, "
                "or to your Vercel project's Environment Variables."
            )
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
    return db


# ---- Fallback data used only if the database is empty/unreachable ----
FALLBACK_PROJECTS = [
    {
        "title": "Sample Project",
        "description": "Add your real projects in MongoDB — this is placeholder data.",
        "tech_stack": ["Flask", "MongoDB", "JavaScript"],
        "github_url": "#",
        "live_url": "#",
        "image": "/static/images/placeholder.png",
        "featured": True,
    }
]

FALLBACK_PROFILE = {
    "name": "Your Name",
    "title": "Full-Stack Developer",
    "bio": "Update your profile info directly in MongoDB (see seed_db.py).",
    "email": "you@example.com",
    "github": "https://github.com/yourusername",
    "linkedin": "https://linkedin.com/in/yourusername",
    "resume_url": "#",
    "skills": ["Python", "Flask", "MongoDB", "JavaScript", "HTML/CSS"],
}


@app.route("/")
def home():
    try:
        database = get_db()
        profile = database.profile.find_one() or FALLBACK_PROFILE
        projects = list(database.projects.find({"featured": True}).limit(3))
        if not projects:
            projects = FALLBACK_PROJECTS
    except Exception:
        profile = FALLBACK_PROFILE
        projects = FALLBACK_PROJECTS
    return render_template("index.html", profile=profile, projects=projects)


@app.route("/projects")
def projects_page():
    try:
        database = get_db()
        projects = list(database.projects.find().sort("_id", -1))
        if not projects:
            projects = FALLBACK_PROJECTS
    except Exception:
        projects = FALLBACK_PROJECTS
    return render_template("projects.html", projects=projects)


@app.route("/about")
def about():
    try:
        database = get_db()
        profile = database.profile.find_one() or FALLBACK_PROFILE
    except Exception:
        profile = FALLBACK_PROFILE
    return render_template("about.html", profile=profile)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in every field before sending.", "error")
            return redirect(url_for("contact"))

        try:
            database = get_db()
            database.messages.insert_one(
                {
                    "name": name,
                    "email": email,
                    "message": message,
                    "created_at": datetime.utcnow(),
                }
            )
            flash("Thanks for reaching out! I'll get back to you soon.", "success")
        except Exception as exc:
            flash(f"Could not save your message right now: {exc}", "error")

        return redirect(url_for("contact"))

    return render_template("contact.html")


# ---- Simple JSON API, handy for the JS on the front end or future use ----
@app.route("/api/projects")
def api_projects():
    try:
        database = get_db()
        projects = list(database.projects.find())
        for p in projects:
            p["_id"] = str(p["_id"])
        return jsonify(projects)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/healthz")
def healthz():
    try:
        get_db().command("ping")
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as exc:
        return jsonify({"status": "degraded", "db_error": str(exc)}), 200


# Vercel's Python runtime looks for a WSGI/ASGI callable named `app`.
if __name__ == "__main__":
    app.run(debug=True, port=5000)
