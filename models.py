from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

db = SQLAlchemy()

PREFLIGHT_CONDITIONS = ['Допущен', 'Отстранен']
EXAM_TYPES = ['ВЛК', 'КМО', 'УМО', 'КМО2']

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    order_no = db.Column(db.String(50), nullable=False)
    preflight_condition = db.Column(db.String(100), default='Допущен')
    note = db.Column(db.String(200))
    examinations = db.relationship('Examination', backref='employee', lazy=True, cascade='all, delete')

class Examination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    diagnosis = db.Column(db.String(200))

def process_employee_form(form):
    preflight = form['preflight_condition'] if form['preflight_condition'] in PREFLIGHT_CONDITIONS else 'Допущен'
    employee_data = {
        'fio': form['fio'],
        'birth_date': datetime.strptime(form['birth_date'], '%Y-%m-%d') if form['birth_date'] else None,
        'position': form['position'],
        'order_no': form['order_no'],
        'preflight_condition': preflight,
        'note': form['note'] if form['note'] else None
    }
    examinations = []
    for exam_type in EXAM_TYPES:
        date_key = f"{exam_type.lower()}_date"
        diag_key = f"{exam_type.lower()}_diagnosis"
        if form.get(date_key):
            try:
                exam_date = datetime.strptime(form[date_key], '%Y-%m-%d')
                examinations.append({
                    'exam_type': exam_type,
                    'exam_date': exam_date,
                    'diagnosis': form.get(diag_key)
                })
            except ValueError:
                print(f"Ошибка формата даты для {exam_type}: {form[date_key]}")
    return employee_data, examinations

def calculate_expiry(employee):
    vlk_date = None
    vlk_expiry = kmo_expiry = umo_expiry = kmo2_expiry = None
    vlk_days_left = kmo_days_left = umo_days_left = kmo2_days_left = float('inf')
    nearest_exam = None
    min_days_left = float('inf')

    # Находим дату последнего ВЛК
    for exam in employee.examinations:
        if exam.exam_type == 'ВЛК':
            if not vlk_date or exam.exam_date > vlk_date:
                vlk_date = exam.exam_date

    if vlk_date:
        # Вычисляем сроки относительно последнего ВЛК
        vlk_expiry = vlk_date + relativedelta(months=12)
        vlk_days_left = (vlk_expiry - datetime.now().date()).days
        if vlk_days_left < min_days_left:
            min_days_left = vlk_days_left
            nearest_exam = 'ВЛК'

        kmo_expiry = vlk_date + relativedelta(months=3)
        kmo_days_left = (kmo_expiry - datetime.now().date()).days
        if kmo_days_left < min_days_left:
            min_days_left = kmo_days_left
            nearest_exam = 'КМО'

        umo_expiry = vlk_date + relativedelta(months=6)
        umo_days_left = (umo_expiry - datetime.now().date()).days
        if umo_days_left < min_days_left:
            min_days_left = umo_days_left
            nearest_exam = 'УМО'

        kmo2_expiry = vlk_date + relativedelta(months=9)
        kmo2_days_left = (kmo2_expiry - datetime.now().date()).days
        if kmo2_days_left < min_days_left:
            min_days_left = kmo2_days_left
            nearest_exam = 'КМО2'

    # Устанавливаем статус "Отстранен", если есть просрочка
    if min_days_left < 0:
        employee.preflight_condition = 'Отстранен'
    elif not employee.examinations:
        employee.preflight_condition = 'Отстранен'
    else:
        employee.preflight_condition = 'Допущен'

    # Примечание не трогаем

    return {
        'employee': employee,
        'vlk_expiry': vlk_expiry,
        'kmo_expiry': kmo_expiry,
        'umo_expiry': umo_expiry,
        'kmo2_expiry': kmo2_expiry,
        'vlk_days_left': vlk_days_left if vlk_days_left != float('inf') else None,
        'kmo_days_left': kmo_days_left if kmo_days_left != float('inf') else None,
        'umo_days_left': umo_days_left if umo_days_left != float('inf') else None,
        'kmo2_days_left': kmo2_days_left if kmo2_days_left != float('inf') else None,
        'min_days_left': min_days_left if min_days_left != float('inf') else None,
        'nearest_exam': nearest_exam
    }