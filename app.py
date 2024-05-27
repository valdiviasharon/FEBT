from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Datos de ejemplo
casos = [
    {"id": 1, "title": "Constructora Río Azul S.A."},
    {"id": 2, "title": "Departamento de Transporte"},
    {"id": 3, "title": "Cadena de Restaurantes Buen Sabor"},
    {"id": 4, "title": "Tienda Electrónica MegaTech"}
]

users1 = [
    {"id": 1, "name": "Ana Flores"},
    {"id": 2, "name": "Diego Torres"},
    {"id": 3, "name": "Gemma Luque"},
    {"id": 4, "name": "Katherine Pino"}
]

@app.route('/')
def index():
    print("Cases:", casos)  # Agrega este print para depurar
    return render_template('index.html', casos=casos, users=users)

@app.route('/case/<int:case_id>')
def case(case_id):
    case = next((c for c in casos if c['id'] == case_id), None)
    return render_template('case.html', case=case)

@app.route('/users')
def user_settings():
    return render_template('users.html', users1=users1)

@app.route('/add_case', methods=['POST'])
def add_case():
    title = request.form['title']
    law_area = request.form.getlist('law_area')
    description = request.form['description']
    responsible = request.form['responsible']
    new_case = {"id": len(casos) + 1, "title": title, "law_area": law_area, "description": description, "responsible": responsible}
    casos.append(new_case)
    save_cases()
    return redirect(url_for('index'))

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    law_area = request.form.getlist('law_area')
    contact = request.form['contact']
    email = request.form['email']
    new_user = {"id": len(users) + 1, "name": name, "law_area": law_area, "contact": contact, "email": email}
    users.append(new_user)
    save_users()
    return redirect(url_for('user_settings'))

def save_cases():
    with open('cases.txt', 'w') as f:
        for case in casos:
            f.write(f"{case['id']}|{case['title']}|{','.join(case['law_area'])}|{case['description']}|{case['responsible']}\n")

def save_users():
    with open('users.txt', 'w') as f:
        for user in users:
            f.write(f"{user['id']}|{user['name']}|{','.join(user['law_area'])}|{user['contact']}|{user['email']}\n")

if __name__ == '__main__':
    if os.path.exists('cases.txt'):
        with open('cases.txt', 'r') as f:
            cases = [dict(zip(["id", "title", "law_area", "description", "responsible"], line.strip().split('|'))) for line in f]
            for case in cases:
                case["law_area"] = case["law_area"].split(',')
    if os.path.exists('users.txt'):
        with open('users.txt', 'r') as f:
            users = [dict(zip(["id", "name", "law_area", "contact", "email"], line.strip().split('|'))) for line in f]
            for user in users:
                user["law_area"] = user["law_area"].split(',')
    app.run(debug=True)
