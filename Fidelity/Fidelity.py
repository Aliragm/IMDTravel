import flask
import random
import os

app = flask.Flask(__name__)

@app.route('/bonus', methods=['POST'])
def add_bonus():
    if random.random() < 0.02:
        os._exit(1)
    
    data = flask.request.get_json()

    if not data or 'user' not in data or 'bonus' not in data:
        return flask.jsonify({"status": "error", "message": "Missing required parameters (user, bonus)"}), 400

    user_id = data.get('user')
    bonus_points = data.get('bonus')

    message = f"Bonus received for user {user_id}: {bonus_points} points"

    return flask.jsonify({"message": message}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)