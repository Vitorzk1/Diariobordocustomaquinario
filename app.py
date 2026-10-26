from datetime import datetime
from functools import wraps
import os
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    current_user, logout_user
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-local-apenas-para-desenvolvimento")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agro.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar o sistema."
login_manager.login_message_category = "warning"


# ============================================================
# MODELOS
# ============================================================

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    # comum = operador, supervisor = gerencia registros,
    # admin = acesso administrativo completo
    perfil = db.Column(db.String(20), nullable=False, default="comum")

    registros_horas = db.relationship(
        "RegistroHora", backref="usuario", lazy=True,
        cascade="all, delete-orphan"
    )
    abastecimentos = db.relationship(
        "RegistroCombustivel", backref="usuario", lazy=True,
        cascade="all, delete-orphan"
    )


class Machine(db.Model):
    __tablename__ = "machine"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(255))
    hourmeter = db.Column(db.Float, default=0, nullable=False)
    last_service_hour = db.Column(db.Float, default=0, nullable=False)
    service_interval = db.Column(db.Float, default=250, nullable=False)
    next_service_at = db.Column(db.Float, default=250, nullable=False)

    checklists = db.relationship(
        "MaintenanceChecklist", backref="machine", lazy=True,
        cascade="all, delete-orphan"
    )
    registros_horas = db.relationship(
        "RegistroHora", backref="machine", lazy=True,
        cascade="all, delete-orphan"
    )
    abastecimentos = db.relationship(
        "RegistroCombustivel", backref="machine", lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def hours_to_service(self):
        return self.next_service_at - self.hourmeter

    @property
    def service_status(self):
        if self.hours_to_service <= 0:
            return "urgent"
        if self.hours_to_service <= 50:
            return "warning"
        return "normal"


class MaintenanceChecklist(db.Model):
    __tablename__ = "maintenance_checklist"

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False)
    task = db.Column(db.String(255), nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)


class RegistroHora(db.Model):
    __tablename__ = "registro_hora"

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horas = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, default="")


class RegistroCombustivel(db.Model):
    __tablename__ = "registro_combustivel"

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    data = db.Column(db.Date, nullable=False)
    litros = db.Column(db.Float, nullable=False)
    horas_trabalhadas = db.Column(db.Float, nullable=False)
    valor_litro = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)

    @property
    def consumo_medio(self):
        return round(self.litros / self.horas_trabalhadas, 2) if self.horas_trabalhadas > 0 else 0


@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(User, int(user_id))


# ============================================================
# UTILITÁRIOS
# ============================================================

def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.perfil != "admin":
            flash("Acesso permitido somente para administradores.", "danger")
            return redirect(url_for("dashboard"))
        return func(*args, **kwargs)
    return wrapper


def supervisor_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.perfil not in ["supervisor", "admin"]:
            flash("Você não possui permissão para esta ação.", "danger")
            return redirect(url_for("dashboard"))
        return func(*args, **kwargs)
    return wrapper


def create_default_checklist(machine):
    tasks = [
        ("Troca do óleo do motor e filtro", 250),
        ("Drenagem do decantador de água do diesel", 250),
        ("Limpeza/inspeção do filtro de ar do motor", 250),
        ("Verificação do nível de fluido hidráulico", 250),
        ("Troca de todos os filtros de combustível", 500),
        ("Substituição completa dos filtros de ar", 500),
        ("Troca do filtro de transmissão", 500),
        ("Lubrificação/engraxamento dos eixos", 500),
        ("Troca total do óleo hidráulico e transmissão", 1000),
        ("Substituição do líquido de arrefecimento", 1000),
        ("Regulagem de válvulas do motor", 1000),
        ("Inspeção do sistema de injeção e correias", 1000),
    ]
    for task, interval in tasks:
        db.session.add(MaintenanceChecklist(
            machine_id=machine.id,
            task=task,
            interval=interval,
            completed=False,
        ))


