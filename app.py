from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

registros = []

@app.route("/")
def inicio():
    return redirect(url_for("registro_horas"))

@app.route("/registro-horas", methods=["GET", "POST"])
def registro_horas():
    if request.method == "POST":
        maquina = request.form["maquina"]
        data_raw = request.form["data"]
        horas = request.form["horas"]
        descricao = request.form["descricao"]

        # Converte a data do formato do navegador (AAAA-MM-DD) para (DD/MM/AAAA)
        if data_raw:
            data_formatada = datetime.strptime(data_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
        else:
            data_formatada = ""

        registros.append({
            "maquina": maquina,
            "data": data_formatada,
            "horas": horas,
            "descricao": descricao
        })

        return redirect(url_for("registro_horas"))

    return render_template(
        "registro_horas.html",
        registros=registros
    )

@app.route("/excluir/<int:index>", methods=["POST"])
def excluir(index):
    if 0 <= index < len(registros):
        registros.pop(index)
    return redirect(url_for("registro_horas"))

@app.route("/sair")
def sair():
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema encerrado</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .mensagem {
            background: white;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 20px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="mensagem">
        <h1>Sistema encerrado</h1>
        <p>Você saiu do registro de horas.</p>
        <a href="/">Voltar para o sistema</a>
    </div>
</body>
</html>"""

if __name__ == "__main__":
    app.run(debug=True)