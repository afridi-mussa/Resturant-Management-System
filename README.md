# BistroSaaS — Restaurant Management System

A full-stack **Restaurant Ordering & Management** web application built with
**Django**. Customers can browse a menu, place orders, and track them; admins
manage the menu, confirm orders, and oversee users. It also ships with a small
**REST API** for the menu.

> New here and just want to run the project on your laptop? See **[INSTALL.md](INSTALL.md)**.

---

## Table of Contents

1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Roles](#roles)
4. [Project Structure](#project-structure)
5. [Data Models](#data-models)
6. [URL / Route Reference](#url--route-reference)
7. [REST API](#rest-api)
8. [Key Workflows](#key-workflows)
9. [Configuration & Settings](#configuration--settings)
10. [Admin Panel Customizations](#admin-panel-customizations)
11. [Common Commands](#common-commands)
12. [Troubleshooting](#troubleshooting)

---

## Features

- **Authentication** — register, login, logout (Django auth).
- **Two roles** — **Customer** (default) and **Admin** (full superuser). Admin
  sign-up requires a secret key.
- **Menu browsing** — search by name/description, filter by category, and
  pagination (6 per page).
- **Menu management (CRUD)** — admins add/edit/delete dishes, including image
  uploads.
- **Ordering** — customers pick items via checkboxes with a live total, then
  submit an order.
- **Order confirmation flow** — admins update order status
  (Pending → Preparing → Completed / Cancelled); customers get an in-app
  notification badge when their order status changes.
- **User profile** — edit personal info (name, email, phone, address, profile
  picture) and change password.
- **REST API** — JSON endpoints for the menu (Django REST Framework).
- **Bootstrap 5 UI** — responsive, modern interface throughout.
- **Custom admin** — red "Cancel" button on all admin forms; admins cannot see
  or delete their own account.

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.x |
| Web framework | Django 6.0.5 |
| API | Django REST Framework 3.17.1 |
| Image handling | Pillow 12.2.0 |
| Database | SQLite (default, file-based) |
| Frontend | Django Templates + Bootstrap 5 (via CDN) + Bootstrap Icons |
| Auth | Django's built-in authentication system |

---

## Roles

| Role | Internal flag | What they can do |
|------|---------------|------------------|
| **Guest** | not logged in | Browse menu, view item details, read the API, register/login |
| **Customer** | `is_superuser = False` | Everything a guest can + place orders, view their order history, edit profile, change password |
| **Admin** | `is_superuser = True` | Everything + add/edit/delete menu items, manage & confirm orders, full `/admin/` panel |

**Becoming an Admin:** on the registration page choose **Role = Admin** and
enter the **Secret Key** (`admin123` by default, configurable in `settings.py`
via `ADMIN_SECRET_KEY`).

---

## Project Structure

```
Resturant-Management/
├── manage.py                  # Django command-line entry point
├── requirements.txt           # Python dependencies
├── db.sqlite3                 # The SQLite database (binary file)
├── README.md                  # This file
├── INSTALL.md                 # Setup guide for new users / group members
│
├── bistro_saas/               # Project configuration package
│   ├── settings.py            # All settings (apps, DB, media, auth, etc.)
│   ├── urls.py                # Root URL routing (admin + includes app urls)
│   ├── wsgi.py / asgi.py      # Server entry points
│
├── ordering/                  # The main application
│   ├── models.py              # Database tables (CustomerProfile, Category, MenuItem, Order)
│   ├── views.py               # Request handlers (FBVs + CBVs)
│   ├── forms.py               # Forms (register, menu item, profile, password)
│   ├── urls.py                # App URL routes + REST API router
│   ├── admin.py               # Admin site configuration
│   ├── serializers.py         # REST API serializer
│   ├── context_processors.py  # Navbar notification counts
│   ├── apps.py                # App config
│   ├── migrations/            # Auto-generated DB schema history
│   └── templates/ordering/    # HTML templates (extend base.html)
│
├── templates/                 # Project-level templates
│   └── admin/submit_line.html # Admin override (adds the Cancel button)
│
└── media/                     # User-uploaded files
    ├── menu_items/            # Menu dish images
    └── profile_pics/          # Profile pictures
```

---

## Data Models

All models live in `ordering/models.py`.

### CustomerProfile
Extra info per user. **One-to-One** with Django's `User`.

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOne(User) | deleted with the user |
| `phone` | CharField | optional |
| `address` | TextField | optional |
| `profile_pic` | ImageField | uploads to `media/profile_pics/` |

> Auto-created for every new user via a `post_save` **signal**.

### Category
A food category. **One-to-Many** with `MenuItem`.

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField | unique |
| `description` | TextField | optional |

### MenuItem
A dish. **Many-to-One** with `Category`.

| Field | Type | Notes |
|-------|------|-------|
| `category` | ForeignKey(Category) | the dish's category |
| `name` | CharField | |
| `description` | TextField | optional |
| `price` | DecimalField | money-safe |
| `image` | ImageField | uploads to `media/menu_items/` |
| `is_available` | BooleanField | hides item from menu when False |

### Order
A customer order. **Many-to-One** with `User`, **Many-to-Many** with `MenuItem`.

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey(User) | who ordered |
| `items` | ManyToMany(MenuItem) | ordered dishes |
| `created_at` | DateTimeField | set on creation |
| `total_amount` | DecimalField | computed server-side |
| `status` | CharField (choices) | Pending / Preparing / Completed / Cancelled |
| `unseen_update` | BooleanField | True when admin changed status (for notifications) |
| `updated_at` | DateTimeField | last modified |

### Relationship diagram

```
User 1───1 CustomerProfile
User 1───* Order *───* MenuItem *───1 Category
```

---

## URL / Route Reference

Base URL during development: **http://127.0.0.1:8000/**

| URL | Name | View | Access | Purpose |
|-----|------|------|--------|---------|
| `/` | `menu_list` | MenuListView | Public | Menu with search/filter/pagination |
| `/menu/<id>/` | `menu_item_detail` | MenuItemDetailView | Public | Dish detail |
| `/menu/add/` | `menu_item_add` | MenuItemCreateView | Admin | Add a dish |
| `/menu/<id>/edit/` | `menu_item_edit` | MenuItemUpdateView | Admin | Edit a dish |
| `/menu/<id>/delete/` | `menu_item_delete` | MenuItemDeleteView | Admin | Delete a dish |
| `/order/place/` | `place_order` | place_order | Customer | Place an order |
| `/my-orders/` | `my_orders` | OrderListView | Customer | Order history |
| `/manage/orders/` | `manage_orders` | ManageOrdersView | Admin | Manage all orders |
| `/manage/orders/<id>/status/` | `update_order_status` | update_order_status | Admin (POST) | Change an order's status |
| `/profile/` | `profile` | profile | Logged in | Edit personal info |
| `/profile/password/` | `change_password` | change_password | Logged in | Change password |
| `/register/` | `register` | register | Guest | Sign up |
| `/login/` | `login` | LoginView | Guest | Log in |
| `/logout/` | `logout` | LogoutView | Logged in | Log out (POST) |
| `/admin/` | — | Django admin | Admin | Full admin panel |
| `/api/menu/` | `api-menu-list` | MenuItemViewSet | Public read | Menu JSON API |

---

## REST API

Powered by Django REST Framework. The router auto-generates the routes.

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/menu/` | List all menu items | Anyone |
| GET | `/api/menu/<id>/` | Single menu item | Anyone |
| POST | `/api/menu/` | Create an item | Authenticated |
| PUT/PATCH | `/api/menu/<id>/` | Update an item | Authenticated |
| DELETE | `/api/menu/<id>/` | Delete an item | Authenticated |

- Visit `/api/menu/` in a browser to use DRF's **browsable API**.
- Append `?format=json` for raw JSON: `/api/menu/?format=json`.
- Each item includes a read-only `category_name` field for convenience.

Permissions use `IsAuthenticatedOrReadOnly` (read = everyone, write = logged in).

---

## Key Workflows

### Placing & confirming an order
1. A **customer** opens `/order/place/`, ticks items (live total updates), and submits.
2. An `Order` is created with status **Pending**.
3. An **admin** opens `/manage/orders/` and clicks **Confirm & Prepare**,
   **Mark Completed**, or **Cancel Order**.
4. The order's `unseen_update` flag is set to `True`.
5. The customer sees a **red badge** on the "My Orders" navbar link and a green
   highlight/banner on `/my-orders/`. Viewing the page clears the flag.

### Registering as Admin
1. Go to `/register/`, choose **Role = Admin**.
2. The **Secret Key** field appears — enter `admin123`.
3. On success the account is created as a Django superuser.

---

## Configuration & Settings

Key settings in `bistro_saas/settings.py`:

| Setting | Value | Meaning |
|---------|-------|---------|
| `DEBUG` | `True` | Development mode (turn off in production) |
| `DATABASES` | SQLite | `db.sqlite3` in the project root |
| `MEDIA_URL` / `MEDIA_ROOT` | `media/` | Where uploaded images live |
| `LOGIN_REDIRECT_URL` | `menu_list` | After login |
| `LOGOUT_REDIRECT_URL` | `login` | After logout |
| `ADMIN_SECRET_KEY` | `admin123` | Required to register as Admin |
| `MESSAGE_TAGS` | ERROR → `danger` | Makes error flash messages red in Bootstrap |

> **Security note:** `SECRET_KEY`, `DEBUG=True`, and the hard-coded
> `ADMIN_SECRET_KEY` are fine for a class project/demo but should be changed and
> moved to environment variables for any real deployment.

---

## Admin Panel Customizations

Configured in `ordering/admin.py` and `templates/admin/submit_line.html`:

- **All models registered**: Users, Customer Profiles, Categories, Menu Items, Orders.
- **Cancel button**: every admin add/edit form has a red **Cancel** button that
  returns to the list without saving.
- **Self-protection**: a logged-in admin **cannot see or delete their own
  account** in the Users list.
- **Useful list tools**: search boxes, status/category filters, inline editing
  of menu price/availability, and a date drill-down for orders.

---

## Common Commands

Run these from the project root with your virtual environment activated.

```bash
# Start the development server
python manage.py runserver

# Apply database schema changes
python manage.py makemigrations
python manage.py migrate

# Create an admin via the command line (alternative to the secret-key signup)
python manage.py createsuperuser

# Open an interactive Python shell with Django loaded
python manage.py shell

# Check the project for problems
python manage.py check
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `db.sqlite3` won't open as text | It's a **binary** database file — use `/admin/`, the Django shell, or a SQLite viewer. |
| Images don't display | Ensure `DEBUG=True` (dev) and that **Pillow** is installed. |
| `NoReverseMatch` errors | A `{% url 'name' %}` references a route that doesn't exist — check `ordering/urls.py`. |
| Can't register as Admin | Secret key must be exactly `admin123` (or whatever `ADMIN_SECRET_KEY` is set to). |
| "Invalid HTTP_HOST" | Add the host to `ALLOWED_HOSTS` in `settings.py`. |

---

Built as a learning project demonstrating Django models, class-based views,
authentication, file uploads, the Django admin, and a REST API.
