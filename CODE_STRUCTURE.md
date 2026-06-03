# BistroSaaS — Code Structure (Easy Guide)

This guide explains **what every file and folder does** in very simple words.
If you have never seen Django before, start here. 🙂

---

## The Big Idea (a real restaurant analogy)

Think of this project like a **real restaurant**:

| Restaurant thing | In our project |
|------------------|----------------|
| The building & rules | `bistro_saas/` (settings) |
| The kitchen & staff | `ordering/` (the app that does the work) |
| The menu register / record book | `db.sqlite3` (the database) |
| The printed menus & posters | `templates/` (the HTML pages) |
| Photos of the food | `media/` (uploaded images) |
| The recipe list to set up | `requirements.txt` |

When you open the website, a **waiter (a "view")** takes your request, looks at
the **record book (database)**, and brings back a **printed page (HTML template)**
to show you.

---

## Full Folder Map

```
Resturant-Management/
│
├── manage.py              ← The "remote control" to run commands
├── requirements.txt       ← List of tools the project needs
├── db.sqlite3             ← THE DATABASE (all data is saved here)
│
├── README.md              ← Full project documentation
├── INSTALL.md             ← How to install on a new laptop
├── DEPLOY.md              ← How to put the site online (PythonAnywhere)
├── CODE_STRUCTURE.md      ← This file (what each file does)
│
├── bistro_saas/           ← PROJECT SETTINGS (the "control room")
│   ├── settings.py        ← All settings (database, apps, etc.)
│   ├── urls.py            ← Main address list of the website
│   ├── wsgi.py / asgi.py  ← Connects the site to the web server
│   └── __init__.py        ← Tells Python this is a package
│
├── ordering/              ← THE MAIN APP (where all the work happens)
│   ├── models.py          ← The DATABASE design (tables/shapes of data)
│   ├── views.py           ← The "waiters" (logic for each page)
│   ├── urls.py            ← Web addresses for this app
│   ├── forms.py           ← The input forms (register, add item, etc.)
│   ├── admin.py           ← Settings for the /admin/ control panel
│   ├── serializers.py     ← Turns data into JSON for the API
│   ├── context_processors.py ← Notification numbers on the navbar
│   ├── apps.py            ← App name/config
│   ├── migrations/        ← History of database changes
│   └── templates/ordering/ ← THE HTML PAGES (what you see) ⭐
│
├── templates/             ← Extra project-wide HTML
│   └── admin/submit_line.html ← Adds the red "Cancel" button in admin
│
├── media/                 ← UPLOADED IMAGES
│   ├── menu_items/        ← Food/dish photos
│   └── profile_pics/      ← User profile pictures
│
├── staticfiles/           ← (Created on the server) CSS/JS for the admin page
└── venv/                  ← The private toolbox (NOT uploaded to GitHub)
```

---

## Where is the HTML? 📄

All the pages you SEE are HTML files inside:

```
ordering/templates/ordering/
```

| File | What page it is |
|------|-----------------|
| `base.html` | The master layout (navbar + footer). Every page is built on top of this. |
| `register.html` | Sign-up page |
| `login.html` | Login page |
| `menu_list.html` | The main menu page (with search & filters) |
| `menu_item_detail.html` | One dish's detail page |
| `menu_item_form.html` | Add / edit a dish (admin) |
| `menu_item_confirm_delete.html` | "Are you sure?" delete page |
| `place_order.html` | Page to choose items and order |
| `order_list.html` | "My Orders" history page |
| `manage_orders.html` | Admin page to confirm/manage orders |
| `profile.html` | Edit personal info page |
| `change_password.html` | Change password page |

> **Tip:** `base.html` is the "frame" of a picture. Every other page fills the
> middle part (`{% block content %}`) while keeping the same navbar and footer.

---

## Where is the CSS / Bootstrap? 🎨

This is important and many people get confused here:

- **There is NO separate CSS folder in this project.**
- The design (colors, buttons, layout) comes from **Bootstrap 5**, which is
  loaded **from the internet (a CDN)**.
- Look at the top of `ordering/templates/ordering/base.html` — you will see lines
  like this that pull in Bootstrap:

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/.../bootstrap.min.css" ...>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/.../bootstrap.bundle.min.js"></script>
```

- A tiny bit of **custom CSS** (just a few lines for the sticky footer) is also
  written inside `base.html` between `<style>` and `</style>` tags.
- The CSS files inside `staticfiles/` are **only for the Django admin page** —
  they are created automatically by the `collectstatic` command, not written by us.

**Summary:** Bootstrap = from the internet (CDN). Custom styling = small `<style>`
block in `base.html`. No separate `.css` files to manage.

---

## Where is the Database? 🗄️

- The whole database is **one single file:** `db.sqlite3` (in the main folder).
- It stores EVERYTHING: users, categories, menu items, orders, profiles.
- You **cannot open it as text** (it's a binary file). To see the data, use:
  - The admin panel: `/admin/`
  - Or a tool like "DB Browser for SQLite".
- The **shape** of this data (what columns each table has) is defined in
  `ordering/models.py`.

The 4 main tables (defined in `models.py`):

| Table | What it stores |
|-------|----------------|
| `CustomerProfile` | Extra user info (phone, address, picture) |
| `Category` | Food groups (e.g. Burgers, Drinks) |
| `MenuItem` | Each dish (name, price, image, etc.) |
| `Order` | Customer orders (items, total, status) |

---

## Where are the Images? 🖼️

- Uploaded images are saved in the **`media/`** folder.
- Dish photos → `media/menu_items/`
- Profile pictures → `media/profile_pics/`
- The setting that controls this is `MEDIA_ROOT` in `settings.py`.

---

## How does ONE page work? (step by step)

Example: you open the **menu page**.

1. You type the address `/` in the browser.
2. Django looks in `ordering/urls.py` and finds it points to `MenuListView`.
3. `MenuListView` (in `views.py`) is the **waiter** — it asks the database
   (`models.py` / `db.sqlite3`) for all available menu items.
4. It then picks the page `menu_list.html` (from `templates/`).
5. The HTML page is filled with the data and sent back to your browser.
6. Bootstrap (from the CDN) makes it look nice. ✨

So the flow is always:
**URL → views.py → models.py (data) → HTML template → your screen**

---

## The Most Important Files (if you only read 3)

1. **`ordering/models.py`** — the data design (the heart of the project).
2. **`ordering/views.py`** — the logic for every page (the brain).
3. **`ordering/templates/ordering/base.html`** — the look of every page (the face).

---

## Quick "Where do I change X?" table

| I want to change... | Edit this file |
|---------------------|----------------|
| The look of all pages (navbar/footer) | `ordering/templates/ordering/base.html` |
| What a specific page shows | that page's `.html` + its view in `views.py` |
| The data fields (add a column) | `ordering/models.py` (then run `makemigrations` + `migrate`) |
| A web address / link | `ordering/urls.py` |
| A form's fields | `ordering/forms.py` |
| The admin panel | `ordering/admin.py` |
| Project settings (database, secret key) | `bistro_saas/settings.py` |

---

That's the whole project! For deeper technical details see **README.md**.
For setup steps see **INSTALL.md**, and for going live see **DEPLOY.md**.
