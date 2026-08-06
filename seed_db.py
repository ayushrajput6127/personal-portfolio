
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME", "portfolio_db")

if not MONGODB_URI:
    raise SystemExit("Set MONGODB_URI in your .env file first.")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# ---- 1. Profile / About info ----
profile = {
    "name": "Ayush",
    "title": "Full-Stack Developer",
    "bio": (
        "I'm a student passionate about IT, networking, and web development. "
        "This portfolio showcases projects I've built while learning full-stack "
        "development with Flask and MongoDB."
    ),
    "email": "you@example.com",
    "github": "https://github.com/yourusername",
    "linkedin": "https://linkedin.com/in/yourusername",
    "resume_url": "#",
    "skills": [
        "Python", "Flask", "MongoDB", "JavaScript",
        "HTML/CSS", "Networking Fundamentals", "Git/GitHub",
    ],
}

db.profile.delete_many({})
db.profile.insert_one(profile)

# ---- 2. Projects ----
projects = [
    {
        "title": "Personal Portfolio Website",
        "description": "A full-stack portfolio built with Flask, MongoDB, and deployed on Vercel.",
        "tech_stack": ["Flask", "MongoDB", "HTML/CSS", "JavaScript", "Vercel"],
        "github_url": "https://github.com/yourusername/portfolio",
        "live_url": "https://your-portfolio.vercel.app",
        "image": "/static/images/placeholder.png",
        "featured": True,
    },
    {
        "title": "Task Management App",
        "description": "A CRUD task tracker with authentication and real-time updates.",
        "tech_stack": ["Flask", "MongoDB", "JavaScript"],
        "github_url": "https://github.com/yourusername/task-manager",
        "live_url": "#",
        "image": "/static/images/placeholder.png",
        "featured": True,
    },
]

db.projects.delete_many({})
db.projects.insert_many(projects)

print(f"Seeded {db.projects.count_documents({})} projects and profile info into '{DB_NAME}'.")
