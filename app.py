from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2

app = Flask(__name__)
app.secret_key = 'catsurge-secret-key-change-in-production'

def get_db():
    return psycopg2.connect(
        host="localhost", database="catsurge_db", user="postgres", 
        password="skdn1418", port="5432"
    )

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
    u = cur.fetchone()
    cur.close()
    conn.close()
    return User(u[0], u[1], u[2]) if u else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, email, password, role FROM users WHERE email = %s", (email,))
        user_data = cur.fetchone()
        
        if user_data:
            # Existing user
            if check_password_hash(user_data[2], password):
                user = User(user_data[0], user_data[1], user_data[3])
                login_user(user)
                flash('Welcome back!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password or email', 'error')
        else:
            # NEW USER - redirect to register
            flash(f'No account found for {email}. Please register!', 'warning')
            return redirect(url_for('register', email=email))
        
        cur.close()
        conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    email = request.args.get('email', '')
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                       (email, generate_password_hash(password), 'student'))
            conn.commit()
            
            # Auto-login
            cur.execute("SELECT id, email, role FROM users WHERE email = %s", (email,))
            user_data = cur.fetchone()
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            flash('Account created successfully!', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('dashboard'))
        except:
            flash('Email already exists!', 'error')
            cur.close()
            conn.close()
    
    return render_template('register.html', email=email)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('admin_dashboard.html')
    return render_template('student_dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
