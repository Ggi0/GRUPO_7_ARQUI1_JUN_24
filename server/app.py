from flask import Flask, request, jsonify
from flask_cors import CORS

# * Initialize Flask app
app = Flask(__name__)

# * Enable CORS for all routes of the app 
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


"""
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({
        "users" : [
            "arman",
            "zack",
            "tin"
        ]   
    })
"""
@app.route('/api/onLED', methods=['POST'])
def handle_data():
    data = request.json
    selected_area = data.get('area')
    # Aquí puedes hacer lo que necesites con la variable 'selected_area'
    print("Área seleccionada:", selected_area)
    return 'Datos recibidos correctamente'

@app.route('/api/offLED', methods=['POST'])
def handle_data_1():
    data = request.json
    selected_area = data.get('area')
    # Aquí puedes hacer lo que necesites con la variable 'selected_area'
    print("Área seleccionada:", selected_area)
    print("Área seleccionada se apaga:", selected_area)
    return 'Datos recibidos correctamente'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
        
