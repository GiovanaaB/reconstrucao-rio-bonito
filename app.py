from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_insegura_trocar_no_env")


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    areas = conn.execute("SELECT * FROM areas ORDER BY prioridade DESC").fetchall()
    conn.close()

    return render_template("index.html", areas=areas)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        prioridade = request.form["prioridade"]

        conn = get_db()
        conn.execute(
            "INSERT INTO areas (nome, descricao, prioridade) VALUES (?, ?, ?)",
            (nome, descricao, prioridade)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = get_db()
        user = conn.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
        conn.close()

        if user and check_password_hash(user["senha"], senha):
            session["user"] = usuario
            return redirect("/")
        else:
            return "Login inválido"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


def criar_banco():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            prioridade INTEGER
        )
    """)

    senha_hash = generate_password_hash("admin")
    try:
        conn.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", senha_hash))
    except:
        pass

    conn.commit()
    conn.close()


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
