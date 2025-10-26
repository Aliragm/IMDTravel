import flask
import requests

app = flask.Flask(__name__)

@app.route('/buyTicket', methods=['POST'])
def buyTicket():
    params = flask.request.get_json()
    query_params = {
        'flight' : params.get('flight'),
        'day' : params.get('day'),
        'user' : params.get('user')
    }
    sale = requests.get(url="http://airlineshub:5000/flight",params=query_params)
    if sale.status_code == requests.codes.ok:
        response = {
            'id_transaction' : sale.json().id_transaction
        }
        return flask.jsonify(response), 200
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)