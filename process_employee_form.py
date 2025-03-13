from datetime import datetime
def process_employee_form(form):
    return {
        'fio': form['fio'],
        'birth_date': datetime.strptime(form['birth_date'], '%Y-%m-%d'),
        'position': form['position'],
        'order_no': form['order_no'],
        'vlk_date': datetime.strptime(form['vlk_date'], '%Y-%m-%d') if form['vlk_date'] else None,
        'vlk_diagnosis': form['vlk_diagnosis'],
        'kmo_date': datetime.strptime(form['kmo_date'], '%Y-%m-%d') if form['kmo_date'] else None,
        'kmo_diagnosis': form['kmo_diagnosis'],
        'umo_date': datetime.strptime(form['umo_date'], '%Y-%m-%d') if form['umo_date'] else None,
        'umo_diagnosis': form['umo_diagnosis'],
        'kmo2_date': datetime.strptime(form['kmo2_date'], '%Y-%m-%d') if form['kmo2_date'] else None,
        'kmo2_diagnosis': form['kmo2_diagnosis'],
        'preflight_condition': form['preflight_condition']
    }