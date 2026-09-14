from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_secreta_agro'

# Configuração do Banco de Dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    # Perfil: 'comum' (Operador), 'supervisor' (Gerente) ou 'admin' (Administrador)
    perfil = db.Column(db.String(20), default='comum') 

class RegistroCombustivel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maquina = db.Column(db.String(100), nullable=False)
    litros = db.Column(db.Float, nullable=False)
    horas_trabalhadas = db.Column(db.Float, nullable=False)
    consumo_medio = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)

# Criar banco de dados e usuário admin padrão
with app.app_context():
    db.create_all()

    admin = Usuario.query.filter_by(email='admin@email.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador Principal',
            email='admin@email.com',
            senha=generate_password_hash('123456'),
            perfil='admin'
        )
        db.session.add(admin)
        db.session.commit()

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            session['perfil'] = usuario.perfil
            return redirect(url_for('index'))
        else:
            flash('E-mail ou senha incorretos!', 'erro')
            
    return render_template('login.html')

@app.route('/cadastro-usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado!', 'erro')
            return redirect(url_for('cadastrar_usuario'))

        # Todo novo cadastro começa como Operador ('comum')
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            perfil='comum'
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login.', 'sucesso')
        return redirect(url_for('login'))

    return render_template('cadastro_usuario.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ROTAS PRINCIPAIS DE COMBUSTÍVEL ---
@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['usuario_id'])
    registros = RegistroCombustivel.query.all()
    
    return render_template('index.html', registros=registros, usuario=usuario)

@app.route('/abastecimento', methods=['GET', 'POST'])
def registrar_abastecimento():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Todos os usuários autenticados (comum, supervisor, admin) podem registrar
    if request.method == 'POST':
        maquina = request.form.get('maquina')
        litros = float(request.form.get('litros'))
        horas = float(request.form.get('horas'))
        valor_litro = float(request.form.get('valor_litro'))
        
        consumo = round(litros / horas, 2) if horas > 0 else 0
        total = round(litros * valor_litro, 2)

        novo = RegistroCombustivel(
            maquina=maquina,
            litros=litros,
            horas_trabalhadas=horas,
            consumo_medio=consumo,
            valor_total=total
        )
        db.session.add(novo)
        db.session.commit()
        flash('Abastecimento registrado com sucesso!', 'sucesso')
        return redirect(url_for('index'))
        
    return render_template('cadastro.html')

@app.route('/deletar/<int:item_id>', methods=['POST'])
def deletar(item_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])
    # Apenas Supervisor e Admin podem excluir registros
    if usuario.perfil in ['supervisor', 'admin']:
        registro = RegistroCombustivel.query.get(item_id)
        if registro:
            db.session.delete(registro)
            db.session.commit()
            flash('Registro excluído com sucesso!', 'sucesso')
    else:
        flash('Você não tem permissão para excluir registros!', 'erro')

    return redirect(url_for('index'))

# --- PAINEL DE GESTÃO DE USUÁRIOS (APENAS ADMIN) ---
@app.route('/admin/permissoes')
def permissoes():
    if 'usuario_id' not in session or session.get('perfil') != 'admin':
        flash('Acesso restrito a Administradores!', 'erro')
        return redirect(url_for('index'))

    # Exibe todos os usuários menos o próprio Admin logado
    usuarios = Usuario.query.filter(Usuario.id != session['usuario_id']).all()
    return render_template('permissoes.html', usuarios=usuarios)

@app.route('/admin/alterar-perfil/<int:user_id>', methods=['POST'])
def alterar_perfil(user_id):
    if session.get('perfil') == 'admin':
        usuario = Usuario.query.get(user_id)
        novo_perfil = request.form.get('novo_perfil')
        if usuario and novo_perfil in ['comum', 'supervisor', 'admin']:
            usuario.perfil = novo_perfil
            db.session.commit()
            flash(f'Perfil do usuário {usuario.nome} alterado para {novo_perfil}!', 'sucesso')
    return redirect(url_for('permissoes'))

@app.route('/admin/excluir-usuario/<int:user_id>', methods=['POST'])
def excluir_usuario(user_id):
    if session.get('perfil') == 'admin':
        usuario = Usuario.query.get(user_id)
        # Evita a exclusão do próprio usuário conectado
        if usuario and usuario.id != session['usuario_id']:
            db.session.delete(usuario)
            db.session.commit()
            flash('Conta do usuário excluída com sucesso!', 'sucesso')
    return redirect(url_for('permissoes'))

if __name__ == '__main__':
    app.run(debug=True)