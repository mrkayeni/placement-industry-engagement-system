
"""
Placement and Industry Engagement Management System
Phase 1 + Phase 2 + Phase 3 Core Application

Technology:
- Python 3
- Tkinter GUI
- SQLite database

How to run:
1. Save this file as placement_system_app.py
2. Open it in Spyder or any Python IDE
3. Run the file
4. Use one of the sample logins below

Sample login details:
Student:
    username: student1
    password: password

Academic Supervisor:
    username: supervisor1
    password: password

Placement Team:
    username: placement1
    password: password

Industry Partner:
    username: partner1
    password: password
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


DATABASE_NAME = "placement_system.db"


class Database:
    def __init__(self, db_name=DATABASE_NAME):
        self.db_name = db_name
        self.create_tables()
        self.seed_data()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS placements (
            placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            skills_required TEXT NOT NULL,
            description TEXT NOT NULL,
            deadline TEXT NOT NULL,
            posted_by INTEGER,
            status TEXT DEFAULT 'Open',
            FOREIGN KEY(posted_by) REFERENCES users(user_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            placement_id INTEGER NOT NULL,
            cv_path TEXT,
            cover_note TEXT,
            status TEXT DEFAULT 'Submitted',
            date_submitted TEXT NOT NULL,
            decision_note TEXT,
            FOREIGN KEY(student_id) REFERENCES users(user_id),
            FOREIGN KEY(placement_id) REFERENCES placements(placement_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS progress_records (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            milestone TEXT NOT NULL,
            progress_note TEXT NOT NULL,
            progress_status TEXT NOT NULL,
            date_added TEXT NOT NULL,
            added_by INTEGER,
            FOREIGN KEY(application_id) REFERENCES applications(application_id),
            FOREIGN KEY(added_by) REFERENCES users(user_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            given_by INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            date_added TEXT NOT NULL,
            FOREIGN KEY(application_id) REFERENCES applications(application_id),
            FOREIGN KEY(given_by) REFERENCES users(user_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            date_created TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)

        conn.commit()
        conn.close()

    def seed_data(self):
        conn = self.connect()
        cur = conn.cursor()

        users = [
            ("student1", "password", "John Smith", "Student", "john.smith@student.bcu.ac.uk"),
            ("supervisor1", "password", "Dr Amina Hassan", "Academic Supervisor", "amina.hassan@bcu.ac.uk"),
            ("placement1", "password", "Placement Officer", "Placement Team", "placement@bcu.ac.uk"),
            ("partner1", "password", "Tech Solutions Ltd", "Industry Partner", "contact@techsolutions.co.uk"),
        ]

        for user in users:
            cur.execute("""
            INSERT OR IGNORE INTO users(username, password, full_name, role, email)
            VALUES (?, ?, ?, ?, ?)
            """, user)

        cur.execute("SELECT user_id FROM users WHERE username='partner1'")
        partner_id = cur.fetchone()[0]

        placements = [
            (
                "Software Engineering Intern",
                "Tech Solutions Ltd",
                "Birmingham",
                "Python, SQL, Problem Solving",
                "Support software development tasks, debugging, testing, and documentation.",
                "2026-07-30",
                partner_id,
                "Open"
            ),
            (
                "Data Analyst Placement",
                "Insight Analytics",
                "London",
                "Excel, SQL, Data Visualisation",
                "Analyse business data, prepare dashboards, and support reporting activities.",
                "2026-08-15",
                partner_id,
                "Open"
            ),
            (
                "Web Development Intern",
                "Creative Web Agency",
                "Remote",
                "HTML, CSS, JavaScript, Basic Python",
                "Assist with website development, content updates, and user interface testing.",
                "2026-09-01",
                partner_id,
                "Open"
            )
        ]

        for placement in placements:
            cur.execute("""
            INSERT INTO placements(title, company, location, skills_required, description, deadline, posted_by, status)
            SELECT ?, ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM placements WHERE title=? AND company=?
            )
            """, placement + (placement[0], placement[1]))

        conn.commit()
        conn.close()

    def authenticate(self, username, password):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
        SELECT user_id, username, full_name, role, email
        FROM users
        WHERE username=? AND password=?
        """, (username, password))
        user = cur.fetchone()
        conn.close()
        return user

    def fetch_all(self, query, params=()):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def execute(self, query, params=()):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        last_id = cur.lastrowid
        conn.close()
        return last_id

    def notify_user(self, user_id, message):
        self.execute("""
        INSERT INTO notifications(user_id, message, date_created)
        VALUES (?, ?, ?)
        """, (user_id, message, datetime.now().strftime("%Y-%m-%d %H:%M")))


class PlacementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Placement and Industry Engagement Management System")
        self.root.geometry("1200x720")
        self.root.minsize(1000, 650)

        self.db = Database()
        self.current_user = None

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.show_login()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()

        container = ttk.Frame(self.root, padding=30)
        container.pack(expand=True, fill="both")

        title = ttk.Label(
            container,
            text="Placement and Industry Engagement Management System",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=20)

        subtitle = ttk.Label(
            container,
            text="Connecting Talent with Opportunity",
            font=("Arial", 14)
        )
        subtitle.pack(pady=5)

        login_frame = ttk.LabelFrame(container, text="Login", padding=25)
        login_frame.pack(pady=30)

        ttk.Label(login_frame, text="Username").grid(row=0, column=0, sticky="w", pady=8)
        self.username_entry = ttk.Entry(login_frame, width=35)
        self.username_entry.grid(row=0, column=1, pady=8)

        ttk.Label(login_frame, text="Password").grid(row=1, column=0, sticky="w", pady=8)
        self.password_entry = ttk.Entry(login_frame, width=35, show="*")
        self.password_entry.grid(row=1, column=1, pady=8)

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=15)

        sample = (
            "Sample Accounts\n"
            "Student: student1 / password\n"
            "Supervisor: supervisor1 / password\n"
            "Placement Team: placement1 / password\n"
            "Industry Partner: partner1 / password"
        )
        ttk.Label(container, text=sample, justify="center").pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Details", "Please enter username and password.")
            return

        user = self.db.authenticate(username, password)
        if user:
            self.current_user = {
                "user_id": user[0],
                "username": user[1],
                "full_name": user[2],
                "role": user[3],
                "email": user[4]
            }
            messagebox.showinfo("Login Successful", f"Welcome {user[2]}")
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_dashboard(self):
        self.clear_window()

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        sidebar = ttk.Frame(main, width=230, padding=15)
        sidebar.pack(side="left", fill="y")

        content = ttk.Frame(main, padding=20)
        content.pack(side="right", fill="both", expand=True)

        ttk.Label(
            sidebar,
            text=self.current_user["full_name"],
            font=("Arial", 13, "bold"),
            wraplength=200
        ).pack(pady=(10, 5))

        ttk.Label(
            sidebar,
            text=self.current_user["role"],
            font=("Arial", 10)
        ).pack(pady=(0, 20))

        self.content = content

        role = self.current_user["role"]

        ttk.Button(sidebar, text="Dashboard Home", command=self.dashboard_home).pack(fill="x", pady=4)

        if role == "Student":
            ttk.Button(sidebar, text="View Placements", command=self.view_placements).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="My Applications", command=self.my_applications).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Upload CV / Documents", command=self.upload_documents).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Notifications", command=self.notifications).pack(fill="x", pady=4)

        elif role == "Placement Team":
            ttk.Button(sidebar, text="Manage Opportunities", command=self.manage_opportunities).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Review Applications", command=self.review_applications).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Reports", command=self.reports).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Notifications", command=self.notifications).pack(fill="x", pady=4)

        elif role == "Academic Supervisor":
            ttk.Button(sidebar, text="Monitor Progress", command=self.monitor_progress).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Provide Feedback", command=self.provide_feedback).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Reports", command=self.reports).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Notifications", command=self.notifications).pack(fill="x", pady=4)

        elif role == "Industry Partner":
            ttk.Button(sidebar, text="Post Opportunity", command=self.manage_opportunities).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Review Applications", command=self.review_applications).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Provide Feedback", command=self.provide_feedback).pack(fill="x", pady=4)
            ttk.Button(sidebar, text="Notifications", command=self.notifications).pack(fill="x", pady=4)

        ttk.Separator(sidebar).pack(fill="x", pady=15)
        ttk.Button(sidebar, text="Logout", command=self.show_login).pack(fill="x", pady=4)

        self.dashboard_home()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def dashboard_home(self):
        self.clear_content()

        ttk.Label(
            self.content,
            text=f"{self.current_user['role']} Dashboard",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=10)

        ttk.Label(
            self.content,
            text="Welcome to the Placement and Industry Engagement Management System.",
            font=("Arial", 12)
        ).pack(anchor="w", pady=5)

        stats_frame = ttk.Frame(self.content)
        stats_frame.pack(fill="x", pady=20)

        total_placements = self.db.fetch_all("SELECT COUNT(*) FROM placements")[0][0]
        total_apps = self.db.fetch_all("SELECT COUNT(*) FROM applications")[0][0]
        total_open = self.db.fetch_all("SELECT COUNT(*) FROM placements WHERE status='Open'")[0][0]

        self.stat_card(stats_frame, "Total Placements", total_placements, 0)
        self.stat_card(stats_frame, "Total Applications", total_apps, 1)
        self.stat_card(stats_frame, "Open Opportunities", total_open, 2)

        ttk.Label(
            self.content,
            text="Use the menu on the left to access your role-specific functions.",
            font=("Arial", 11)
        ).pack(anchor="w", pady=10)

    def stat_card(self, parent, label, value, column):
        frame = ttk.LabelFrame(parent, text=label, padding=20)
        frame.grid(row=0, column=column, padx=10, sticky="nsew")
        ttk.Label(frame, text=str(value), font=("Arial", 24, "bold")).pack()
        parent.columnconfigure(column, weight=1)

    def create_tree(self, parent, columns, headings):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=130)
        tree.pack(fill="both", expand=True, pady=10)
        return tree

    def view_placements(self):
        self.clear_content()
        ttk.Label(self.content, text="Available Placement Opportunities", font=("Arial", 18, "bold")).pack(anchor="w")

        columns = ("ID", "Title", "Company", "Location", "Skills", "Deadline", "Status")
        tree = self.create_tree(self.content, columns, columns)

        placements = self.db.fetch_all("""
        SELECT placement_id, title, company, location, skills_required, deadline, status
        FROM placements
        WHERE status='Open'
        """)

        for row in placements:
            tree.insert("", "end", values=row)

        form = ttk.LabelFrame(self.content, text="Apply for Selected Placement", padding=15)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Cover Note").grid(row=0, column=0, sticky="nw", pady=5)
        cover_text = tk.Text(form, height=4, width=80)
        cover_text.grid(row=0, column=1, pady=5)

        cv_path_var = tk.StringVar()

        def choose_cv():
            path = filedialog.askopenfilename(title="Select CV or Document")
            if path:
                cv_path_var.set(path)

        ttk.Button(form, text="Choose CV / Document", command=choose_cv).grid(row=1, column=0, pady=5)
        ttk.Entry(form, textvariable=cv_path_var, width=80).grid(row=1, column=1, pady=5)

        def apply():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a placement first.")
                return

            values = tree.item(selected, "values")
            placement_id = values[0]
            cover_note = cover_text.get("1.0", "end").strip()
            cv_path = cv_path_var.get().strip()

            existing = self.db.fetch_all("""
            SELECT application_id FROM applications
            WHERE student_id=? AND placement_id=?
            """, (self.current_user["user_id"], placement_id))

            if existing:
                messagebox.showwarning("Already Applied", "You have already applied for this placement.")
                return

            self.db.execute("""
            INSERT INTO applications(student_id, placement_id, cv_path, cover_note, status, date_submitted)
            VALUES (?, ?, ?, ?, 'Submitted', ?)
            """, (
                self.current_user["user_id"],
                placement_id,
                cv_path,
                cover_note,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            self.db.notify_user(self.current_user["user_id"], "Your placement application has been submitted successfully.")
            messagebox.showinfo("Application Submitted", "Your application has been submitted successfully.")

        ttk.Button(form, text="Submit Application", command=apply).grid(row=2, column=1, sticky="e", pady=10)

    def my_applications(self):
        self.clear_content()
        ttk.Label(self.content, text="My Applications", font=("Arial", 18, "bold")).pack(anchor="w")

        columns = ("App ID", "Placement", "Company", "Date", "Status", "Decision Note")
        tree = self.create_tree(self.content, columns, columns)

        rows = self.db.fetch_all("""
        SELECT a.application_id, p.title, p.company, a.date_submitted, a.status, IFNULL(a.decision_note, '')
        FROM applications a
        JOIN placements p ON a.placement_id = p.placement_id
        WHERE a.student_id=?
        ORDER BY a.application_id DESC
        """, (self.current_user["user_id"],))

        for row in rows:
            tree.insert("", "end", values=row)

    def upload_documents(self):
        self.clear_content()
        ttk.Label(self.content, text="Upload CV / Documents", font=("Arial", 18, "bold")).pack(anchor="w")

        apps = self.db.fetch_all("""
        SELECT a.application_id, p.title, p.company, IFNULL(a.cv_path, '')
        FROM applications a
        JOIN placements p ON a.placement_id = p.placement_id
        WHERE a.student_id=?
        """, (self.current_user["user_id"],))

        columns = ("App ID", "Placement", "Company", "Current Document")
        tree = self.create_tree(self.content, columns, columns)

        for row in apps:
            tree.insert("", "end", values=row)

        def upload():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select an application first.")
                return

            app_id = tree.item(selected, "values")[0]
            path = filedialog.askopenfilename(title="Select CV / Document")
            if path:
                self.db.execute("UPDATE applications SET cv_path=? WHERE application_id=?", (path, app_id))
                messagebox.showinfo("Document Uploaded", "Document path has been saved successfully.")
                self.upload_documents()

        ttk.Button(self.content, text="Upload / Replace Document", command=upload).pack(anchor="e", pady=10)

    def manage_opportunities(self):
        self.clear_content()
        ttk.Label(self.content, text="Manage Placement Opportunities", font=("Arial", 18, "bold")).pack(anchor="w")

        columns = ("ID", "Title", "Company", "Location", "Skills", "Deadline", "Status")
        tree = self.create_tree(self.content, columns, columns)

        rows = self.db.fetch_all("""
        SELECT placement_id, title, company, location, skills_required, deadline, status
        FROM placements
        ORDER BY placement_id DESC
        """)

        for row in rows:
            tree.insert("", "end", values=row)

        form = ttk.LabelFrame(self.content, text="Create / Update Opportunity", padding=15)
        form.pack(fill="x", pady=10)

        title_var = tk.StringVar()
        company_var = tk.StringVar()
        location_var = tk.StringVar()
        skills_var = tk.StringVar()
        deadline_var = tk.StringVar()
        status_var = tk.StringVar(value="Open")

        fields = [
            ("Title", title_var),
            ("Company", company_var),
            ("Location", location_var),
            ("Skills Required", skills_var),
            ("Deadline YYYY-MM-DD", deadline_var),
            ("Status", status_var),
        ]

        for i, (label, var) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=var, width=60).grid(row=i, column=1, pady=3)

        ttk.Label(form, text="Description").grid(row=6, column=0, sticky="nw", pady=3)
        desc_text = tk.Text(form, width=60, height=4)
        desc_text.grid(row=6, column=1, pady=3)

        def load_selected():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select a placement first.")
                return

            values = tree.item(selected, "values")
            placement_id = values[0]
            row = self.db.fetch_all("""
            SELECT title, company, location, skills_required, description, deadline, status
            FROM placements WHERE placement_id=?
            """, (placement_id,))[0]

            title_var.set(row[0])
            company_var.set(row[1])
            location_var.set(row[2])
            skills_var.set(row[3])
            desc_text.delete("1.0", "end")
            desc_text.insert("1.0", row[4])
            deadline_var.set(row[5])
            status_var.set(row[6])

        def save_new():
            if not title_var.get().strip() or not company_var.get().strip():
                messagebox.showwarning("Missing Details", "Title and company are required.")
                return

            self.db.execute("""
            INSERT INTO placements(title, company, location, skills_required, description, deadline, posted_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title_var.get().strip(),
                company_var.get().strip(),
                location_var.get().strip(),
                skills_var.get().strip(),
                desc_text.get("1.0", "end").strip(),
                deadline_var.get().strip(),
                self.current_user["user_id"],
                status_var.get().strip() or "Open"
            ))
            messagebox.showinfo("Saved", "Placement opportunity created successfully.")
            self.manage_opportunities()

        def update_selected():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select a placement first.")
                return

            placement_id = tree.item(selected, "values")[0]
            self.db.execute("""
            UPDATE placements
            SET title=?, company=?, location=?, skills_required=?, description=?, deadline=?, status=?
            WHERE placement_id=?
            """, (
                title_var.get().strip(),
                company_var.get().strip(),
                location_var.get().strip(),
                skills_var.get().strip(),
                desc_text.get("1.0", "end").strip(),
                deadline_var.get().strip(),
                status_var.get().strip(),
                placement_id
            ))
            messagebox.showinfo("Updated", "Placement opportunity updated successfully.")
            self.manage_opportunities()

        def close_selected():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select a placement first.")
                return

            placement_id = tree.item(selected, "values")[0]
            self.db.execute("UPDATE placements SET status='Closed' WHERE placement_id=?", (placement_id,))
            messagebox.showinfo("Closed", "Placement opportunity has been closed.")
            self.manage_opportunities()

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=7, column=1, sticky="e", pady=10)

        ttk.Button(btn_frame, text="Load Selected", command=load_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Save New", command=save_new).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Update Selected", command=update_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Close Selected", command=close_selected).pack(side="left", padx=4)

    def review_applications(self):
        self.clear_content()
        ttk.Label(self.content, text="Review Applications", font=("Arial", 18, "bold")).pack(anchor="w")

        columns = ("App ID", "Student", "Placement", "Company", "Date", "Status", "CV Path")
        tree = self.create_tree(self.content, columns, columns)

        rows = self.db.fetch_all("""
        SELECT a.application_id, u.full_name, p.title, p.company, a.date_submitted, a.status, IFNULL(a.cv_path, '')
        FROM applications a
        JOIN users u ON a.student_id = u.user_id
        JOIN placements p ON a.placement_id = p.placement_id
        ORDER BY a.application_id DESC
        """)

        for row in rows:
            tree.insert("", "end", values=row)

        form = ttk.LabelFrame(self.content, text="Application Decision", padding=15)
        form.pack(fill="x", pady=10)

        decision_var = tk.StringVar(value="Approved")
        ttk.Label(form, text="Decision").grid(row=0, column=0, sticky="w")
        ttk.Combobox(form, textvariable=decision_var, values=["Approved", "Rejected", "Shortlisted", "Submitted"], width=30).grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="Decision Note").grid(row=1, column=0, sticky="nw", pady=5)
        note_text = tk.Text(form, width=80, height=4)
        note_text.grid(row=1, column=1, pady=5)

        def save_decision():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select an application first.")
                return

            values = tree.item(selected, "values")
            app_id = values[0]
            student_name = values[1]

            self.db.execute("""
            UPDATE applications
            SET status=?, decision_note=?
            WHERE application_id=?
            """, (decision_var.get(), note_text.get("1.0", "end").strip(), app_id))

            student_id = self.db.fetch_all("SELECT student_id FROM applications WHERE application_id=?", (app_id,))[0][0]
            self.db.notify_user(student_id, f"Your application status has been updated to: {decision_var.get()}.")

            messagebox.showinfo("Decision Saved", f"Application for {student_name} updated successfully.")
            self.review_applications()

        ttk.Button(form, text="Save Decision", command=save_decision).grid(row=2, column=1, sticky="e", pady=10)

    def monitor_progress(self):
        self.clear_content()
        ttk.Label(self.content, text="Monitor Placement Progress", font=("Arial", 18, "bold")).pack(anchor="w")

        columns = ("App ID", "Student", "Placement", "Application Status")
        tree = self.create_tree(self.content, columns, columns)

        rows = self.db.fetch_all("""
        SELECT a.application_id, u.full_name, p.title, a.status
        FROM applications a
        JOIN users u ON a.student_id = u.user_id
        JOIN placements p ON a.placement_id = p.placement_id
        WHERE a.status IN ('Approved', 'Shortlisted', 'Submitted')
        ORDER BY a.application_id DESC
        """)

        for row in rows:
            tree.insert("", "end", values=row)

        form = ttk.LabelFrame(self.content, text="Add Progress Record", padding=15)
        form.pack(fill="x", pady=10)

        milestone_var = tk.StringVar()
        status_var = tk.StringVar(value="On Track")

        ttk.Label(form, text="Milestone").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=milestone_var, width=60).grid(row=0, column=1, pady=3)

        ttk.Label(form, text="Progress Status").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Combobox(form, textvariable=status_var, values=["On Track", "Needs Support", "Completed", "Issue Detected"], width=30).grid(row=1, column=1, sticky="w", pady=3)

        ttk.Label(form, text="Progress Note").grid(row=2, column=0, sticky="nw", pady=3)
        note_text = tk.Text(form, width=80, height=4)
        note_text.grid(row=2, column=1, pady=3)

        def add_progress():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select an application first.")
                return

            app_id = tree.item(selected, "values")[0]

            self.db.execute("""
            INSERT INTO progress_records(application_id, milestone, progress_note, progress_status, date_added, added_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                app_id,
                milestone_var.get().strip(),
                note_text.get("1.0", "end").strip(),
                status_var.get(),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                self.current_user["user_id"]
            ))

            student_id = self.db.fetch_all("SELECT student_id FROM applications WHERE application_id=?", (app_id,))[0][0]
            self.db.notify_user(student_id, f"Progress update added: {status_var.get()}.")

            messagebox.showinfo("Progress Saved", "Progress record added successfully.")

        ttk.Button(form, text="Add Progress Record", command=add_progress).grid(row=3, column=1, sticky="e", pady=10)

        ttk.Label(self.content, text="Recent Progress Records", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 0))
        columns2 = ("ID", "App ID", "Milestone", "Status", "Date", "Note")
        progress_tree = self.create_tree(self.content, columns2, columns2)

        progress_rows = self.db.fetch_all("""
        SELECT progress_id, application_id, milestone, progress_status, date_added, progress_note
        FROM progress_records
        ORDER BY progress_id DESC
        LIMIT 10
        """)

        for row in progress_rows:
            progress_tree.insert("", "end", values=row)

    def provide_feedback(self):
        self.clear_content()
        ttk.Label(self.content, text="Provide Feedback", font=("Arial", 18, "bold")).pack(anchor="w")

        columns = ("App ID", "Student", "Placement", "Status")
        tree = self.create_tree(self.content, columns, columns)

        rows = self.db.fetch_all("""
        SELECT a.application_id, u.full_name, p.title, a.status
        FROM applications a
        JOIN users u ON a.student_id = u.user_id
        JOIN placements p ON a.placement_id = p.placement_id
        ORDER BY a.application_id DESC
        """)

        for row in rows:
            tree.insert("", "end", values=row)

        form = ttk.LabelFrame(self.content, text="Feedback Details", padding=15)
        form.pack(fill="x", pady=10)

        rating_var = tk.IntVar(value=5)

        ttk.Label(form, text="Rating 1-5").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(form, from_=1, to=5, textvariable=rating_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="Comment").grid(row=1, column=0, sticky="nw", pady=5)
        comment_text = tk.Text(form, width=80, height=5)
        comment_text.grid(row=1, column=1, pady=5)

        def save_feedback():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select an application first.")
                return

            app_id = tree.item(selected, "values")[0]
            comment = comment_text.get("1.0", "end").strip()

            if not comment:
                messagebox.showwarning("Missing Comment", "Please enter feedback comment.")
                return

            self.db.execute("""
            INSERT INTO feedback(application_id, given_by, rating, comment, date_added)
            VALUES (?, ?, ?, ?, ?)
            """, (
                app_id,
                self.current_user["user_id"],
                rating_var.get(),
                comment,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            student_id = self.db.fetch_all("SELECT student_id FROM applications WHERE application_id=?", (app_id,))[0][0]
            self.db.notify_user(student_id, "New feedback has been added to your placement record.")

            messagebox.showinfo("Feedback Saved", "Feedback has been saved successfully.")

        ttk.Button(form, text="Save Feedback", command=save_feedback).grid(row=2, column=1, sticky="e", pady=10)

    def reports(self):
        self.clear_content()
        ttk.Label(self.content, text="Reports and Analytics", font=("Arial", 18, "bold")).pack(anchor="w")

        report_text = tk.Text(self.content, height=25, width=120)
        report_text.pack(fill="both", expand=True, pady=10)

        total_students = self.db.fetch_all("SELECT COUNT(*) FROM users WHERE role='Student'")[0][0]
        total_placements = self.db.fetch_all("SELECT COUNT(*) FROM placements")[0][0]
        total_open = self.db.fetch_all("SELECT COUNT(*) FROM placements WHERE status='Open'")[0][0]
        total_apps = self.db.fetch_all("SELECT COUNT(*) FROM applications")[0][0]
        approved = self.db.fetch_all("SELECT COUNT(*) FROM applications WHERE status='Approved'")[0][0]
        rejected = self.db.fetch_all("SELECT COUNT(*) FROM applications WHERE status='Rejected'")[0][0]
        submitted = self.db.fetch_all("SELECT COUNT(*) FROM applications WHERE status='Submitted'")[0][0]

        company_rows = self.db.fetch_all("""
        SELECT company, COUNT(*) 
        FROM placements
        GROUP BY company
        ORDER BY COUNT(*) DESC
        """)

        status_rows = self.db.fetch_all("""
        SELECT status, COUNT(*)
        FROM applications
        GROUP BY status
        """)

        report = []
        report.append("PLACEMENT AND INDUSTRY ENGAGEMENT MANAGEMENT SYSTEM REPORT")
        report.append("=" * 70)
        report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        report.append("Summary")
        report.append("-" * 70)
        report.append(f"Total students: {total_students}")
        report.append(f"Total placement opportunities: {total_placements}")
        report.append(f"Open placement opportunities: {total_open}")
        report.append(f"Total applications: {total_apps}")
        report.append(f"Approved applications: {approved}")
        report.append(f"Rejected applications: {rejected}")
        report.append(f"Submitted applications awaiting review: {submitted}")
        report.append("")
        report.append("Placements by Company")
        report.append("-" * 70)

        for company, count in company_rows:
            report.append(f"{company}: {count}")

        report.append("")
        report.append("Applications by Status")
        report.append("-" * 70)

        for status, count in status_rows:
            report.append(f"{status}: {count}")

        report.append("")
        report.append("Interpretation")
        report.append("-" * 70)
        report.append(
            "This report helps the placement team monitor placement uptake, "
            "student applications, employer engagement, and application outcomes."
        )

        report_text.insert("1.0", "\n".join(report))
        report_text.config(state="disabled")

    def notifications(self):
        self.clear_content()
        ttk.Label(self.content, text="Notifications and Alerts", font=("Arial", 18, "bold")).pack(anchor="w")

        columns = ("ID", "Message", "Date", "Read")
        tree = self.create_tree(self.content, columns, columns)

        rows = self.db.fetch_all("""
        SELECT notification_id, message, date_created,
        CASE WHEN is_read=1 THEN 'Yes' ELSE 'No' END
        FROM notifications
        WHERE user_id=?
        ORDER BY notification_id DESC
        """, (self.current_user["user_id"],))

        for row in rows:
            tree.insert("", "end", values=row)

        def mark_read():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Select a notification first.")
                return

            notification_id = tree.item(selected, "values")[0]
            self.db.execute("UPDATE notifications SET is_read=1 WHERE notification_id=?", (notification_id,))
            messagebox.showinfo("Updated", "Notification marked as read.")
            self.notifications()

        ttk.Button(self.content, text="Mark Selected as Read", command=mark_read).pack(anchor="e", pady=10)


def main():
    root = tk.Tk()
    app = PlacementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
