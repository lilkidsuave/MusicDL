from flask import Flask, request, render_template, redirect, url_for, flash
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    services = ["spotify", "applemusic", "tidal"]  # Add more services as needed
    return render_template('index.html', services=services)

@app.route('/search', methods=['POST'])
def search():
    service = request.form['service']
    query = request.form['query']
    command = f'./orpheus.py search {service} track "{query}"'  # Modify this based on your requirements

    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        flash(result, 'success')
    except subprocess.CalledProcessError as e:
        flash(e.output, 'error')

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
