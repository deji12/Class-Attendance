# 📝 Attendance Management System

This is a Django-based web application designed to simplify and secure student attendance tracking for universities and colleges. It supports geolocation, single-device restrictions, and admin/class representative dashboards for full attendance visibility.

---

## 🚀 Features

- Class representatives can initiate attendance sessions (max duration: **30 minutes**).
- Students can sign attendance only:
  - From a **single device** (IP tracking enforced)
  - If they are **within 100 meters** of the class rep (GPS-based)
- **No VPNs allowed** — location is verified using city and country data.
- Each student can sign **only once per session**.
- Admin and class reps can view:
  - Who signed each session
  - Overall summary (% attendance) per student per course
  - Downloadable summary as Excel
- Responsive user interface and mobile-friendly design.
- Secure authentication with password reset functionality.

---

## 🛠️ Built With

- **Python 3.11+**
- **Django 4+**
- **SQLite** (default, can be replaced with PostgreSQL/MySQL)
- **Bootstrap 5**
- **jQuery** (used for dynamic modal handling and geolocation logic)

---

## ⚙️ How to Run Locally

### 1. Clone the repository

```bash
git https://github.com/deji12/Class-Attendance.git
cd attendance-system
```

### 2. Create and activae virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up ```.env``` file
Create a ```.env``` file in the root directory past the following and fill the environment variables:

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=*,
STUDENT_LEVELS=100,200,300,400,500
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_SSL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

### 5. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (for admin dashboard)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

### 8. Access the app

- Visit the site: http://127.0.0.1:8000/

- Admin panel: http://127.0.0.1:8000/admin/

# 📧 Contact
For questions, suggestions, or contributions, feel free to reach out:

- Name: Ayodeji Adesola

- GitHub: @deji12

- Email: adesolaayodeji53@gmail.com