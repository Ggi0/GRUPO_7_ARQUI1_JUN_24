from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({
        "users" : [
            "arman",
            "zack",
            "tin"
        ]   
    })

if __name__ == '__main__':
    app.run(debug=True,port=8000)