from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SESSION_TYPE'] = 'filesystem'

# Database simulation with JSON file
DATABASE_FILE = 'users_database.json'

def load_users():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user_data(username):
    users = load_users()
    return users.get(username, None)

def save_user_data(username, data):
    users = load_users()
    users[username] = data
    save_users(users)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        users = load_users()
        
        # Validation
        if not username or not email or not password:
            return render_template('register.html', error='Tous les champs sont requis')
        
        if username in users:
            return render_template('register.html', error='Cet utilisateur existe déjà')
        
        if password != confirm_password:
            return render_template('register.html', error='Les mots de passe ne correspondent pas')
        
        if len(password) < 6:
            return render_template('register.html', error='Le mot de passe doit avoir au moins 6 caractères')
        
        # Create user
        users[username] = {
            'email': email,
            'password': generate_password_hash(password),
            'capital': 100.00,
            'positions': [],
            'gains': 0.00,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_users(users)
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_data(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Identifiants invalides')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = get_user_data(session['username'])
    return render_template('dashboard.html', user=user, username=session['username'])

@app.route('/api/user-data')
def api_user_data():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = get_user_data(session['username'])
    return jsonify(user)

@app.route('/api/add-position', methods=['POST'])
def api_add_position():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    user = get_user_data(session['username'])
    
    position = {
        'id': len(user['positions']) + 1,
        'symbol': data.get('symbol'),
        'shares': float(data.get('shares')),
        'entry_price': float(data.get('entry_price')),
        'current_price': float(data.get('current_price')),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    user['positions'].append(position)
    save_user_data(session['username'], user)
    
    return jsonify({'success': True, 'position': position})

@app.route('/api/delete-position/<int:position_id>', methods=['DELETE'])
def api_delete_position(position_id):
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = get_user_data(session['username'])
    user['positions'] = [p for p in user['positions'] if p['id'] != position_id]
    save_user_data(session['username'], user)
    
    return jsonify({'success': True})

@app.route('/api/update-position/<int:position_id>', methods=['PUT'])
def api_update_position(position_id):
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    user = get_user_data(session['username'])
    
    for position in user['positions']:
        if position['id'] == position_id:
            position['current_price'] = float(data.get('current_price'))
            position['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    
    save_user_data(session['username'], user)
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)