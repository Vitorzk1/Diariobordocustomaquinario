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
        data = request.form["data"]
        horas = request.form["horas"]
        descricao = request.form["descricao"]

        registros.append({
            "maquina": maquina,
            "data": data,
            "horas": horas,
            "descricao": descricao
        })

        return redirect(url_for("registro_horas"))

    return render_template("registro_horas.html", registros=registros)


if __name__ == "__main__":
    app.run(debug=True)
