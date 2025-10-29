from flask import Flask, Response
import random

app = Flask(__name__)

@app.route('/exchange', methods=['GET'])
def get_exchange_rate():
    rate = random.uniform(5.0, 6.0)
    return Response(str(rate), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)