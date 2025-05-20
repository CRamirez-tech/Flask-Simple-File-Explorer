import os
from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from datetime import datetime

port = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
BASE_DIR = os.path.abspath("drive")  # Carpeta raíz para archivos

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def index(req_path):
    abs_path = os.path.join(BASE_DIR, req_path)

    if not os.path.exists(abs_path):
        return "Ruta no encontrada", 404

    if os.path.isfile(abs_path):
        return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path), as_attachment=True)

    files = os.listdir(abs_path)
    file_list = []
    for f in files:
        file_path = os.path.join(abs_path, f)
        file_list.append({
            'name': f,
            'is_dir': os.path.isdir(file_path),
            'size': os.path.getsize(file_path) if os.path.isfile(file_path) else '',
            'path': os.path.relpath(file_path, BASE_DIR),
            "modified": datetime.fromtimestamp(os.path.getmtime(file_path))
        })

    return render_template('index.html', files=file_list, current_path=req_path)

@app.route('/upload', methods=['POST'])
def upload():
    current_path = request.form.get("path", "")
    file = request.files['file']
    upload_path = os.path.join(BASE_DIR, current_path)
    file.save(os.path.join(upload_path, file.filename))
    return redirect(url_for('index', req_path=current_path))

@app.route('/delete', methods=['POST'])
def delete():
    file_path = os.path.join(BASE_DIR, request.form['file'])
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
            os.rmdir(file_path)
        else:
            os.remove(file_path)
    return redirect(url_for('index', req_path=os.path.dirname(request.form['file'])))

if __name__ == '__main__':
    os.makedirs(BASE_DIR, exist_ok=True)
    app.run(host='0.0.0.0', debug=True, port=port)
