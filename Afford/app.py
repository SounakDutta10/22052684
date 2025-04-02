from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# API Endpoints
REGISTER_URL = "http://20.244.56.144/evaluation-service/register"
AUTH_URL = "http://20.244.56.144/evaluation-service/auth"
TEST_SERVER_URL = "http://20.244.56.144/evaluation-service/numbers/"  # To fetch numbers

# Replace with your credentials
credentials = {
    "email": "your_email@domain.com",
    "name": "Your Name",
    "mobileNo": "9999999999",
    "githubUsername": "your_github",
    "rollNo": "your_roll_no",
    "collegeName": "Your College",
    "accessCode": "your_access_code"
}

# Rolling Window Storage
WINDOW_SIZE = 10
stored_numbers = []

def register():
    """ Registers the user on the test server and retrieves client ID & secret. """
    response = requests.post(REGISTER_URL, json=credentials)
    if response.status_code == 200:
        return response.json()
    return None

def get_auth_token(client_id, client_secret):
    """ Authenticates and retrieves a token for API calls. """
    auth_data = {"clientID": client_id, "clientSecret": client_secret}
    response = requests.post(AUTH_URL, json=auth_data)
    if response.status_code == 200:
        return response.json().get("token")
    return None

@app.route('/register', methods=['POST'])
def register_api():
    data = register()
    if data:
        return jsonify(data), 200
    return jsonify({"error": "Registration failed"}), 400

@app.route('/auth', methods=['POST'])
def auth_api():
    client_id = request.json.get("clientID")
    client_secret = request.json.get("clientSecret")
    token = get_auth_token(client_id, client_secret)
    if token:
        return jsonify({"token": token}), 200
    return jsonify({"error": "Authentication failed"}), 401

@app.route('/numbers/<numberid>', methods=['GET'])
def fetch_numbers(numberid):
    start_time = time.time()

    # Fetch numbers from test server
    headers = {"Authorization": f"Bearer YOUR_ACCESS_TOKEN"}
    response = requests.get(TEST_SERVER_URL + numberid, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch numbers"}), 500

    numbers = response.json().get("numbers", [])

    # Store unique numbers with a rolling window
    for num in numbers:
        if num not in stored_numbers:
            stored_numbers.append(num)
            if len(stored_numbers) > WINDOW_SIZE:
                stored_numbers.pop(0)  # Maintain window size

    # Compute average
    avg = sum(stored_numbers) / len(stored_numbers)

    response_time_ms = int((time.time() - start_time) * 1000)

    response_data = {
        "numbers": numbers,
        "previous_numbers": stored_numbers,
        "average": avg,
        "response_time_ms": response_time_ms
    }

    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(port=9876, debug=True)