# ============================================================
# AUTENTICAÇÃO
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = User.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))

        flash("E-mail ou senha incorretos.", "danger")

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("cadastro"))

        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("cadastro"))

        usuario = User(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha, method="scrypt"),
            perfil="comum",
        )
        db.session.add(usuario)
        db.session.commit()
        flash("Cadastro realizado. Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("login"))


@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")


# ============================================================
# DASHBOARD / MÁQUINAS / MANUTENÇÃO
# ============================================================

@app.route("/")
@login_required
def dashboard():
    machines = Machine.query.order_by(Machine.name).all()
    total_horas = sum(r.horas for r in RegistroHora.query.all())
    total_litros = sum(r.litros for r in RegistroCombustivel.query.all())
    total_combustivel = sum(r.valor_total for r in RegistroCombustivel.query.all())

    return render_template(
        "dashboard.html",
        machines=machines,
        total_horas=total_horas,
        total_litros=total_litros,
        total_combustivel=total_combustivel,
    )


@app.route("/maquinas/adicionar", methods=["POST"])
@login_required
def add_machine():
    try:
        name = request.form.get("name", "").strip()
        notes = request.form.get("notes", "").strip()
        hourmeter = float(request.form.get("hourmeter", 0))
        service_interval = float(request.form.get("service_interval", 250))

        if not name or hourmeter < 0 or service_interval <= 0:
            raise ValueError

        machine = Machine(
            name=name,
            notes=notes,
            hourmeter=hourmeter,
            last_service_hour=hourmeter,
            service_interval=service_interval,
            next_service_at=hourmeter + service_interval,
        )
        db.session.add(machine)
        db.session.flush()
        create_default_checklist(machine)
        db.session.commit()
        flash("Máquina cadastrada com sucesso.", "success")
    except (TypeError, ValueError):
        db.session.rollback()
        flash("Informe valores válidos para a máquina.", "danger")

    return redirect(url_for("dashboard"))


@app.route("/maquinas/<int:machine_id>/excluir", methods=["POST"])
@supervisor_required
def delete_machine(machine_id):
    machine = db.get_or_404(Machine, machine_id)
    db.session.delete(machine)
    db.session.commit()
    flash("Máquina excluída.", "success")
    return redirect(url_for("dashboard"))


@app.route("/manutencao")
@login_required
def manutencao():
    machines = Machine.query.order_by(Machine.name).all()
    return render_template("manutencao.html", machines=machines)


@app.route("/manutencao/<int:machine_id>/concluir", methods=["POST"])
@supervisor_required
def complete_service(machine_id):
    machine = db.get_or_404(Machine, machine_id)
    machine.last_service_hour = machine.hourmeter
    machine.next_service_at = machine.hourmeter + machine.service_interval
    for checklist in machine.checklists:
        checklist.completed = False
    db.session.commit()
    flash(f"Manutenção da máquina {machine.name} registrada.", "success")
    return redirect(url_for("manutencao"))


@app.route("/checklist/<int:checklist_id>/alternar", methods=["POST"])
@login_required
def toggle_checklist(checklist_id):
    checklist = db.get_or_404(MaintenanceChecklist, checklist_id)
    checklist.completed = not checklist.completed
    db.session.commit()
    return redirect(url_for("manutencao"))


# ============================================================
# REGISTRO DE HORAS
# ============================================================

@app.route("/registro-horas", methods=["GET", "POST"])
@login_required
def registro_horas():
    machines = Machine.query.order_by(Machine.name).all()

    if request.method == "POST":
        try:
            machine_id = int(request.form.get("machine_id"))
            data = datetime.strptime(request.form.get("data", ""), "%Y-%m-%d").date()
            horas = float(request.form.get("horas", 0))
            descricao = request.form.get("descricao", "").strip()

            if horas <= 0:
                raise ValueError

            machine = db.get_or_404(Machine, machine_id)
            registro = RegistroHora(
                machine_id=machine.id,
                user_id=current_user.id,
                data=data,
                horas=horas,
                descricao=descricao,
            )
            db.session.add(registro)
            # O registro de horas passa a alimentar o horímetro da máquina.
            machine.hourmeter += horas
            db.session.commit()
            flash("Registro de horas inserido e horímetro atualizado.", "success")
            return redirect(url_for("registro_horas"))
        except (TypeError, ValueError):
            db.session.rollback()
            flash("Informe máquina, data e uma quantidade de horas válida.", "danger")

    if current_user.perfil == "admin":
        registros = RegistroHora.query.order_by(RegistroHora.data.desc(), RegistroHora.id.desc()).all()
    else:
        registros = RegistroHora.query.filter_by(user_id=current_user.id).order_by(
            RegistroHora.data.desc(), RegistroHora.id.desc()
        ).all()

    return render_template("registro_horas.html", registros=registros, machines=machines)


@app.route("/registro-horas/<int:registro_id>/excluir", methods=["POST"])
@supervisor_required
def delete_hour_record(registro_id):
    registro = db.get_or_404(RegistroHora, registro_id)
    # Ao excluir, desfazemos o incremento do horímetro para manter consistência.
    registro.machine.hourmeter = max(0, registro.machine.hourmeter - registro.horas)
    db.session.delete(registro)
    db.session.commit()
    flash("Registro de horas excluído.", "success")
    return redirect(url_for("registro_horas"))


# ============================================================
# REGISTRO DE COMBUSTÍVEL
# ============================================================

@app.route("/abastecimentos", methods=["GET", "POST"])
@login_required
def abastecimentos():
    machines = Machine.query.order_by(Machine.name).all()

    if request.method == "POST":
        try:
            machine_id = int(request.form.get("machine_id"))
            data = datetime.strptime(request.form.get("data", ""), "%Y-%m-%d").date()
            litros = float(request.form.get("litros", 0))
            horas = float(request.form.get("horas", 0))
            valor_litro = float(request.form.get("valor_litro", 0))

            if litros <= 0 or horas <= 0 or valor_litro < 0:
                raise ValueError

            machine = db.get_or_404(Machine, machine_id)
            registro = RegistroCombustivel(
                machine_id=machine.id,
                user_id=current_user.id,
                data=data,
                litros=litros,
                horas_trabalhadas=horas,
                valor_litro=valor_litro,
                valor_total=round(litros * valor_litro, 2),
            )
            db.session.add(registro)
            db.session.commit()
            flash("Abastecimento registrado com sucesso.", "success")
            return redirect(url_for("abastecimentos"))
        except (TypeError, ValueError):
            db.session.rollback()
            flash("Informe valores válidos para o abastecimento.", "danger")

    registros = RegistroCombustivel.query.order_by(
        RegistroCombustivel.data.desc(), RegistroCombustivel.id.desc()
    ).all()
    return render_template("abastecimentos.html", registros=registros, machines=machines)


@app.route("/abastecimentos/<int:registro_id>/excluir", methods=["POST"])
@supervisor_required
def delete_fuel_record(registro_id):
    registro = db.get_or_404(RegistroCombustivel, registro_id)
    db.session.delete(registro)
    db.session.commit()
    flash("Abastecimento excluído.", "success")
    return redirect(url_for("abastecimentos"))


# ============================================================
# ADMINISTRAÇÃO DE USUÁRIOS
# ============================================================

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "admin.html",
        quantidade_usuarios=User.query.count(),
        quantidade_maquinas=Machine.query.count(),
        quantidade_horas=RegistroHora.query.count(),
        quantidade_abastecimentos=RegistroCombustivel.query.count(),
    )


