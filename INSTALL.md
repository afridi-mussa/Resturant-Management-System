# Installation & Setup Guide — BistroSaaS

This guide explains, step by step, how to run the **BistroSaaS** project on your
own laptop after cloning it from GitHub. It is written for teammates who may be
new to Django — just follow each step in order.

> Works on **Windows**, **macOS**, and **Linux**. Commands for each are shown.

---

## 1. Prerequisites (install these first)

You need two things installed on your laptop:

1. **Python 3.10 or newer** — download from <https://www.python.org/downloads/>
   - On Windows, during install **tick the box "Add Python to PATH"**.
2. **Git** — download from <https://git-scm.com/downloads>

Check they're installed by opening a terminal (PowerShell on Windows, Terminal
on macOS/Linux) and running:

```bash
python --version
git --version
```

If you see version numbers, you're good. (On macOS/Linux you may need to type
`python3` instead of `python`.)

---

## 2. Get the code from GitHub

Pick a folder where you keep projects, then clone the repository:

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd Resturant-Management
```

> Replace `<YOUR_GITHUB_REPO_URL>` with the link from the GitHub page
> (the green **Code** button → copy the HTTPS URL).

---

## 3. Create a virtual environment

A virtual environment keeps this project's packages separate from your system.

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

After activating, your terminal prompt should start with `(venv)`.

> If Windows blocks activation with a script-execution error, run this once,
> then try activating again:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

## 4. Install the dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

This installs Django, Django REST Framework, and Pillow.

---

## 5. Set up the database

Create the database tables:

```bash
python manage.py migrate
```

> **Note:** This project uses SQLite, so no database server setup is needed.
> If a `db.sqlite3` file was included in the repo you can skip ahead, but
> running `migrate` is always safe.

---

## 6. Create an admin account

You have **two options**:

**Option A — via the website (recommended):**
1. Start the server (next step), open the site, go to **Register**.
2. Choose **Role = Admin** and enter the secret key: **`admin123`**.

**Option B — via the command line:**
```bash
python manage.py createsuperuser
```
Then follow the prompts (username, email, password).

---

## 7. Run the project

```bash
python manage.py runserver
```

You'll see output ending with:

```
Starting development server at http://127.0.0.1:8000/
```

Open that link in your browser: **http://127.0.0.1:8000/**

- Main site: <http://127.0.0.1:8000/>
- Admin panel: <http://127.0.0.1:8000/admin/>
- Menu API: <http://127.0.0.1:8000/api/menu/>

To stop the server, press **Ctrl + C** in the terminal.

---

## 8. Try it out

1. **Register** a normal customer account (Role = Customer).
2. Log in as your **Admin** account and **add a category** and some
   **menu items** (with images) using the **Manage Items** / **Add Menu Item**
   button.
3. Log back in as the **customer**, go to **Place Order**, pick items, and submit.
4. As the **admin**, open **Manage Orders** and confirm/complete the order.
5. As the **customer**, see the notification badge update on **My Orders**.

---

## Daily use (after the first setup)

Every time you come back to work on the project:

```bash
# 1. Go into the project folder
cd Resturant-Management

# 2. Activate the virtual environment
#    Windows:
venv\Scripts\activate
#    macOS/Linux:
source venv/bin/activate

# 3. Run the server
python manage.py runserver
```

If a teammate added new packages or changed models, also run:

```bash
pip install -r requirements.txt
python manage.py migrate
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python` not found | Try `python3`. On Windows, reinstall Python and tick "Add to PATH". |
| `(venv)` not showing | The virtual environment isn't active — re-run the activate command from step 3. |
| Activation blocked on Windows | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again. |
| `ModuleNotFoundError: No module named 'django'` | The venv isn't active, or you skipped `pip install -r requirements.txt`. |
| Images won't upload/show | Make sure Pillow installed correctly (it's in `requirements.txt`). |
| Port already in use | Run on another port: `python manage.py runserver 8001`. |
| Can't register as Admin | The secret key must be exactly `admin123`. |

---

## What NOT to commit to GitHub

The repository includes a `.gitignore` that already excludes these, but as a
reminder, **don't push**:

- `venv/` — everyone creates their own.
- `db.sqlite3` — personal/local data (optional to share for demos).
- `__pycache__/` — auto-generated Python cache.
- Uploaded files in `media/` — usually local test data.

---

Need the full feature/route documentation? See **[README.md](README.md)**.
