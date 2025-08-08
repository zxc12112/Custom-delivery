from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = 'tracking.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS parcels (
                tracking_number TEXT PRIMARY KEY
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_number TEXT,
                status TEXT,
                timestamp TEXT,
                FOREIGN KEY(tracking_number) REFERENCES parcels(tracking_number)
            )
        ''')
        conn.commit()

def add_update(tracking_number, status):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        # Ensure parcel exists
        c.execute('INSERT OR IGNORE INTO parcels (tracking_number) VALUES (?)', (tracking_number,))
        # Add update with current time
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        c.execute('INSERT INTO updates (tracking_number, status, timestamp) VALUES (?, ?, ?)', (tracking_number, status, now))
        conn.commit()

def get_updates(tracking_number):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('SELECT status, timestamp FROM updates WHERE tracking_number=? ORDER BY id', (tracking_number,))
        return c.fetchall()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = ''
    if request.method == 'POST':
        tn = request.form.get('tracking_number', '').strip()
        status = request.form.get('status', '').strip()
        if tn and status:
            add_update(tn, status)
            message = f'Added update for {tn}'
        else:
            message = 'Please enter both tracking number and status.'
    return render_template('admin.html', message=message)

@app.route('/track', methods=['GET', 'POST'])
def track():
    updates = None
    tn = ''
    message = ''
    if request.method == 'POST':
        tn = request.form.get('tracking_number', '').strip()
        if tn:
            updates = get_updates(tn)
            if not updates:
                message = f'No updates found for {tn}'
        else:
            message = 'Please enter a tracking number.'
    return render_template('track.html', updates=updates, tracking_number=tn, message=message)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
