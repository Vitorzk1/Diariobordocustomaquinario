from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# =========================
# CONFIGURAÇÃO DO BANCO
# =========================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maquinario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =========================
# MODELO DAS MÁQUINAS
# =========================

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(255))

    hourmeter = db.Column(db.Float, default=0)

    last_service_hour = db.Column(db.Float, default=0)

    service_interval = db.Column(db.Float, default=250)

    next_service_at = db.Column(db.Float, default=250)

    # Relacionamento com as checklists
    checklists = db.relationship(
        'MaintenanceChecklist',
        backref='machine',
        lazy=True,
        cascade='all, delete-orphan'
    )


# =========================
# MODELO DAS CHECKLISTS
# =========================

class MaintenanceChecklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    machine_id = db.Column(
        db.Integer,
        db.ForeignKey('machine.id'),
        nullable=False
    )

    task = db.Column(db.String(255), nullable=False)

    # 250, 500 ou 1000 horas
    interval = db.Column(db.Integer, nullable=False)

    completed = db.Column(db.Boolean, default=False)


# =========================
# CRIAÇÃO DO BANCO
# =========================

with app.app_context():
    db.create_all()


# =========================
# FUNÇÃO PARA CRIAR CHECKLIST
# =========================

def create_default_checklist(machine):

    tasks = [

        # 250 HORAS
        ("Troca do óleo do motor e filtro", 250),
        ("Drenagem do decantador de água do diesel", 250),
        ("Limpeza/inspeção do filtro de ar do motor", 250),
        ("Verificação do nível de fluido hidráulico", 250),

        # 500 HORAS
        ("Troca de todos os filtros de combustível", 500),
        ("Substituição completa dos filtros de ar", 500),
        ("Troca do filtro de transmissão", 500),
        ("Lubrificação/engraxamento dos eixos", 500),

        # 1000 HORAS
        ("Troca total do óleo hidráulico e transmissão", 1000),
        ("Substituição do líquido de arrefecimento", 1000),
        ("Regulagem de válvulas do motor", 1000),
        ("Inspeção do sistema de injeção e correias", 1000)
    ]

    for task, interval in tasks:

        checklist = MaintenanceChecklist(
            machine_id=machine.id,
            task=task,
            interval=interval,
            completed=False
        )

        db.session.add(checklist)


# =========================
# FUNÇÃO PARA CALCULAR STATUS
# =========================

def calculate_status(machine):

    machine.next_service_at = (
        machine.last_service_hour +
        machine.service_interval
    )

    machine.hours_to_service = (
        machine.next_service_at -
        machine.hourmeter
    )

    if machine.hours_to_service <= 0:

        machine.service_status = 'urgent'

    elif machine.hours_to_service <= 50:

        machine.service_status = 'warning'

    else:

        machine.service_status = 'normal'


# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route('/')
def home():

    machines = Machine.query.all()

    for machine in machines:
        calculate_status(machine)

    db.session.commit()

    return render_template(
        'Alertas_de_manutencao_preventiva.html',
        machines=machines
    )


# =========================
# CADASTRAR MÁQUINA
# =========================

@app.route('/add_machine', methods=['POST'])
def add_machine():

    name = request.form.get('name')
    notes = request.form.get('notes')

    hourmeter = float(
        request.form.get('hourmeter', 0)
    )

    service_interval = float(
        request.form.get('service_interval', 250)
    )

    machine = Machine(
        name=name,
        notes=notes,
        hourmeter=hourmeter,
        last_service_hour=hourmeter,
        service_interval=service_interval,
        next_service_at=hourmeter + service_interval
    )

    db.session.add(machine)

    db.session.commit()

    # Cria as checklists
    create_default_checklist(machine)

    db.session.commit()

    return redirect(url_for('home'))


# =========================
# EXCLUIR MÁQUINA
# =========================

@app.route('/delete_machine/<int:machine_id>', methods=['POST'])
def delete_machine(machine_id):

    machine = Machine.query.get_or_404(machine_id)

    db.session.delete(machine)

    db.session.commit()

    return redirect(url_for('home'))


# =========================
# ADICIONAR HORAS
# =========================

@app.route(
    '/update_hourmeter/<int:machine_id>',
    methods=['POST']
)
def update_hourmeter(machine_id):

    machine = Machine.query.get_or_404(machine_id)

    hours = float(
        request.form.get('hours', 10)
    )

    machine.hourmeter += hours

    calculate_status(machine)

    db.session.commit()

    return redirect(url_for('home'))


# =========================
# REGISTRAR MANUTENÇÃO
# =========================

@app.route(
    '/complete_service/<int:machine_id>',
    methods=['POST']
)
def complete_service(machine_id):

    machine = Machine.query.get_or_404(machine_id)

    machine.last_service_hour = machine.hourmeter

    machine.next_service_at = (
        machine.hourmeter +
        machine.service_interval
    )

    # Reinicia as checklists
    for checklist in machine.checklists:

        checklist.completed = False

    calculate_status(machine)

    db.session.commit()

    return redirect(url_for('home'))


# =========================
# MARCAR CHECKLIST
# =========================

@app.route(
    '/toggle_checklist/<int:checklist_id>',
    methods=['POST']
)
def toggle_checklist(checklist_id):

    checklist = MaintenanceChecklist.query.get_or_404(
        checklist_id
    )

    checklist.completed = not checklist.completed

    db.session.commit()

    return redirect(url_for('home'))


# =========================
# EXECUTAR
# =========================

if __name__ == '__main__':
    app.run(debug=True)