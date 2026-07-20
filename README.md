# Smart Attendance Dashboard (Flask + MySQL)

A web-based **Smart Attendance System** for college management, built using **Python Flask**, **MySQL**, and **HTML/CSS**.  
It allows staff to log in, manage students and courses, mark attendance, view attendance reports, and send email reminders to students with low attendance.

---

## 1. Features

- **College Management Login**
  - Secure login page for staff (admin / HOD) using a `users` table in MySQL.
  - Session-based authentication in Flask (only logged-in users can access the dashboard pages).

- **Dashboard**
  - Central dashboard at `/` with cards for:
    - Students
    - Mark Attendance
    - Attendance Report
  - Shows quick overview metrics (total students, total courses, reminder threshold).

- **Students Management (Read-only in this version)**
  - `students` table in MySQL stores:
    - Roll number
    - Full name
    - Email
    - Department
    - Year of study
  - Students list page at `/students` displays all students in a styled table.

- **Courses**
  - `courses` table in MySQL stores:
    - Course code
    - Course name
    - Faculty name
  - Used in dropdowns for marking attendance and viewing reports.

- **Attendance Recording**
  - `attendance` table stores:
    - `student_id` (foreign key to `students`)
    - `course_id` (foreign key to `courses`)
    - `attendance_date`
    - `status` (`Present` / `Absent`)
  - Mark Attendance page at `/attendance`:
    - Select course and date.
    - For each student, choose Present/Absent using radio buttons.
    - Data is saved to MySQL through Flask backend.

- **Attendance Report & Email Reminders**
  - Report page at `/report`:
    - Select a course to view:
      - Total classes
      - Present count
      - Attendance percentage per student
    - Low attendance (below threshold) highlighted with colored badges.
  - Email reminders:
    - Uses **Flask-Mail** + **Gmail SMTP**.
    - Sends reminder emails to students whose attendance is below a selected threshold (e.g., 75%).

---

## 2. Tech Stack

- **Backend:** Python 3.x, Flask
- **Database:** MySQL (MySQL Workbench)
- **Frontend:** HTML, CSS (custom styling, no CSS framework)
- **Email:** Flask-Mail with Gmail SMTP
- **Tools:** VS Code, Git, GitHub

---

## 3. Database Schema (MySQL)

### `students`

```sql
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department VARCHAR(50),
    year_of_study VARCHAR(20)
);
```

### `courses`

```sql
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL,
    faculty_name VARCHAR(100) NOT NULL
);
```

### `attendance`

```sql
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

### `users` (for college management login)

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff'
);
```

---

## 4. Sample Data

Example initial data used for the mini project:[web:155][web:59]

- **Students:** 8 M.Tech CSE students (MTCS001–MTCS008) with email, department = CSE, year (1st / 2nd).
- **Courses:** 4 courses:
  - CSE5101 – Machine Learning
  - CSE5102 – Advanced Computer Networks
  - CSE5103 – Deep Learning Techniques
  - CSE5104 – Full Stack Web Development
- **Attendance:** Multiple dates with Present/Absent for each student in each course to generate meaningful percentages in the report.

---

## 5. Flask App Structure

Main files:

- `app.py` – Flask application:
  - DB connection (`mysql.connector`)
  - Routes:
    - `/login` – college management login
    - `/logout` – clear session
    - `/` – dashboard (protected)
    - `/students` – students list (protected)
    - `/attendance` – mark attendance (GET/POST, protected)
    - `/report` – attendance report (GET/POST, protected)
    - `/send_reminders` – send email reminders (POST, protected)

- `templates/`
  - `base.html` – shared layout (header, navigation, styling).
  - `dashboard.html` – main dashboard with cards.
  - `students.html` – students list table.
  - `attendance.html` – mark attendance form inside a card.
  - `report.html` – report table with badges + email reminder form.
  - `login.html` – centered login card.

---

## 6. Email Configuration (Flask-Mail)

Configured in `app.py`:

```python
from flask_mail import Mail, Message

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "YOUR_EMAIL@gmail.com"
app.config["MAIL_PASSWORD"] = "YOUR_APP_PASSWORD"
app.config["MAIL_DEFAULT_SENDER"] = "YOUR_EMAIL@gmail.com"

mail = Mail(app)
```

> Note: For security, use a **Gmail App Password** instead of your normal password, and do not commit real credentials to GitHub.[web:24][web:26][web:31]

---

## 7. How to Run

1. **Clone the repository**

```bash
git clone https://github.com/<your-username>/smart_attendance_system.git
cd smart_attendance_system
```

2. **Create virtual environment (optional but recommended)**

```bash
python -m venv venv
source venv/Scripts/activate    # Windows PowerShell / CMD
```

3. **Install dependencies**

```bash
pip install flask flask-mail mysql-connector-python
```

4. **Create MySQL database and tables**

In MySQL Workbench:

```sql
CREATE DATABASE smart_attendance;
USE smart_attendance;

/* Run the CREATE TABLE scripts and INSERT sample data */
```

5. **Configure DB credentials in `app.py`**

```python
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "smart_attendance"
}
```

6. **Run the Flask app**

```bash
python app.py
```

Visit:

- `http://127.0.0.1:5000/login` – login  
- `http://127.0.0.1:5000/` – dashboard (after login)  

---

## 8. Future Enhancements

- Add **student login** to view personal attendance.
- Add **role-based access** (Admin, HOD, Faculty) with separate dashboards.[web:162][web:96]
- Implement **edit/add** forms for students and courses (CRUD).
- Integrate **Bootstrap** or a design system for more advanced UI.
- Export attendance reports to **CSV/PDF**.
- Add graph visualizations (bar/pie charts) for attendance analytics.

---

## 9. Project Use Cases

- Web development **mini project** for college courses.
- Demonstration of:
  - Flask routing and forms
  - MySQL integration
  - Session-based login
  - Admin dashboard
  - Email notifications for low attendance.[web:54][web:59]