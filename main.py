import os
from flask import Flask, request, jsonify, render_template, abort

# --- НАСТРОЙКА ---
app = Flask(__name__, static_folder='static', template_folder='templates')

HOME_DIR = os.path.expanduser("~")
DATA_DIR = os.path.join(HOME_DIR, "collected_data")

# --- API ЭНДПОИНТ ДЛЯ ПРИЕМА ДАННЫХ ---
@app.route('/collect', methods=['POST'])
def collect_data():
    try:
        # Получаем JSON из тела запроса
        info = request.get_json()
        folder_name = os.path.basename(info['folder_name'])
        file_name = os.path.basename(info['file_name'])
        
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        target_dir = os.path.join(DATA_DIR, folder_name)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(info['content'])
        
        return jsonify({"status": "success", "message": "Data saved."}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- ЭНДПОИНТЫ ДЛЯ ПРОСМОТРА ДАННЫХ ---
@app.route('/')
def list_computers():
    computers = []
    if os.path.isdir(DATA_DIR):
        computers = sorted([d for d in os.listdir(DATA_DIR) 
                          if os.path.isdir(os.path.join(DATA_DIR, d))])
    return render_template("index.html", computers=computers)

@app.route('/<computer_name>')
def view_computer(computer_name):
    computer_path = os.path.join(DATA_DIR, os.path.basename(computer_name))
    if not os.path.isdir(computer_path):
        abort(404)
    
    files = sorted([f for f in os.listdir(computer_path) 
                   if os.path.isfile(os.path.join(computer_path, f))])
    return render_template("computer_view.html", 
                         computer_name=computer_name, 
                         files=files)

@app.route('/<computer_name>/<file_name>')
def view_file(computer_name, file_name):
    file_path = os.path.join(DATA_DIR, 
                           os.path.basename(computer_name), 
                           os.path.basename(file_name))
    
    if not os.path.isfile(file_path):
        abort(404)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return render_template("file_view.html", 
                         computer_name=computer_name, 
                         file_name=file_name, 
                         content=content)

# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)