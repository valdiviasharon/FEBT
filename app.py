from flask import Flask, request, redirect, url_for, render_template, flash
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'supersecretkey'  # Necesario para que flash funcione

# Asegúrate de que la carpeta de subida exista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Definir archivos de almacenamiento
USERS_FILE = 'users.json'
CASES_FILE = 'cases.json'

# Funciones para manejar archivos
def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as file:
        return json.load(file)

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Cargar datos
users_db = load_data(USERS_FILE)
cases_db = load_data(CASES_FILE)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'txt'}

@app.route('/')
def index():
    return render_template('index.html', casos=cases_db, users=users_db)

@app.route('/users')
def users():
    return render_template('users.html', users1=users_db)

@app.route('/case/<int:case_id>')
def case_page(case_id):
    case = next((case for case in cases_db if case['id'] == case_id), None)
    if case:
        return render_template('case.html', case=case)
    else:
        flash('Case not found')
        return redirect(url_for('index'))

@app.route('/upload_file', methods=['POST'])
def upload_file():
    case_id = request.form['case_id']
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Actualizar la lista de documentos del caso
        case = next((case for case in cases_db if case['id'] == int(case_id)), None)
        if case:
            case['documents'].append(filename)
            save_data(CASES_FILE, cases_db)
        
        flash('File successfully uploaded')
        return redirect(url_for('case_page', case_id=case_id))
    else:
        flash('Allowed file types are pdf, txt')
        return redirect(request.url)

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        user = {
            'name': request.form['name'],
            'law_area': request.form['law_area'].split(','),
            'contact': request.form['contact'],
            'email': request.form['email']
        }
        users_db.append(user)
        save_data(USERS_FILE, users_db)
        flash('User successfully added')
    except KeyError as e:
        flash(f'Missing data: {e.args[0]}')
    return redirect(url_for('users'))

@app.route('/add_case', methods=['POST'])
def add_case():
    try:
        case = {
            'id': len(cases_db) + 1,
            'title': request.form['title'],
            'law_area': request.form['law_area'].split(','),
            'description': request.form['description'],
            'responsible': request.form['responsible'],
            'client_name': request.form['client_name'],
            'client_surname': request.form['client_surname'],
            'document_type': request.form['document_type'],
            'document_number': request.form['document_number'],
            'contact_number': request.form['contact_number'],
            'email': request.form['email'],
            'documents': []
        }
        cases_db.append(case)
        save_data(CASES_FILE, cases_db)
        flash('Case successfully added')
    except KeyError as e:
        flash(f'Missing data: {e.args[0]}')
    return redirect(url_for('index'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        try:
            users_db[user_id]['name'] = request.form['name']
            users_db[user_id]['law_area'] = request.form['law_area'].split(',')
            users_db[user_id]['contact'] = request.form['contact']
            users_db[user_id]['email'] = request.form['email']
            save_data(USERS_FILE, users_db)
            flash('User successfully updated')
        except KeyError as e:
            flash(f'Missing data: {e.args[0]}')
        return redirect(url_for('users'))
    else:
        user = users_db[user_id]
        return render_template('edit_user.html', user=user, user_id=user_id)

@app.route('/edit_case/<int:case_id>', methods=['GET', 'POST'])
def edit_case(case_id):
    if request.method == 'POST':
        try:
            case = next(case for case in cases_db if case['id'] == case_id)
            case['title'] = request.form['title']
            case['law_area'] = request.form['law_area'].split(',')
            case['description'] = request.form['description']
            case['responsible'] = request.form['responsible']
            case['client_name'] = request.form['client_name']
            case['client_surname'] = request.form['client_surname']
            case['document_type'] = request.form['document_type']
            case['document_number'] = request.form['document_number']
            case['contact_number'] = request.form['contact_number']
            case['email'] = request.form['email']
            
            if 'new_document' in request.files and request.files['new_document'].filename != '':
                new_document = request.files['new_document']
                if allowed_file(new_document.filename):
                    filename = secure_filename(new_document.filename)
                    new_document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    case['documents'].append(filename)
            
            save_data(CASES_FILE, cases_db)
            flash('Case successfully updated')
        except KeyError as e:
            flash(f'Missing data: {e.args[0]}')
        return redirect(url_for('index'))
    else:
        case = next(case for case in cases_db if case['id'] == case_id)
        return render_template('edit_case.html', case=case, users=users_db)

@app.route('/delete_case/<int:case_id>', methods=['POST'])
def delete_case(case_id):
    global cases_db
    cases_db = [case for case in cases_db if case['id'] != case_id]
    save_data(CASES_FILE, cases_db)
    flash('Case successfully deleted')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