@app.route("/admin/usuarios")
@admin_required
def usuarios():
    return render_template("usuarios.html", usuarios=User.query.order_by(User.nome).all())


@app.route("/admin/usuarios/<int:user_id>/perfil", methods=["POST"])
@admin_required
def alterar_perfil(user_id):
    usuario = db.get_or_404(User, user_id)
    novo_perfil = request.form.get("perfil")
    if usuario.id == current_user.id:
        flash("Você não pode alterar seu próprio perfil.", "warning")
    elif novo_perfil in ["comum", "supervisor", "admin"]:
        usuario.perfil = novo_perfil
        db.session.commit()
        flash("Perfil atualizado.", "success")
    else:
        flash("Perfil inválido.", "danger")
    return redirect(url_for("usuarios"))


@app.route("/admin/usuarios/<int:user_id>/excluir", methods=["POST"])
@admin_required
def excluir_usuario(user_id):
    usuario = db.get_or_404(User, user_id)
    if usuario.id == current_user.id:
        flash("Você não pode excluir sua própria conta.", "warning")
    else:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuário excluído.", "success")
    return redirect(url_for("usuarios"))


# ============================================================
# INICIALIZAÇÃO
# ============================================================

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(email="admin@email.com").first()
    if not admin:
        admin = User(
            nome="Administrador",
            email="admin@email.com",
            senha=generate_password_hash(os.environ.get("INITIAL_ADMIN_PASSWORD", "admin123"), method="scrypt"),
            perfil="admin",
        )
        db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
