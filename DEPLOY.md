# Deploying BistroSaaS on PythonAnywhere (Free)

Netlify/Vercel sirf static sites ke liye hain — Django (Python backend) wahan
nahi chalta. PythonAnywhere Django ke liye banaya gaya hai aur free hai.

Neeche har step diya gaya hai. `YOURNAME` ko apne PythonAnywhere username se
replace karein.

---

## Step 1 — Account banayein
1. <https://www.pythonanywhere.com/> pe jayein.
2. **Pricing & signup → Create a Beginner account (free)**.
3. Username yaad rakhein — aapki site `YOURNAME.pythonanywhere.com` hogi.

---

## Step 2 — Code clone karein (Bash console)
1. Dashboard pe upar **Consoles → Bash** kholein.
2. Ye command chalayein:

```bash
git clone https://github.com/afridi-mussa/Resturant-Management-System.git
```

3. Folder mein jayein:

```bash
cd Resturant-Management-System
```

---

## Step 3 — Virtual environment + packages
Bash console mein (Python 3.13 use karein — latest available):

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 4 — Database + admin + static files
Isi console mein:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

`createsuperuser` mein username/email/password daalein (ye aapka admin hoga).

---

## Step 5 — Web app banayein
1. Dashboard pe **Web → Add a new web app** pe click karein.
2. **Manual configuration** chunein (Django wala nahi — Manual!).
3. Python version **3.13** chunein.

---

## Step 6 — Virtualenv set karein
**Web** tab mein neeche scroll karke **Virtualenv** section mein ye path daalein:

```
/home/YOURNAME/Resturant-Management-System/venv
```

---

## Step 7 — WSGI file edit karein
1. **Web** tab mein **WSGI configuration file** wale link pe click karein
   (kuch aisa: `/var/www/YOURNAME_pythonanywhere_com_wsgi.py`).
2. Us file ka SAARA content delete karke ye paste karein
   (`YOURNAME` replace karna na bhoolein):

```python
import os
import sys

# Project folder ko path mein add karein
path = '/home/YOURNAME/Resturant-Management-System'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'bistro_saas.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

3. **Save** karein.

---

## Step 8 — Static aur Media files map karein
Isi **Web** tab mein **Static files** section mein 2 entries add karein:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOURNAME/Resturant-Management-System/staticfiles` |
| `/media/` | `/home/YOURNAME/Resturant-Management-System/media` |

---

## Step 9 — Reload karein
**Web** tab mein upar bara green **Reload** button dabayein.

Ab apni site kholein:

```
https://YOURNAME.pythonanywhere.com/
```

Admin panel: `https://YOURNAME.pythonanywhere.com/admin/`

---

## Baad mein code update karne ka tareeqa
Jab aap apne computer se naye changes GitHub pe push karein, to PythonAnywhere
ke Bash console mein:

```bash
cd Resturant-Management-System
git pull
source venv/bin/activate
pip install -r requirements.txt        # agar naye packages aaye hon
python manage.py migrate               # agar models change huए hon
python manage.py collectstatic --noinput
```

Phir **Web** tab se **Reload** dabayein.

---

## Common masail
| Masla | Hal |
|-------|-----|
| "DisallowedHost" error | settings.py mein `ALLOWED_HOSTS` mein `.pythonanywhere.com` already hai — push/pull check karein. |
| Admin page bina design ke | `collectstatic` chalayein + Step 8 ka static mapping check karein → Reload. |
| Images nahi dikh rahin | Step 8 ka `/media/` mapping check karein → Reload. |
| "Something went wrong" | Web tab mein **Error log** kholein, last lines parhein. |
| Python version error | venv aur web app dono mein same Python (3.13) hona chahiye. |
