# Anonymous Confession → Instagram

Public link → anonymous text → you approve at `/admin` → rendered slides (carousel if long) posted to feed + every slide to Stories. $0/month.

## Local dry run
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # set ADMIN_PASSWORD, uncomment DRY_RUN=1
.venv/bin/flask --app app run   # http://localhost:5000  (admin: any user + ADMIN_PASSWORD)
.venv/bin/python test_render.py
```
Approved images land in `static/posts/<id>/`.

## Meta setup (once, free, no app review)
1. developers.facebook.com → Create app → Business → add product **Instagram** → *API setup with Instagram login*.
2. Add your IG Business/Creator account under **Instagram testers**; accept in the IG app (Settings → Apps and websites → Tester invites).
3. Click **Generate token** (scopes `instagram_business_basic`, `instagram_business_content_publish`). Put the token and Instagram user ID in `.env`.
4. Leave the app in Development mode.

## PythonAnywhere (free) deploy
1. Web → Add new web app → Flask → point the WSGI file at `/home/<user>/confession/app.py` (`from app import app as application`).
2. Upload the project, create `.env` (`BASE_URL=https://<user>.pythonanywhere.com`, no `DRY_RUN`).
3. Web tab → Static files: URL `/static/` → `/home/<user>/confession/static/` (Instagram fetches images from here).
4. Tasks tab → daily: `python3 /home/<user>/confession/refresh_token.py` (token expires after 60 days otherwise).
5. Every 3 months click **Run until 3 months from today** on the Web tab.
6. If posting fails with a connection error, check `graph.instagram.com` is on PythonAnywhere's free-tier whitelist.
