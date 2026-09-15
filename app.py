"""Anonymous confession submit page + admin approval queue that posts to Instagram."""
import os
import sqlite3
import traceback
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, Response, flash, redirect, render_template, request, url_for

import render

load_dotenv(Path(__file__).with_name(".env"))
if not os.environ.get("DRY_RUN"):
    import instagram

ROOT = Path(__file__).parent
DB = ROOT / "confessions.db"
MAX_LEN = 3000

app = Flask(__name__)
app.secret_key = os.environ.get("ADMIN_PASSWORD", "dev")


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS confessions (
        id INTEGER PRIMARY KEY, text TEXT NOT NULL, created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending', number INTEGER, ig_media_id TEXT)""")
    return con


@app.before_request
def admin_auth():
    if request.path.startswith("/admin"):
        auth = request.authorization
        if not auth or auth.password != os.environ.get("ADMIN_PASSWORD"):
            return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="admin"'})


@app.get("/")
def index():
    return render_template("index.html", max_len=MAX_LEN)


@app.post("/submit")
def submit():
    text = request.form.get("text", "").strip()
    if not text or len(text) > MAX_LEN:
        return render_template("index.html", max_len=MAX_LEN, error="Please write between 1 and 3000 characters."), 400
    with db() as con:
        con.execute("INSERT INTO confessions (text, created_at) VALUES (?, ?)", (text, date.today().isoformat()))
    return render_template("index.html", max_len=MAX_LEN, done=True)


@app.get("/admin")
def admin():
    with db() as con:
        rows = con.execute("SELECT * FROM confessions WHERE status='pending' ORDER BY id").fetchall()
    return render_template("admin.html", rows=rows)


@app.post("/admin/<int:cid>/approve")
def approve(cid):
    # ponytail: sync post inside the request (~20-60s); move to a scheduled task if PA timeouts bite
    with db() as con:
        row = con.execute("SELECT * FROM confessions WHERE id=? AND status='pending'", (cid,)).fetchone()
        if not row:
            return redirect(url_for("admin"))
        number = row["number"] or (con.execute("SELECT COALESCE(MAX(number),0)+1 FROM confessions").fetchone()[0])
        con.execute("UPDATE confessions SET number=? WHERE id=?", (number, cid))

    date_str = date.fromisoformat(row["created_at"]).strftime("%d %b %Y")
    out = ROOT / "static" / "posts" / str(cid)
    feed = render.render(row["text"], number, date_str, out, "feed", render.FEED)
    story = render.render(row["text"], number, date_str, out, "story", render.STORY)
    urls = lambda paths: [f"{os.environ['BASE_URL'].rstrip('/')}/static/posts/{cid}/{p.name}" for p in paths]

    try:
        if os.environ.get("DRY_RUN"):
            media_id = "dry-run"
        else:
            media_id = instagram.post_feed(urls(feed), f"Confession #{number} · {date_str}")
            instagram.post_stories(urls(story))
    except Exception as e:
        traceback.print_exc()
        flash(f"#{cid} failed: {e}")
        return redirect(url_for("admin"))

    with db() as con:
        con.execute("UPDATE confessions SET status='posted', ig_media_id=? WHERE id=?", (media_id, cid))
    flash(f"#{cid} posted as Confession #{number}")
    return redirect(url_for("admin"))


@app.post("/admin/<int:cid>/reject")
def reject(cid):
    with db() as con:
        con.execute("UPDATE confessions SET status='rejected' WHERE id=? AND status='pending'", (cid,))
    return redirect(url_for("admin"))
