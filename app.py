# app.py
import os
import json
import random
from datetime import datetime
from pathlib import Path
import pickle
import re
from difflib import SequenceMatcher



# --- AI model (optional). If missing, we fallback gracefully ---
MODEL_PATH = "ai_model.pkl"
try:
    with open(MODEL_PATH, "rb") as f:
        AI_MODEL = pickle.load(f)
except Exception:
    AI_MODEL = None



def _extract_features_for_model(code: str, program_output: str, expected_output: str):
    """
    Example feature vector. Keep it consistent with what your ai_model.pkl expects.
    If you trained with a different set, adjust here accordingly.
    """
    code = code or ""
    program_output = (program_output or "").strip()
    expected_output = (expected_output or "").strip()

    # Output similarity (0..1)
    sim = SequenceMatcher(None, program_output, expected_output).ratio()

    # Basic code stats
    lines = code.splitlines()
    line_count = len(lines)
    avg_line_len = (sum(len(l) for l in lines) / max(1, line_count))

    # Comment ratio
    comment_lines = [l for l in lines if l.strip().startswith(("#", "//", "/*", "*"))]
    comment_ratio = len(comment_lines) / max(1, line_count)

    # Simple keyword density
    tokens = re.findall(r'\b(if|for|while|def|class|return|try|catch|public|static|void|int|float|String)\b', code)
    keyword_ratio = len(tokens) / max(1, len(code.split()))

    # Runtime error flag (based on output text)
    has_error = 1.0 if "error" in program_output.lower() or "exception" in program_output.lower() else 0.0

    # Example 5-D feature vector (adjust to your trained model)
    return [[sim, keyword_ratio, comment_ratio, avg_line_len, has_error]]


def _predict_ai_score_0_to_10(code: str, program_output: str, expected_output: str) -> float:
    """
    Returns a 0..10 float. Uses ai_model.pkl if available, else a heuristic fallback.
    """
    # If we have a model, use it
    if AI_MODEL is not None:
        try:
            feats = _extract_features_for_model(code, program_output, expected_output)
            pred = float(AI_MODEL.predict(feats)[0])
            return round(max(0.0, min(10.0, pred)), 1)
        except Exception:
            pass  # fall through to heuristic

    # Fallback: similarity → score, minus error penalty
    program_output = (program_output or "").strip()
    expected_output = (expected_output or "").strip()
    sim = SequenceMatcher(None, program_output, expected_output).ratio()
    penalty = 2.0 if ("error" in program_output.lower() or "exception" in program_output.lower()) else 0.0
    score = sim * 10.0 - penalty
    return round(max(0.0, min(10.0, score)), 1)


from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, abort, session
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)

import pymysql
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ------------------------------------------------------
# App & Config
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "ai_test_evaluator")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# JDoodle — for reliability, keep your current keys but prefer env override
JDOODLE_CLIENT_ID = os.getenv("JDOODLE_CLIENT_ID", "684ce1e4c51b165d92994051f14829b0")
JDOODLE_CLIENT_SECRET = os.getenv("JDOODLE_CLIENT_SECRET", "9f70c2f6306608238a093959eb83e2874acd0e377668f829c64b6ea384886ae8")

UPLOAD_PROBLEMS_DIR = BASE_DIR / "static" / "uploads" / "problems"
UPLOAD_PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------
# DB helpers
# ------------------------------------------------------
def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )

def fetch_one(q, p=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, p)
            return cur.fetchone()
    finally:
        conn.close()

def fetch_all(q, p=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, p)
            return cur.fetchall()
    finally:
        conn.close()

def execute(q, p=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, p)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_returning_id(q, p=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, p)
            new_id = cur.lastrowid
        conn.commit()
        return new_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def log_action(user_id, role, action):
    try:
        execute(
            "INSERT INTO activity_logs (user_id, role, action, created_at) VALUES (%s,%s,%s,NOW())",
            (user_id, role, action),
        )
    except Exception:
        pass

# ------------------------------------------------------
# Auth
# ------------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = "index"

class User(UserMixin):
    def __init__(self, id, email, name, role):
        self.id = str(id)
        self.email = email
        self.name = name
        self.role = role

