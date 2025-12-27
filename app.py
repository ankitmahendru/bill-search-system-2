from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from werkzeug.security import check_password_hash
import csv
import io
from flask import make_response
import os
from database import init_db

# Needed for file download
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
DB_NAME = "bills.db"

# --- LOGIN SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE id=?", (user_id,))
    res = c.fetchone()
    conn.close()
    if res:
        return User(id=res[0], username=res[1])
    return None

# --- HELPER FUNCTIONS ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- PUBLIC ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    bill = None
    if request.method == 'POST':
        # REQ 2: Auto-Capitalize
        raw_addr = request.form['address']
        address = raw_addr.strip().upper()
        
        conn = get_db_connection()
        # Join tables to get Name + Bill details
        bill = conn.execute('''
            SELECT r.name, b.amount, b.due_date 
            FROM bills b
            JOIN residents r ON b.address = r.address
            WHERE b.address = ?
        ''', (address,)).fetchone()
        conn.close()
        
        if not bill:
            flash('No active bill found for this address.', 'danger')
            
    return render_template('index.html', bill=bill)

# --- ADMIN ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(id=user['id'], username=user['username'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


from datetime import datetime

# Custom Filter to format date to Indian Standard (DD-MM-YYYY)
@app.template_filter('indian_date')
def indian_date_filter(value):
    if not value:
        return '-'
    try:
        # Converts YYYY-MM-DD to DD-MM-YYYY
        return datetime.strptime(value, '%Y-%m-%d').strftime('%d-%m-%Y')
    except ValueError:
        return value
        

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    conn = get_db_connection()
    
    # 1. FETCH TABLE DATA: Get all residents + their current bill (if any)
    # LEFT JOIN ensures we see residents even if they don't have a bill yet.
    all_residents = conn.execute('''
        SELECT r.address, r.name, b.amount, b.due_date 
        FROM residents r
        LEFT JOIN bills b ON r.address = b.address
        ORDER BY r.address ASC
    ''').fetchall()

    # 2. HANDLE SELECTION (Search Bar or Table Click)
    resident = None
    current_bill = None
    search_term = ""

    # Check if triggered by Search Button (POST) or Table Select Link (GET)
    if request.method == 'POST':
        search_term = request.form.get('address', '').strip().upper()
    elif request.args.get('select_address'):
        search_term = request.args.get('select_address').strip().upper()

    # If we have a target address, fetch its specific details for the form
    if search_term:
        resident = conn.execute('SELECT * FROM residents WHERE address = ?', (search_term,)).fetchone()
        current_bill = conn.execute('SELECT * FROM bills WHERE address = ?', (search_term,)).fetchone()
        
        if not resident and request.method == 'POST':
            flash(f'Address "{search_term}" not found. You can add it below.', 'info')

    conn.close()

    return render_template('dashboard.html', 
                         all_residents=all_residents, # New data for the table
                         resident=resident, 
                         bill=current_bill, 
                         search_term=search_term)


@app.route('/save_bill', methods=['POST'])
@login_required
def save_bill():
    # REQ 2: Auto-Capitalize
    address = request.form['address'].strip().upper()
    name = request.form['name']
    amount = request.form['amount']
    due_date = request.form['due_date']
    
    conn = get_db_connection()
    try:
        # 1. Upsert Resident (Create if new, update name if exists)
        conn.execute('INSERT OR REPLACE INTO residents (address, name) VALUES (?, ?)', 
                     (address, name))
        
        # 2. REQ 3: Delete OLD bill for this address
        conn.execute('DELETE FROM bills WHERE address = ?', (address,))
        
        # 3. Insert NEW bill
        conn.execute('INSERT INTO bills (address, amount, due_date) VALUES (?, ?, ?)',
                     (address, amount, due_date))
        
        conn.commit()
        flash('Bill saved successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('dashboard'))


    # --- BULK IMPORT/EXPORT ROUTES ---

@app.route('/export_csv')
@login_required
def export_csv():
    conn = get_db_connection()
    # Fetch all data (Left Join to include residents without bills)
    data = conn.execute('''
        SELECT r.address, r.name, b.amount, b.due_date 
        FROM residents r
        LEFT JOIN bills b ON r.address = b.address
        ORDER BY r.address ASC
    ''').fetchall()
    conn.close()

    # Create CSV in memory
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Write Header
    cw.writerow(['Address', 'Name', 'Bill Amount', 'Due Date (YYYY-MM-DD)'])
    
    # Write Rows
    for row in data:
        cw.writerow([
            row['address'], 
            row['name'], 
            row['amount'] if row['amount'] else 0, 
            row['due_date'] if row['due_date'] else ''
        ])

    # Prepare Response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=billing_data.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/import_csv', methods=['POST'])
@login_required
def import_csv():
    if 'file' not in request.files:
        flash('No file uploaded.', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Read file stream safely
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        
        # Skip Header Row (optional, depends if your CSV has headers)
        next(csv_input, None) 

        conn = get_db_connection()
        count = 0
        
        for row in csv_input:
            # Expected Format: [Address, Name, Amount, DueDate]
            if len(row) < 4: continue
            
            # Clean Data
            address = row[0].strip().upper()
            name = row[1].strip()
            amount = row[2].strip()
            due_date = row[3].strip()

            if not address or not name: continue # Skip invalid rows

            # 1. Update/Insert Resident
            conn.execute('INSERT OR REPLACE INTO residents (address, name) VALUES (?, ?)', 
                         (address, name))
            
            # 2. Update Bill (Delete old -> Insert new)
            conn.execute('DELETE FROM bills WHERE address = ?', (address,))
            
            # Only add bill if amount is greater than 0
            if amount and float(amount) > 0:
                conn.execute('INSERT INTO bills (address, amount, due_date) VALUES (?, ?, ?)',
                             (address, amount, due_date))
            
            count += 1

        conn.commit()
        conn.close()
        flash(f'Success! Processed {count} records.', 'success')

    except Exception as e:
        flash(f'Error processing CSV: {e}', 'danger')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # AUTO-SETUP: If database is missing, create it automatically
    if not os.path.exists('bills.db'):
        print("⚠️ Database not found. Creating new system...")
        init_db()

    # Open browser automatically for the user
    import webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    Timer(1, open_browser).start()

    # Run the app
    app.run(debug=False, port=5000)