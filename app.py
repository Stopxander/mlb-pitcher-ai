import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "MLB Pitcher AI is running"

@app.route("/data")
def get_data():
    url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"

    # Obtener datos de la API
    response = requests.get(url)
    data = response.json()

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