@login_manager.user_loader
def load_user(user_id: str):
    role = session.get('auth_role')
    if not role:
        return None
    try:
        if role == 'admin':
            row = fetch_one("SELECT id, email, name FROM admins WHERE id=%s", (user_id,))
            if row: return User(row["id"], row["email"], row.get("name") or "Admin", "admin")
        elif role == 'teacher':
            row = fetch_one("SELECT id, email, name FROM teachers WHERE id=%s", (user_id,))
            if row: return User(row["id"], row["email"], row.get("name") or "Teacher", "teacher")
        elif role == 'student':
            row = fetch_one("SELECT id, email, name FROM students WHERE id=%s", (user_id,))
            if row: return User(row["id"], row["email"], row.get("name") or "Student", "student")
    except Exception:
        pass
    return None

@app.context_processor
def inject_now():
    return {"now": datetime.now}

# ------------------------------------------------------
# Core routes
# ------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

# ------------------------------------------------------
# Admin
# ------------------------------------------------------
@app.route("/admin/login", endpoint="admin.admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            row = fetch_one("SELECT id, email, name, password FROM admins WHERE email=%s", (email,))
            if row and (check_password_hash(row["password"], password) or row["password"] == password):
                user = User(row["id"], row["email"], row.get("name") or "Admin", "admin")
                session['auth_role'] = 'admin'
                login_user(user)
                log_action(user.id, 'admin', 'Logged in to admin dashboard')
                flash("Welcome, Admin!", "success")
                return redirect(url_for("admin.dashboard"))
        except Exception:
            flash("Login error (admin).", "danger")
        flash("Invalid credentials.", "danger")
    return render_template("admin_login.html")

@app.route("/admin/dashboard", endpoint="admin.dashboard")
@login_required
def admin_dashboard():
    if getattr(current_user, "role", "") != "admin":
        abort(403)
    stats = {"teachers": 0, "students": 0, "exams": 0, "submissions": 0}
    try:
        stats["teachers"] = fetch_one("SELECT COUNT(*) c FROM teachers")["c"]
        stats["students"] = fetch_one("SELECT COUNT(*) c FROM students")["c"]
        stats["exams"] = fetch_one("SELECT COUNT(*) c FROM exams")["c"]
        stats["submissions"] = fetch_one("SELECT COUNT(*) c FROM submissions")["c"]
    except Exception:
        pass
    return render_template("admin_dashboard.html", stats=stats)

# ------------------------------------------------------
# Auth: Student / Teacher
# ------------------------------------------------------
@app.route("/auth/login/student", endpoint="auth.login_student", methods=["GET", "POST"])
def login_student():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            row = fetch_one("SELECT id, email, name, password FROM students WHERE email=%s", (email,))
            if row and (check_password_hash(row["password"], password) or row["password"] == password):
                user = User(row["id"], row["email"], row.get("name") or "Student", "student")
                session['auth_role'] = 'student'
                login_user(user)
                log_action(user.id, 'student', 'Logged in')
                flash("Logged in as student.", "success")
                return redirect(url_for("student.dashboard"))
        except Exception:
            flash("Login error (student).", "danger")
        flash("Invalid credentials.", "danger")
    return render_template("student_login.html")

@app.route("/auth/register/student", endpoint="auth.register_student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            execute(
                "INSERT INTO students(name, email, password, created_at) VALUES(%s,%s,%s,NOW())",
                (name, email, generate_password_hash(password)),
            )
            flash("Student registered. Please login.", "success")
            return redirect(url_for("auth.login_student"))
        except Exception as ex:
            flash(f"Registration error (student): {ex}", "danger")
    return render_template("student_register.html")

@app.route("/auth/login/teacher", endpoint="auth.login_teacher", methods=["GET", "POST"])
def login_teacher():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            row = fetch_one("SELECT id, email, name, password FROM teachers WHERE email=%s", (email,))
            if row and (check_password_hash(row["password"], password) or row["password"] == password):
                user = User(row["id"], row["email"], row.get("name") or "Teacher", "teacher")
                session['auth_role'] = 'teacher'
                login_user(user)
                log_action(user.id, 'teacher', 'Logged in')
                flash("Logged in as teacher.", "success")
                return redirect(url_for("teacher.dashboard"))
        except Exception:
            flash("Login error (teacher).", "danger")
        flash("Invalid credentials.", "danger")
    return render_template("teacher_login.html")

@app.route("/auth/register/teacher", endpoint="auth.register_teacher", methods=["GET", "POST"])
def register_teacher():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            execute(
                "INSERT INTO teachers(name, email, password, created_at) VALUES(%s,%s,%s,NOW())",
                (name, email, generate_password_hash(password)),
            )
            flash("Teacher registered. Please login.", "success")
            return redirect(url_for("auth.login_teacher"))
        except Exception as ex:
            flash(f"Registration error (teacher): {ex}", "danger")
    return render_template("teacher_register.html")

@app.route("/logout")
@login_required
def logout():
    role = getattr(current_user, "role", "")
    session.pop('auth_role', None)
    logout_user()
    if role:
        flash("Logged out.", "info")
    return redirect(url_for("index"))

# ------------------------------------------------------
# Teacher Area
# ------------------------------------------------------
@app.route("/teacher/dashboard", endpoint="teacher.dashboard")
@login_required
def teacher_dashboard():
    if getattr(current_user, "role", "") != "teacher":
        abort(403)
    try:
        exams = fetch_all(
            """
            SELECT e.id, e.title, e.description, e.exam_date, e.duration, e.created_at,
                   COALESCE(SUM(CASE WHEN s.status='submitted' THEN 1 ELSE 0 END),0) AS submitted_count,
                   COALESCE(COUNT(a.student_id),0) AS assigned_count
            FROM exams e
            LEFT JOIN exam_assignments a ON a.exam_id = e.id
            LEFT JOIN submissions s ON s.exam_id = e.id
            WHERE e.created_by = %s
            GROUP BY e.id, e.title, e.description, e.exam_date, e.duration, e.created_at
            ORDER BY e.id DESC
            LIMIT 20
            """,
            (current_user.id,),
        )
    except Exception:
        exams = []
    return render_template("teacher_dashboard.html", exams=exams)

@app.route("/teacher/exams/create", endpoint="teacher.create_exam", methods=["GET", "POST"])
@login_required
def teacher_create_exam():
    if getattr(current_user, "role", "") != "teacher":
        abort(403)
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        duration_raw = request.form.get("duration", "30")
        exam_date_str = (request.form.get("date") or "").strip()
        if not title:
            flash("Title is required.", "danger")
            return render_template("teacher_create_exam.html")
        try:
            duration = max(5, min(300, int(duration_raw or 30)))
        except ValueError:
            duration = 30
        exam_date_sql = None
        if exam_date_str:
            try:
                dt = datetime.strptime(exam_date_str, "%Y-%m-%d")
                exam_date_sql = dt.strftime("%Y-%m-%d")
            except ValueError:
                flash("Invalid exam date format.", "danger")
                return render_template("teacher_create_exam.html")
        try:
            execute(
                """
                INSERT INTO exams (title, description, exam_date, duration, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                (title, description, exam_date_sql, duration, current_user.id),
            )
            flash("Exam created.", "success")
            return redirect(url_for("teacher.dashboard"))
        except Exception as ex:
            flash(f"Error creating exam: {ex}", "danger")
    return render_template("teacher_create_exam.html")

@app.route("/teacher/exams/upload", endpoint="teacher.upload_problems", methods=["GET", "POST"])
@login_required
def teacher_upload_problems():
    if getattr(current_user, "role", "") != "teacher":
        abort(403)
    try:
        exams = fetch_all(
            """
            SELECT id, title, exam_date, created_at
            FROM exams
            WHERE created_by=%s
            ORDER BY id DESC
            """,
            (current_user.id,),
        )
    except Exception:
        exams = []
    if request.method == "POST":
        exam_id = (request.form.get("exam_id") or "").strip()
        if not exam_id.isdigit():
            flash("Please select a valid exam.", "danger")
            return render_template("teacher_upload_problems.html", exams=exams)
        exam_id = int(exam_id)
        mode = (request.form.get("mode") or "").strip()
        if mode == "manual":
            q_text = (request.form.get("question_text") or "").strip()
            q_answer = (request.form.get("correct_output") or "").strip()
            q_marks_raw = (request.form.get("marks") or "").strip()
            if not q_text:
                flash("Question text is required.", "danger")
                return render_template("teacher_upload_problems.html", exams=exams)
            try:
                q_marks = max(1, int(q_marks_raw or 1))
            except ValueError:
                q_marks = 1
            try:
                execute(
                    """
                    INSERT INTO questions (exam_id, text, correct_output, marks, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (exam_id, q_text, q_answer, q_marks),
                )
                flash("Question added.", "success")
                return redirect(url_for("teacher.upload_problems"))
            except Exception as ex:
                flash(f"Error adding question: {ex}", "danger")
                return render_template("teacher_upload_problems.html", exams=exams)

        # Excel upload
        f = request.files.get("file")
        if not f or not f.filename.lower().endswith(".xlsx"):
            flash("Please upload a .xlsx file.", "danger")
            return render_template("teacher_upload_problems.html", exams=exams)
        try:
            safe_name = secure_filename(f.filename)
            save_path = UPLOAD_PROBLEMS_DIR / safe_name
            f.save(save_path)
        except Exception as ex:
            flash(f"Failed to save file: {ex}", "danger")
            return render_template("teacher_upload_problems.html", exams=exams)
        try:
            import pandas as pd
            df = pd.read_excel(save_path)
            required = {"text", "correct_output", "marks"}
            if not required.issubset({c.strip().lower() for c in df.columns}):
                flash("Excel must have headers: text, correct_output, marks", "danger")
                return render_template("teacher_upload_problems.html", exams=exams)
            inserted = 0
            for _, row in df.iterrows():
                text = str(row.get("text", "")).strip()
                correct_output = str(row.get("correct_output", "")).strip()
                try:
                    marks = int(row.get("marks", 1))
                except Exception:
                    marks = 1
                if not text:
                    continue
                execute(
                    """
                    INSERT INTO questions (exam_id, text, correct_output, marks, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (exam_id, text, correct_output, marks),
                )
                inserted += 1
            flash(f"Uploaded {inserted} question(s) from Excel.", "success")
            return redirect(url_for("teacher.dashboard"))
        except Exception as ex:
            flash(f"Failed to parse Excel: {ex}", "danger")
            return render_template("teacher_upload_problems.html", exams=exams)
    return render_template("teacher_upload_problems.html", exams=exams)

@app.route("/teacher/submissions", endpoint="teacher.view_submissions")
@login_required
def teacher_view_submissions():
    if current_user.role != "teacher":
        abort(403)
    try:
        rows = fetch_all(
            """
            SELECT s.id submission_id, e.id exam_id, e.title exam_title,
                   st.id student_id, st.name student_name,
                   s.status, COALESCE(ev.score, 0) marks, s.created_at
            FROM submissions s
            JOIN exams e ON e.id = s.exam_id
            JOIN students st ON st.id = s.student_id
            LEFT JOIN evaluations ev ON ev.submission_id = s.id
            WHERE e.created_by = %s
            ORDER BY s.created_at DESC
            """,
            (current_user.id,),
        )
    except Exception:
        rows = []
    return render_template("teacher_view_submissions.html", rows=rows)

@app.route("/teacher/report/<int:student_id>/<int:exam_id>", endpoint="teacher.student_report")
@login_required
def teacher_student_report(student_id, exam_id):
    if current_user.role != "teacher":
        abort(403)
    report = fetch_one(
        """
        SELECT st.name AS student_name, e.title AS exam_title, COALESCE(ev.score,0) AS marks,
               ev.feedback AS remarks
        FROM exams e
        JOIN submissions s ON s.exam_id = e.id AND s.student_id = %s
        LEFT JOIN evaluations ev ON ev.submission_id = s.id
        JOIN students st ON st.id = s.student_id
        WHERE e.id = %s AND e.created_by = %s
        ORDER BY s.created_at DESC LIMIT 1
        """,
        (student_id, exam_id, current_user.id),
    )
    return render_template("teacher_student_report.html", report=report)

# ------------------------------------------------------
# Student Area
# ------------------------------------------------------
@app.route("/student/dashboard", endpoint="student.dashboard")
@login_required
def student_dashboard():
    if getattr(current_user, "role", "") != "student":
        abort(403)
    return render_template("student_dashboard.html")

@app.route("/student/exams", endpoint="student.exam_list")
@login_required
def student_exam_list():
    if getattr(current_user, "role", "") != "student":
        abort(403)
    try:
        exams = fetch_all(
            """
            SELECT
                e.id,
                e.title,
                e.duration AS duration,
                CASE WHEN s.id IS NULL THEN 'assigned' ELSE s.status END AS status
            FROM exams e
            JOIN exam_assignments a ON a.exam_id = e.id
            LEFT JOIN (
                SELECT MAX(id) AS id, exam_id, student_id, MAX(status) status
                FROM submissions
                WHERE student_id = %s
                GROUP BY exam_id, student_id
            ) s ON s.exam_id = e.id
            WHERE a.student_id = %s
            ORDER BY e.id DESC
            """,
            (current_user.id, current_user.id),
        )
    except Exception as ex:
        flash(f"Could not load assigned exams: {ex}", "danger")
        exams = []
    return render_template("student_exam_list.html", exams=exams)

def allocate_random_questions(exam_id: int, k_default: int = 1):
    qs = fetch_all("SELECT id, marks FROM questions WHERE exam_id=%s ORDER BY id", (exam_id,))
    if not qs:
        return []
    k = min(k_default, len(qs))
    picked = random.sample(qs, k)
    return [q["id"] for q in picked]

@app.route("/student/exam/<int:exam_id>/start", endpoint="student.exam_start", methods=["GET", "POST"])
@login_required
def student_exam_start(exam_id):
    if getattr(current_user, "role", "") != "student":
        abort(403)
    exam = fetch_one(
        """
        SELECT e.id, e.title, e.duration AS duration
        FROM exams e
        JOIN exam_assignments a ON a.exam_id = e.id
        WHERE e.id = %s AND a.student_id = %s
        """,
        (exam_id, current_user.id),
    )
    if not exam:
        flash("This exam is not assigned to you (or it does not exist).", "danger")
        return redirect(url_for("student.exam_list"))
    if request.method == "POST":
        submission_id = execute_returning_id(
            "INSERT INTO submissions (exam_id, student_id, status, created_at) VALUES (%s,%s,%s,NOW())",
            (exam_id, current_user.id, "started"),
        )
        qids = allocate_random_questions(exam_id, k_default=5)
        execute("UPDATE submissions SET questions_json=%s WHERE id=%s",
                (json.dumps(qids), submission_id))
        log_action(current_user.id, 'student', f'Started exam {exam_id}')
        flash("Exam started. Good luck!", "info")
        return redirect(url_for("student.code_editor", exam_id=exam_id))
    return render_template("student_exam_start.html",
                           exam_id=exam_id, exam=exam,
                           timer_minutes=int(exam.get("duration") or 30))


@app.route("/student/exam/<int:exam_id>/editor", endpoint="student.code_editor")
@login_required
def student_code_editor(exam_id):
    if current_user.role != "student":
        abort(403)
    exam = fetch_one("SELECT id, title, duration FROM exams WHERE id=%s", (exam_id,))
    if not exam:
        abort(404)
    sub = fetch_one(
        """
        SELECT id, status, questions_json
        FROM submissions
        WHERE exam_id=%s AND student_id=%s
        ORDER BY created_at DESC LIMIT 1
        """,
        (exam_id, current_user.id),
    )
    if not sub:
        flash("Please start the exam first.", "warning")
        return redirect(url_for("student.exam_start", exam_id=exam_id))
    qids = []
    if sub.get("questions_json"):
        try:
            qids = json.loads(sub["questions_json"])
        except Exception:
            qids = []
    questions = []
    if qids:
        fmt = ",".join(["%s"] * len(qids))
        questions = fetch_all(f"SELECT id, text, marks, correct_output FROM questions WHERE id IN ({fmt})", tuple(qids))
        qmap = {q["id"]: q for q in questions}
        questions = [qmap[qid] for qid in qids if qid in qmap]
    return render_template("student_code_editor.html",
                           exam=exam, questions=questions,
                           exam_id=exam_id, submission_id=sub["id"],
                           timer_minutes=int((exam or {}).get("duration") or 30))

# ------------------- JDoodle -------------------
def jdoodle_execute(script: str, language_key: str, stdin_data: str = ""):
    JD_LANGUAGE_MAP = {
        "python3": ("python3", "4"),
        "cpp17": ("cpp17", "0"),
        "java": ("java", "4"),
        "c": ("c", "5"),
        "javascript": ("nodejs", "4"),
    }

    if not JDOODLE_CLIENT_ID or not JDOODLE_CLIENT_SECRET:
        return {"error": "JDoodle credentials not configured."}

    if language_key not in JD_LANGUAGE_MAP:
        return {"error": f"Unsupported language: {language_key}"}

    lang, version_index = JD_LANGUAGE_MAP[language_key]
    payload = {
        "clientId": JDOODLE_CLIENT_ID,
        "clientSecret": JDOODLE_CLIENT_SECRET,
        "script": script,
        "language": lang,
        "versionIndex": version_index,
        "stdin": stdin_data or ""
    }

    try:
        resp = requests.post("https://api.jdoodle.com/v1/execute", json=payload, timeout=25)
        if resp.status_code != 200:
            return {"error": f"JDoodle HTTP {resp.status_code}", "output": resp.text}
        data = resp.json()
        if data.get("error"):
            return {"error": data.get("error"), "output": data.get("output", "")}
        return {
            "output": data.get("output", ""),
            "cpuTime": data.get("cpuTime", ""),
            "memory": data.get("memory", ""),
            "statusCode": data.get("statusCode", 200)
        }
    except requests.exceptions.Timeout:
        return {"error": "JDoodle request timed out."}
    except Exception as ex:
        return {"error": f"JDoodle error: {ex}"}

@app.route("/student/run_code", methods=["POST"])
@login_required
def run_code():
    try:
        if getattr(current_user, "role", "") != "student":
            return jsonify({"error": "Unauthorized"}), 403

        code = request.form.get("code", "")
        language = request.form.get("language", "")
        input_data = request.form.get("input_data", "")

        if not code or not language:
            return jsonify({"error": "Missing code or language"}), 400

        result = jdoodle_execute(code, language, input_data)
        # Always return JSON so the frontend can show something
        return jsonify(result), 200
    except Exception as ex:
        # Never throw plain HTML back to the editor; keep it JSON
        return jsonify({"error": f"Server error: {ex}"}), 500



@app.route("/student/exam/<int:exam_id>/submit", endpoint="student.submit_exam", methods=["POST"])
@login_required
def student_submit_exam(exam_id):
    if current_user.role != "student":
        abort(403)

    language = request.form.get("language", "python3")
    code = request.form.get("code", "")

    try:
        # Create a submission row with code + status=submitted
        submission_id = execute_returning_id(
            "INSERT INTO submissions(exam_id, student_id, status, code, created_at) VALUES(%s,%s,%s,%s,NOW())",
            (exam_id, current_user.id, "submitted", code),
        )

        # Carry-forward allocated questions from the most recent "started" submission
        prev = fetch_one(
            """
            SELECT questions_json FROM submissions
            WHERE exam_id=%s AND student_id=%s AND id <> %s
            ORDER BY created_at DESC LIMIT 1
            """,
            (exam_id, current_user.id, submission_id),
        )
        if prev and prev.get("questions_json"):
            execute("UPDATE submissions SET questions_json=%s WHERE id=%s",
                    (prev["questions_json"], submission_id))

        # Load allocated questions
        sub = fetch_one("SELECT questions_json FROM submissions WHERE id=%s", (submission_id,))
        qids = []
        if sub and sub.get("questions_json"):
            try:
                qids = json.loads(sub["questions_json"])
            except Exception:
                qids = []

        # Run student's program ONCE (no stdin here; extend if you store testcases)
        run_result = jdoodle_execute(code, language, "")
        program_output = (run_result.get("output") or "").strip()
        runtime_err = run_result.get("error")

        # Build per-question AI scores (each 0..10), then average → final 0..10
        ai_scores = []
        feedback_lines = []

        if runtime_err:
            feedback_lines.append(f"Runtime error: {runtime_err}")

        if qids:
            fmt = ",".join(["%s"] * len(qids))
            qs = fetch_all(
                f"SELECT id, text, marks, correct_output FROM questions WHERE id IN ({fmt})",
                tuple(qids)
            )
            qmap = {q["id"]: q for q in qs}

            for qid in qids:
                q = qmap.get(qid)
                if not q:
                    continue
                expected = (q.get("correct_output") or "").strip()
                score_0_10 = _predict_ai_score_0_to_10(code, program_output, expected)
                ai_scores.append(score_0_10)

                # feedback: show expected and sample of actual
                sample_actual = program_output.replace("\r", "")[:120]
                feedback_lines.append(
                    f"Q{qid}: AI score {score_0_10:.1f}/10 (expected like '{expected}', saw '{sample_actual}')"
                )
        else:
            feedback_lines.append("No allocated questions found; AI scored on program output only.")
            # With no questions, use an output-only baseline
            score_0_10 = _predict_ai_score_0_to_10(code, program_output, program_output)
            ai_scores.append(score_0_10)

        # Final exam score: average of per-question AI scores → 0..10
        final_score = round(sum(ai_scores) / max(1, len(ai_scores)), 1)

        remarks = "\n".join(feedback_lines) if feedback_lines else "AI-evaluated."

        execute(
            "INSERT INTO evaluations(submission_id, score, feedback, evaluated_at) VALUES(%s,%s,%s,NOW())",
            (submission_id, final_score, remarks),
        )
        log_action(current_user.id, 'student', f'Submitted exam {exam_id} (AI score {final_score}/10)')
        flash(f"Exam submitted. AI score: {final_score}/10", "success")

    except Exception as ex:
        flash(f"Submission error: {ex}", "danger")

    return redirect(url_for("student.view_report", exam_id=exam_id))





@app.route("/student/report/<int:exam_id>", endpoint="student.view_report")
@login_required
def student_view_report(exam_id):
    if current_user.role != "student":
        abort(403)

    # If 0, fallback to most recent submission
    if exam_id == 0:
        latest = fetch_one(
            "SELECT exam_id FROM submissions WHERE student_id=%s ORDER BY created_at DESC LIMIT 1",
            (current_user.id,)
        )
        if latest:
            exam_id = latest["exam_id"]
        else:
            flash("No submissions found.", "info")
            return redirect(url_for("student.exam_list"))

    # Fetch submission, exam, evaluation
    report_row = fetch_one(
        """
        SELECT e.title AS exam_title, s.created_at AS date,
               COALESCE(ev.score,0) AS obtained_marks,
               COALESCE(ev.feedback,'') AS feedback_text,
               e.id AS exam_id, s.id AS submission_id
        FROM submissions s
        JOIN exams e ON e.id = s.exam_id
        LEFT JOIN evaluations ev ON ev.submission_id = s.id
        WHERE s.exam_id=%s AND s.student_id=%s
        ORDER BY s.created_at DESC LIMIT 1
        """,
        (exam_id, current_user.id)
    )

    if not report_row:
        flash("No report found for this exam.", "warning")
        return redirect(url_for("student.exam_list"))

    # Calculate total marks
    qids = []
    sub_q = fetch_one("SELECT questions_json FROM submissions WHERE id=%s", (report_row["submission_id"],))
    if sub_q and sub_q.get("questions_json"):
        try:
            qids = json.loads(sub_q["questions_json"])
        except Exception:
            qids = []

    total_marks = 0
    questions = []
    if qids:
        fmt = ",".join(["%s"] * len(qids))
        qs = fetch_all(f"SELECT id, text, marks, correct_output FROM questions WHERE id IN ({fmt})", tuple(qids))
        qmap = {q["id"]: q for q in qs}
        total_marks = sum(q["marks"] for q in qs)

        # Parse feedback text
        fb_lines = (report_row.get("feedback_text") or "").splitlines()
        for line in fb_lines:
            # try to match pattern "Q<ID>: ..."
            if line.startswith("Q"):
                parts = line.split(":", 1)
                qnum = parts[0][1:].strip() if len(parts) > 1 else None
                feedback = parts[1].strip() if len(parts) > 1 else ""
                qid = int(qnum) if qnum and qnum.isdigit() else None
                q = qmap.get(qid, {"text": "Unknown Question", "marks": 0})
                questions.append({
                    "text": q["text"],
                    "obtained": q["marks"] if "correct" in feedback.lower() else 0,
                    "total": q["marks"],
                    "feedback": feedback
                })
            else:
                continue

    # Compute pass/fail
    obtained = float(report_row["obtained_marks"])
    status = "Pass" if total_marks and (obtained / total_marks) * 100 >= 40 else "Fail"

    # Package everything for template
    report = {
        "exam_title": report_row["exam_title"],
        "date": report_row["date"].strftime("%Y-%m-%d %H:%M"),
        "total_marks": total_marks,
        "obtained_marks": obtained,
        "status": status,
        "questions": questions,
        "summary": report_row.get("feedback_text", "")
    }

    return render_template("student_view_report.html", report=report)


# ------------------------------------------------------
# Assign exam
# ------------------------------------------------------
@app.route("/teacher/exams/<int:exam_id>/assign", endpoint="teacher.assign_exam", methods=["GET", "POST"])
@login_required
def teacher_assign_exam(exam_id):
    if getattr(current_user, "role", "") != "teacher":
        abort(403)
    exam = fetch_one("SELECT id, title FROM exams WHERE id=%s AND created_by=%s", (exam_id, current_user.id))
    if not exam:
        flash("Exam not found or not yours.", "danger")
        return redirect(url_for("teacher.dashboard"))
    if request.method == "POST":
        ids = request.form.getlist("student_ids")
        try:
            execute("DELETE FROM exam_assignments WHERE exam_id=%s", (exam_id,))
            for sid in ids:
                if sid.isdigit():
                    execute(
                        "INSERT INTO exam_assignments (exam_id, student_id, assigned_at) VALUES (%s,%s,NOW())",
                        (exam_id, int(sid)),
                    )
            flash(f"Assigned to {len(ids)} student(s).", "success")
            return redirect(url_for("teacher.dashboard"))
        except Exception as ex:
            flash(f"Error assigning exam: {ex}", "danger")
    students = fetch_all("SELECT id, name, email FROM students ORDER BY id DESC")
    assigned = fetch_all("SELECT student_id FROM exam_assignments WHERE exam_id=%s", (exam_id,))
    assigned_set = {row["student_id"] for row in assigned}
    return render_template("teacher_assign_exam.html", exam=exam, students=students, assigned_set=assigned_set)

@app.route("/teacher/exams/<int:exam_id>/assign_all", endpoint="teacher.assign_exam_all", methods=["POST"])
@login_required
def teacher_assign_exam_all(exam_id):
    if getattr(current_user, "role", "") != "teacher":
        abort(403)
    exam = fetch_one("SELECT id FROM exams WHERE id=%s AND created_by=%s", (exam_id, current_user.id))
    if not exam:
        abort(403)
    try:
        students = fetch_all("SELECT id FROM students")
        execute("DELETE FROM exam_assignments WHERE exam_id=%s", (exam_id,))
        for s in students:
            execute(
                "INSERT INTO exam_assignments (exam_id, student_id, assigned_at) VALUES (%s,%s,NOW())",
                (exam_id, s["id"]),
            )
        flash(f"Assigned to {len(students)} student(s).", "success")
    except Exception as ex:
        flash(f"Error assigning to all: {ex}", "danger")
    return redirect(url_for("teacher.assign_exam", exam_id=exam_id))

# ------------------------------------------------------
# Main
# ------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
