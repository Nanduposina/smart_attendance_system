from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "nanduposina@gmail.com"
app.config["MAIL_PASSWORD"] = "swky vmkn awwz lsax"
app.config["MAIL_DEFAULT_SENDER"] = "nanduposina@gmail.com"

mail = Mail(app)

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "Sweden@2003",
    "database": "smart_attendance"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT roll_no, full_name, email, department, year_of_study FROM students;")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("students.html", students=students)

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        course_id = request.form.get("course_id")
        attendance_date = request.form.get("attendance_date")

        cursor.execute("SELECT id FROM students;")
        student_ids = cursor.fetchall()

        for s in student_ids:
            sid = s["id"]
            status = request.form.get(f"status_{sid}")
            if status:
                cursor.execute(
                    "INSERT INTO attendance (student_id, course_id, attendance_date, status) VALUES (%s, %s, %s, %s)",
                    (sid, course_id, attendance_date, status)
                )

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("home"))

    cursor.execute("SELECT id, course_name FROM courses;")
    courses = cursor.fetchall()

    cursor.execute("SELECT id, roll_no, full_name FROM students;")
    students = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("attendance.html", courses=courses, students=students)

@app.route("/report", methods=["GET", "POST"])
def report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Load courses for dropdown
    cursor.execute("SELECT id, course_name FROM courses;")
    courses = cursor.fetchall()

    selected_course_id = None
    report_rows = []

    if request.method == "POST":
        selected_course_id = request.form.get("course_id")

        if selected_course_id:
            # Attendance summary per student for that course
            summary_query = """
                SELECT s.roll_no,
                       s.full_name,
                       COUNT(a.id) AS total_classes,
                       SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count
                FROM students s
                LEFT JOIN attendance a
                    ON s.id = a.student_id
                   AND a.course_id = %s
                GROUP BY s.id, s.roll_no, s.full_name
                ORDER BY s.roll_no;
            """
            cursor.execute(summary_query, (selected_course_id,))
            results = cursor.fetchall()

            # Calculate percentage
            for row in results:
                total = row["total_classes"]
                present = row["present_count"]
                if total > 0:
                    percentage = round((present / total) * 100, 2)
                else:
                    percentage = 0.0
                report_rows.append({
                    "roll_no": row["roll_no"],
                    "full_name": row["full_name"],
                    "total_classes": total,
                    "present_count": present,
                    "percentage": percentage
                })

    cursor.close()
    conn.close()

    return render_template(
        "report.html",
        courses=courses,
        selected_course_id=selected_course_id,
        report_rows=report_rows
    )

@app.route("/send_reminders", methods=["POST"])
def send_reminders():
    course_id = request.form.get("course_id")
    threshold = float(request.form.get("threshold", 75.0))  # default 75%

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get course name
    cursor.execute("SELECT course_name FROM courses WHERE id = %s", (course_id,))
    course_row = cursor.fetchone()
    course_name = course_row["course_name"] if course_row else "Selected Course"

    # Attendance summary + email for low attendance
    summary_query = """
        SELECT s.roll_no,
               s.full_name,
               s.email,
               COUNT(a.id) AS total_classes,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count
        FROM students s
        LEFT JOIN attendance a
            ON s.id = a.student_id
           AND a.course_id = %s
        GROUP BY s.id, s.roll_no, s.full_name, s.email
    """
    cursor.execute(summary_query, (course_id,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # Send emails to students below threshold
    for row in results:
        total = row["total_classes"]
        present = row["present_count"]
        if total == 0:
            continue
        percentage = (present / total) * 100

        if percentage < threshold:
            msg = Message(
                subject=f"Attendance Reminder for {course_name}",
                recipients=[row["email"]]
            )
            msg.body = (
                f"Dear {row['full_name']},\n\n"
                f"Your attendance in the course '{course_name}' is {percentage:.2f}% "
                f"({present} out of {total} classes).\n"
                f"Please attend upcoming classes regularly to improve your attendance.\n\n"
                f"Regards,\nSmart Attendance System"
            )
            mail.send(msg)

    return redirect(url_for("report"))

if __name__ == "__main__":
    app.run(debug=True)