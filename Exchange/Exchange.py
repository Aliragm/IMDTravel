import flask
import random
import time

app = flask.Flask(__name__)

fail_state_active = False
fail_until_timestamp = 0

@app.route('/exchange', methods=['GET'])
def get_exchange_rate():
    global fail_state_active, fail_until_timestamp

    current_time = time.time()

    if fail_state_active:
        if current_time < fail_until_timestamp:
            return flask.jsonify({"error": "Simulated Server Error"}), 500
        else:
            fail_state_active = False

    if random.random() < 0.1:
        fail_state_active = True
        fail_until_timestamp = current_time + 5
        return flask.jsonify({"error": "Simulated Server Error"}), 500

    rate = random.uniform(5.0, 6.0)
    return flask.jsonify({"value": rate}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)