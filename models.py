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
    examinations = db.relationship('Examination', backref='employee', lazy=True)

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
            examinations.append({
                'exam_type': exam_type,
                'exam_date': datetime.strptime(form[date_key], '%Y-%m-%d'),
                'diagnosis': form.get(diag_key)
            })
    return employee_data, examinations

def calculate_expiry(employee):
    vlk_expiry = kmo_expiry = umo_expiry = kmo2_expiry = None
    vlk_days_left = kmo_days_left = umo_days_left = kmo2_days_left = float('inf')
    notes = []

    for exam in employee.examinations:
        if exam.exam_type == 'ВЛК':
            vlk_expiry = exam.exam_date + relativedelta(months=12)
            vlk_days_left = (vlk_expiry - datetime.now().date()).days
            if vlk_days_left < 0:
                notes.append(f"Просрочен ВЛК ({-vlk_days_left} дней)")
            elif vlk_days_left <= 30:
                notes.append(f"ВЛК: {vlk_days_left} дней до истечения")
        elif exam.exam_type == 'КМО':
            kmo_expiry = exam.exam_date + relativedelta(months=3)
            kmo_days_left = (kmo_expiry - datetime.now().date()).days
            if kmo_days_left < 0:
                notes.append(f"Просрочен КМО ({-kmo_days_left} дней)")
            elif kmo_days_left <= 30:
                notes.append(f"КМО: {kmo_days_left} дней до истечения")
        elif exam.exam_type == 'УМО':
            umo_expiry = exam.exam_date + relativedelta(months=3)
            umo_days_left = (umo_expiry - datetime.now().date()).days
            if umo_days_left < 0:
                notes.append(f"Просрочен УМО ({-umo_days_left} дней)")
            elif umo_days_left <= 30:
                notes.append(f"УМО: {umo_days_left} дней до истечения")
        elif exam.exam_type == 'КМО2':
            kmo2_expiry = exam.exam_date + relativedelta(months=3)
            kmo2_days_left = (kmo2_expiry - datetime.now().date()).days
            if kmo2_days_left < 0:
                notes.append(f"Просрочен КМО2 ({-kmo2_days_left} дней)")
            elif kmo2_days_left <= 30:
                notes.append(f"КМО2: {kmo2_days_left} дней до истечения")

    min_days_left = min(vlk_days_left, kmo_days_left, umo_days_left, kmo2_days_left)

    # Автоматическое обновление статуса и примечания
    if min_days_left < 0:
        employee.preflight_condition = 'Отстранен'
        if not notes:
            notes.append("Просрочен осмотр")
    elif not employee.examinations:
        employee.preflight_condition = 'Отстранен'
        notes.append("Нет осмотров")
    else:
        employee.preflight_condition = 'Допущен'

    # Обновляем примечание
    employee.note = "; ".join(notes) if notes else employee.note

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
        'min_days_left': min_days_left if min_days_left != float('inf') else None
    }