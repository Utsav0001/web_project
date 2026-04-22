from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3, os, json
from datetime import datetime, date, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'healthsync_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    db = sqlite3.connect('healthsync.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            dob TEXT,
            blood_group TEXT,
            gender TEXT,
            address TEXT,
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            allergies TEXT,
            chronic_conditions TEXT,
            profile_pic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doctor_name TEXT NOT NULL,
            specialty TEXT,
            hospital TEXT,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'upcoming',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            instructions TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            file_name TEXT,
            file_path TEXT,
            description TEXT,
            record_date TEXT,
            doctor_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    db.commit()
    db.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_notification(user_id, message, ntype='info'):
    db = get_db()
    db.execute('INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)', (user_id, message, ntype))
    db.commit()
    db.close()

# ─── AUTH ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        phone = request.form.get('phone', '')
        db = get_db()
        try:
            db.execute('INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)', (name, email, password, phone))
            db.commit()
            user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            add_notification(user['id'], f'Welcome to HealthSync, {name}! Start by adding your health information.', 'success')
            db.close()
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            flash('Email already registered', 'error')
            db.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    uid = session['user_id']
    today = date.today().isoformat()
    upcoming = db.execute(
        "SELECT * FROM appointments WHERE user_id=? AND appointment_date>=? AND status='upcoming' ORDER BY appointment_date, appointment_time LIMIT 3", (uid, today)
    ).fetchall()
    medications = db.execute("SELECT * FROM medications WHERE user_id=? AND is_active=1 LIMIT 5", (uid,)).fetchall()
    notifications = db.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (uid,)).fetchall()
    unread_count = db.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0", (uid,)).fetchone()[0]
    total_appointments = db.execute("SELECT COUNT(*) FROM appointments WHERE user_id=?", (uid,)).fetchone()[0]
    active_meds = db.execute("SELECT COUNT(*) FROM medications WHERE user_id=? AND is_active=1", (uid,)).fetchone()[0]
    total_records = db.execute("SELECT COUNT(*) FROM health_records WHERE user_id=?", (uid,)).fetchone()[0]
    user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    db.close()
    return render_template('dashboard.html', upcoming=upcoming, medications=medications,
                           notifications=notifications, unread_count=unread_count,
                           total_appointments=total_appointments, active_meds=active_meds,
                           total_records=total_records, user=user, today=today)

# ─── APPOINTMENTS ─────────────────────────────────────────────────────────────

@app.route('/appointments')
@login_required
def appointments():
    db = get_db()
    uid = session['user_id']
    today = date.today().isoformat()
    all_appts = db.execute("SELECT * FROM appointments WHERE user_id=? ORDER BY appointment_date DESC, appointment_time DESC", (uid,)).fetchall()
    db.close()
    return render_template('appointments.html', appointments=all_appts, today=today)

@app.route('/appointments/add', methods=['POST'])
@login_required
def add_appointment():
    uid = session['user_id']
    db = get_db()
    db.execute('''INSERT INTO appointments (user_id, doctor_name, specialty, hospital, appointment_date, appointment_time, reason, notes)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
               (uid, request.form['doctor_name'], request.form['specialty'], request.form['hospital'],
                request.form['appointment_date'], request.form['appointment_time'],
                request.form['reason'], request.form.get('notes', '')))
    db.commit()
    add_notification(uid, f"Appointment with Dr. {request.form['doctor_name']} scheduled for {request.form['appointment_date']}", 'appointment')
    db.close()
    flash('Appointment scheduled successfully!', 'success')
    return redirect(url_for('appointments'))

@app.route('/appointments/update/<int:appt_id>', methods=['POST'])
@login_required
def update_appointment(appt_id):
    db = get_db()
    action = request.form.get('action')
    if action == 'cancel':
        db.execute("UPDATE appointments SET status='cancelled' WHERE id=? AND user_id=?", (appt_id, session['user_id']))
    elif action == 'complete':
        db.execute("UPDATE appointments SET status='completed' WHERE id=? AND user_id=?", (appt_id, session['user_id']))
    elif action == 'reschedule':
        db.execute("UPDATE appointments SET appointment_date=?, appointment_time=?, status='upcoming' WHERE id=? AND user_id=?",
                   (request.form['new_date'], request.form['new_time'], appt_id, session['user_id']))
    db.commit()
    db.close()
    flash('Appointment updated!', 'success')
    return redirect(url_for('appointments'))

@app.route('/appointments/delete/<int:appt_id>', methods=['POST'])
@login_required
def delete_appointment(appt_id):
    db = get_db()
    db.execute("DELETE FROM appointments WHERE id=? AND user_id=?", (appt_id, session['user_id']))
    db.commit()
    db.close()
    flash('Appointment deleted.', 'info')
    return redirect(url_for('appointments'))

# ─── MEDICATIONS ─────────────────────────────────────────────────────────────

@app.route('/medications')
@login_required
def medications():
    db = get_db()
    uid = session['user_id']
    meds = db.execute("SELECT * FROM medications WHERE user_id=? ORDER BY is_active DESC, reminder_time ASC", (uid,)).fetchall()
    db.close()
    return render_template('medications.html', medications=meds)

@app.route('/medications/add', methods=['POST'])
@login_required
def add_medication():
    uid = session['user_id']
    db = get_db()
    db.execute('''INSERT INTO medications (user_id, medicine_name, dosage, frequency, reminder_time, start_date, end_date, instructions)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
               (uid, request.form['medicine_name'], request.form['dosage'], request.form['frequency'],
                request.form['reminder_time'], request.form.get('start_date', ''), request.form.get('end_date', ''),
                request.form.get('instructions', '')))
    db.commit()
    add_notification(uid, f"Reminder set for {request.form['medicine_name']} at {request.form['reminder_time']}", 'medication')
    db.close()
    flash('Medication reminder added!', 'success')
    return redirect(url_for('medications'))

