from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin123@db:5432/medical_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    order_no = db.Column(db.String(50), nullable=False)
    vlk_date = db.Column(db.Date)
    vlk_diagnosis = db.Column(db.String(200))
    kmo_date = db.Column(db.Date)
    kmo_diagnosis = db.Column(db.String(200))
    umo_date = db.Column(db.Date)
    umo_diagnosis = db.Column(db.String(200))
    kmo2_date = db.Column(db.Date)  # Добавляем поле для второй КМО
    kmo2_diagnosis = db.Column(db.String(200))  # Добавляем поле для диагноза второй КМО
    preflight_condition = db.Column(db.String(100))

@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            employee = Employee(
                fio=request.form['fio'],
                birth_date=datetime.strptime(request.form['birth_date'], '%Y-%m-%d'),
                position=request.form['position'],
                order_no=request.form['order_no'],
                vlk_date=datetime.strptime(request.form['vlk_date'], '%Y-%m-%d') if request.form['vlk_date'] else None,
                vlk_diagnosis=request.form['vlk_diagnosis'],
                kmo_date=datetime.strptime(request.form['kmo_date'], '%Y-%m-%d') if request.form['kmo_date'] else None,
                kmo_diagnosis=request.form['kmo_diagnosis'],
                umo_date=datetime.strptime(request.form['umo_date'], '%Y-%m-%d') if request.form['umo_date'] else None,
                umo_diagnosis=request.form['umo_diagnosis'],
                kmo2_date=datetime.strptime(request.form['kmo2_date'], '%Y-%m-%d') if request.form['kmo2_date'] else None,  # Новое поле
                kmo2_diagnosis=request.form['kmo2_diagnosis'],  # Новое поле
                preflight_condition=request.form['preflight_condition']
            )
            db.session.add(employee)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return f"Error adding employee: {str(e)}"
    return render_template('add.html')
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        try:
            employee.fio = request.form['fio']
            employee.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
            employee.position = request.form['position']
            employee.order_no = request.form['order_no']
            employee.vlk_date = datetime.strptime(request.form['vlk_date'], '%Y-%m-%d') if request.form['vlk_date'] else None
            employee.vlk_diagnosis = request.form['vlk_diagnosis']
            employee.kmo_date = datetime.strptime(request.form['kmo_date'], '%Y-%m-%d') if request.form['kmo_date'] else None
            employee.kmo_diagnosis = request.form['kmo_diagnosis']
            employee.umo_date = datetime.strptime(request.form['umo_date'], '%Y-%m-%d') if request.form['umo_date'] else None
            employee.umo_diagnosis = request.form['umo_diagnosis']
            employee.kmo2_date = datetime.strptime(request.form['kmo2_date'], '%Y-%m-%d') if request.form['kmo2_date'] else None  # Новое поле
            employee.kmo2_diagnosis = request.form['kmo2_diagnosis']  # Новое поле
            employee.preflight_condition = request.form['preflight_condition']
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return f"Error updating employee: {str(e)}"
    return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>')
def delete(id):
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error deleting employee: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)