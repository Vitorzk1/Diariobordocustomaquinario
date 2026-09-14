from datetime import datetime
from functools import wraps
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user,
    logout_user
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configurações do App e Banco de Dados
app.config["SECRET_KEY"] = "123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sistema.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar essa página."
login_manager.login_message_category = "warning"

#===========================================================
#                      MODELS
#===========================================================

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default="usuario")
    
    registros = db.relationship(
        'RegistroMaquina', 
        backref='usuario', 
        lazy=True, 
        cascade="all, delete-orphan"
    )

class RegistroMaquina(db.Model):
    __tablename__ = "registro_maquina"
    
    id = db.Column(db.Integer, primary_key=True)
    maquina = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(20), nullable=False)
    horas = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(User, int(user_id))

#===========================================================
#                      DECORATORS
#===========================================================

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.perfil != "admin":
            flash("Acesso negado. Apenas administradores.", "danger")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

#===========================================================
#                ROTAS DE AUTENTICAÇÃO
#===========================================================

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("registro_horas"))
    return redirect(url_for("login"))

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("registro_horas"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        perfil = request.form.get("perfil", "usuario")

        usuario_existente = User.query.filter_by(email=email).first()
        if usuario_existente:
            flash("E-mail já cadastrado. Faça login.", "danger")
            return redirect(url_for("login"))

        novo_usuario = User(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha, method='scrypt'),
            perfil=perfil
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("registro_horas"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = User.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("registro_horas"))
        
        flash("E-mail ou senha incorretos.", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("login"))

@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html", usuario=current_user)

#===========================================================
#            REGISTRO DE MÁQUINAS (SISTEMA)
#===========================================================

@app.route("/registro-horas", methods=["GET", "POST"])
@login_required
def registro_horas():
    if request.method == "POST":
        maquina = request.form.get("maquina", "").strip()
        data_raw = request.form.get("data", "")
        horas = request.form.get("horas", "").strip()
        descricao = request.form.get("descricao", "").strip()

        try:
            data_formatada = datetime.strptime(data_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            data_formatada = data_raw

        novo_registro = RegistroMaquina(
            maquina=maquina,
            data=data_formatada,
            horas=horas,
            descricao=descricao,
            user_id=current_user.id
        )
        
        db.session.add(novo_registro)
        db.session.commit()
        flash("Registro inserido com sucesso!", "success")
        return redirect(url_for("registro_horas"))

    if current_user.perfil == "admin":
        registros = RegistroMaquina.query.all()
    else:
        registros = RegistroMaquina.query.filter_by(user_id=current_user.id).all()

    return render_template("registro_horas.html", registros=registros)

@app.route("/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    registro = db.get_or_404(RegistroMaquina, id)
    
    if current_user.perfil == "admin" or registro.user_id == current_user.id:
        db.session.delete(registro)
        db.session.commit()
        flash("Registro excluído com sucesso!", "success")
    else:
        flash("Você não tem permissão para excluir este registro.", "danger")

    return redirect(url_for("registro_horas"))

#===========================================================
#              DASHBOARD E PAINEL ADMIN
#===========================================================

@app.route("/admin/dashboard")
@login_required
@admin_required
def dashboard():
    quantidade_usuarios = User.query.count()
    quantidade_registros = RegistroMaquina.query.count()
    return render_template(
        "admin_dashboard.html",
        quantidade=quantidade_usuarios,
        total_registros=quantidade_registros
    )

@app.route("/admin/usuarios")
@login_required
@admin_required
def usuarios():
    lista_usuarios = User.query.all()
    return render_template("usuarios.html", usuarios=lista_usuarios)

@app.route("/admin/alterar_perfil/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def alterar_perfil(user_id):
    usuario = db.get_or_404(User, user_id)

    if usuario.id == current_user.id:
        flash("Você não pode alterar seu próprio perfil.", "warning")
        return redirect(url_for("usuarios"))

    novo_perfil = request.form.get("perfil")
    if novo_perfil in ["admin", "usuario"]:
        usuario.perfil = novo_perfil
        db.session.commit()
        flash(f"Perfil de {usuario.nome} atualizado para {novo_perfil}!", "success")
    else:
        flash("Perfil inválido selecionado.", "danger")

    return redirect(url_for("usuarios"))

@app.route("/admin/deletar_usuario/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def deletar_usuario(user_id):
    usuario = db.get_or_404(User, user_id)

    if usuario.id == current_user.id:
        flash("Você não pode deletar a sua própria conta.", "warning")
        return redirect(url_for("usuarios"))

    db.session.delete(usuario)
    db.session.commit()
    flash(f"Usuário {usuario.nome} e seus registros foram removidos com sucesso.", "success")
    return redirect(url_for("usuarios"))

#===========================================================
#            INICIALIZAÇÃO DO BANCO DE DADOS
#===========================================================

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email="admin@email.com").first()
    if not admin:
        admin = User(
            nome="Admin",
            email="admin@email.com",
            senha=generate_password_hash("admin123", method='scrypt'),
            perfil="admin"
        )
        db.session.add(admin)
        db.session.commit()

#===========================================================
#                         EXECUÇÃO
#===========================================================

if __name__ == "__main__":
    app.run(debug=True)