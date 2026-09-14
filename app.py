from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

machines = [
    {
        'id': 1,
        'name': 'Trator CAT 320',
        'notes': 'Frota A',
        'hourmeter': 1200,
        'last_service_hour': 1000,
        'next_service_at': 1250,
        'service_interval': 250,
        'service_status': 'warning',
        'hours_to_service': 50
    }
]

@app.route('/')
def home():
    return render_template('Alertas_de_manutencao_preventiva.html', machines=machines)

@app.route('/update_hourmeter/<int:machine_id>', methods=['POST'])
def update_hourmeter(machine_id):
    for m in machines:
        if m['id'] == machine_id:
            m['hourmeter'] += 10
            m['hours_to_service'] = m['next_service_at'] - m['hourmeter']
            if m['hours_to_service'] <= 0:
                m['service_status'] = 'urgent'
    return redirect(url_for('home'))

@app.route('/complete_service/<int:machine_id>', methods=['POST'])
def complete_service(machine_id):
    for m in machines:
        if m['id'] == machine_id:
            m['last_service_hour'] = m['hourmeter']
            m['next_service_at'] = m['hourmeter'] + m['service_interval']
            m['hours_to_service'] = m['service_interval']
            m['service_status'] = 'normal'
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)