@app.route('/medications/toggle/<int:med_id>', methods=['POST'])
@login_required
def toggle_medication(med_id):
    db = get_db()
    med = db.execute("SELECT is_active FROM medications WHERE id=? AND user_id=?", (med_id, session['user_id'])).fetchone()
    if med:
        db.execute("UPDATE medications SET is_active=? WHERE id=?", (0 if med['is_active'] else 1, med_id))
        db.commit()
    db.close()
    return redirect(url_for('medications'))

@app.route('/medications/delete/<int:med_id>', methods=['POST'])
@login_required
def delete_medication(med_id):
    db = get_db()
    db.execute("DELETE FROM medications WHERE id=? AND user_id=?", (med_id, session['user_id']))
    db.commit()
    db.close()
    flash('Medication removed.', 'info')
    return redirect(url_for('medications'))

# ─── HEALTH RECORDS ───────────────────────────────────────────────────────────

@app.route('/records')
@login_required
def records():
    db = get_db()
    uid = session['user_id']
    category = request.args.get('category', '')
    if category:
        recs = db.execute("SELECT * FROM health_records WHERE user_id=? AND category=? ORDER BY record_date DESC", (uid, category)).fetchall()
    else:
        recs = db.execute("SELECT * FROM health_records WHERE user_id=? ORDER BY record_date DESC", (uid,)).fetchall()
    categories = db.execute("SELECT DISTINCT category FROM health_records WHERE user_id=?", (uid,)).fetchall()
    db.close()
    return render_template('records.html', records=recs, categories=categories, selected_category=category)

@app.route('/records/add', methods=['POST'])
@login_required
def add_record():
    uid = session['user_id']
    file_name, file_path = '', ''
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            file.save(file_path)
    db = get_db()
    db.execute('''INSERT INTO health_records (user_id, title, category, file_name, file_path, description, record_date, doctor_name)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
               (uid, request.form['title'], request.form['category'], file_name, file_path,
                request.form.get('description', ''), request.form.get('record_date', ''), request.form.get('doctor_name', '')))
    db.commit()
    db.close()
    flash('Health record added!', 'success')
    return redirect(url_for('records'))

@app.route('/records/delete/<int:rec_id>', methods=['POST'])
@login_required
def delete_record(rec_id):
    db = get_db()
    db.execute("DELETE FROM health_records WHERE id=? AND user_id=?", (rec_id, session['user_id']))
    db.commit()
    db.close()
    flash('Record deleted.', 'info')
    return redirect(url_for('records'))

# ─── PROFILE ─────────────────────────────────────────────────────────────────

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db()
    uid = session['user_id']
    if request.method == 'POST':
        db.execute('''UPDATE users SET name=?, phone=?, dob=?, blood_group=?, gender=?, address=?,
                      emergency_contact_name=?, emergency_contact_phone=?, allergies=?, chronic_conditions=?
                      WHERE id=?''',
                   (request.form['name'], request.form['phone'], request.form['dob'],
                    request.form['blood_group'], request.form['gender'], request.form['address'],
                    request.form['emergency_contact_name'], request.form['emergency_contact_phone'],
                    request.form['allergies'], request.form['chronic_conditions'], uid))
        db.commit()
        session['user_name'] = request.form['name']
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    db.close()
    return render_template('profile.html', user=user)

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    db = get_db()
    uid = session['user_id']
    user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if check_password_hash(user['password'], request.form['current_password']):
        db.execute("UPDATE users SET password=? WHERE id=?", (generate_password_hash(request.form['new_password']), uid))
        db.commit()
        flash('Password changed successfully!', 'success')
    else:
        flash('Current password is incorrect', 'error')
    db.close()
    return redirect(url_for('profile'))

# ─── NOTIFICATIONS API ────────────────────────────────────────────────────────

@app.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    db = get_db()
    db.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (session['user_id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})

@app.route('/api/reminders/check')
@login_required
def check_reminders():
    db = get_db()
    uid = session['user_id']
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    due_meds = db.execute(
        "SELECT * FROM medications WHERE user_id=? AND is_active=1 AND reminder_time=?", (uid, current_time)
    ).fetchall()
    db.close()
    reminders = [{'name': m['medicine_name'], 'dosage': m['dosage'], 'time': m['reminder_time']} for m in due_meds]
    return jsonify({'reminders': reminders, 'time': current_time})

@app.route('/api/upcoming-reminders')
@login_required
def upcoming_reminders():
    db = get_db()
    uid = session['user_id']
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    meds = db.execute("SELECT * FROM medications WHERE user_id=? AND is_active=1 ORDER BY reminder_time", (uid,)).fetchall()
    db.close()
    upcoming = []
    for m in meds:
        med_time = m['reminder_time']
        if med_time >= current_time:
            upcoming.append({'name': m['medicine_name'], 'dosage': m['dosage'], 'time': med_time, 'frequency': m['frequency']})
    return jsonify({'upcoming': upcoming[:5]})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
