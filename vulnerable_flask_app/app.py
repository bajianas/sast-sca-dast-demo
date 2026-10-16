import os
import subprocess
from flask import Flask, request
from flask_wtf.csrf import CSRFProtect
from markupsafe import escape

app = Flask(__name__)

# Secret lu depuis une variable d'environnement (jamais en dur)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "")

# Protection CSRF activée
csrf = CSRFProtect(app)

# Seules ces commandes sont autorisées (liste blanche)
ALLOWED_COMMANDS = {
    "ls": ["ls", "-la"],
    "date": ["date"],
    "whoami": ["whoami"],
}


@app.route('/')
def index():
    return """
    <h1>Welcome to our Flask App</h1>
    <ul>
        <li><a href="/hello?name=World">Hello Page</a></li>
        <li><a href="/execute?cmd=ls">Execute Command Page</a></li>
        <li><a href="/admin">Admin Area</a></li>
    </ul>
    """


@app.route('/hello')
def hello():
    name = escape(request.args.get('name', 'Guest'))  # corrige le XSS
    return f"""
    <h1>Hello Page</h1>
    <p>Hello, {name}!</p>
    <p><a href="/">Back to Homepage</a></p>
    """


@app.route('/execute')
def execute():
    key = request.args.get('cmd', 'ls')
    command = ALLOWED_COMMANDS.get(key)
    if command is None:
        return "<p>Commande non autorisée</p>", 403
    # Pas de shell=True : liste d'arguments
    result = subprocess.run(command, capture_output=True, text=True)
    return f"""
    <h1>Execute Command Page</h1>
    <p>Executing command: <code>{escape(key)}</code></p>
    <pre>{escape(result.stdout)}</pre>
    <pre style="color: red;">{escape(result.stderr)}</pre>
    <p><a href="/">Back to Homepage</a></p>
    """


@app.route('/admin')
def admin():
    # La clé secrète n'est plus affichée
    return """
    <h1>Admin Area</h1>
    <p>Accès restreint.</p>
    <p><a href="/">Back to Homepage</a></p>
    """


if __name__ == '__main__':
    # Hôte lu depuis l'environnement : 127.0.0.1 par défaut
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    app.run(debug=False, host=host)
