from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=NA-5CG14964F6\\SQLEXPRESS;"
        "DATABASE=ValentinesGarageDB;"
        "Trusted_Connection=yes;"
    )

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "role" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("checkin"))

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        user = cursor.execute("""
            SELECT EmployeeID, Role
            FROM Employees
            WHERE FullName = ? AND Password = ?
        """, name, password).fetchone()

        conn.close()

        if user:
            session["user_id"] = user.EmployeeID
            session["role"] = user.Role
            flash("Login successful.", "success")
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# ---------------- TRUCK CHECK-IN ----------------
@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if "role" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        registration = request.form["registration"]
        model = request.form["model"]
        mileage = request.form["mileage"]
        condition = request.form["condition"]
        notes = request.form["notes"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Trucks
            (RegistrationNumber, Model, Mileage, ConditionReport, Notes)
            VALUES (?, ?, ?, ?, ?)
        """, registration, model, mileage, condition, notes)
        conn.commit()
        conn.close()

        return redirect(url_for("tasks"))
    return render_template("checkin.html")
# ---------------- REPAIR TASKS ----------------
@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if "role" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        truck_id = request.form["truck_id"]
        description = request.form["description"]
        employee_id = request.form["employee_id"]
        task_notes = request.form["task_notes"]

        cursor.execute("""
            INSERT INTO RepairTasks (TruckID, Description, EmployeeID, TaskNotes)
            VALUES (?, ?, ?, ?)
        """, truck_id, description, employee_id, task_notes)

        conn.commit()

    trucks = cursor.execute(
        "SELECT TruckID, RegistrationNumber FROM Trucks"
    ).fetchall()

    employees = cursor.execute(
        "SELECT EmployeeID, FullName FROM Employees WHERE Role='Mechanic'"
    ).fetchall()

    tasks = cursor.execute("""
        SELECT
            R.TaskID,
            T.RegistrationNumber,
            R.Description,
            R.TaskNotes,
            R.Status,
            E.FullName
        FROM RepairTasks R
        JOIN Trucks T ON R.TruckID = T.TruckID
        JOIN Employees E ON R.EmployeeID = E.EmployeeID
    """).fetchall()

    conn.close()

    return render_template(
        "tasks.html",
        trucks=trucks,
        employees=employees,
        tasks=tasks
    )
# ---------------- COMPLETE TASK ----------------
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE RepairTasks
        SET Status = 'Completed'
        WHERE TaskID = ?
    """, task_id)

    conn.commit()
    conn.close()

    flash("Task marked as completed.", "success")
    return redirect(url_for("tasks"))

# ---------------- REPORTS (MANAGER ONLY) ----------------
@app.route("/reports")
def reports():
    if session.get("role") != "Manager":
        return redirect(url_for("tasks"))

    conn = get_db_connection()
    cursor = conn.cursor()

    report_data = cursor.execute("""
        SELECT
            Trucks.RegistrationNumber,
            Trucks.Model,
            Trucks.Mileage,
            Trucks.ConditionReport,
            Employees.FullName,
            RepairTasks.Description,
            RepairTasks.TaskNotes,
            RepairTasks.Status
        FROM RepairTasks
        JOIN Trucks ON RepairTasks.TruckID = Trucks.TruckID
        JOIN Employees ON RepairTasks.EmployeeID = Employees.EmployeeID
        ORDER BY Trucks.CheckInDate DESC
    """).fetchall()

    conn.close()

    return render_template("reports.html", report_data=report_data)

# ---------------- USER MANAGEMENT (MANAGER ONLY) ----------------
@app.route("/users", methods=["GET", "POST"])
def manage_users():
    if session.get("role") != "Manager":
        return redirect(url_for("tasks"))

    error = request.args.get("error")

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        password = request.form["password"]

        cursor.execute("""
            INSERT INTO Employees (FullName, Role, Password)
            VALUES (?, ?, ?)
        """, name, role, password)

        conn.commit()
        flash("User added successfully.", "success")

    users = cursor.execute("""
        SELECT EmployeeID, FullName, Role FROM Employees
    """).fetchall()

    conn.close()

    return render_template("users.html", users=users, error=error)

# ---------------- DELETE USER ----------------
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if session.get("role") != "Manager":
        return redirect(url_for("tasks"))

    if session.get("user_id") == user_id:
        return redirect(url_for("manage_users", error="You cannot delete your own account."))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Employees WHERE EmployeeID = ?", user_id)
    conn.commit()
    conn.close()

    flash("User deleted.", "success")
    return redirect(url_for("manage_users"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
