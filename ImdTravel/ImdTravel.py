import flask
import requests

app = flask.Flask(__name__)

@app.route('/buyTicket', methods=['POST'])
def buyTicket():
    params = flask.request.get_json()

    if not params:
        return flask.jsonify({'error' : 'Invalid request'}), 400
    
    query_params = {
        'flight' : params.get('flight'),
        'day' : params.get('day'),
        'user' : params.get('user')
    }

    if not all(query_params.values()):
        return flask.jsonify({"error' : 'All fields 'flight', 'day', and 'user' are obrigatory"}), 400

    try:
        sale = requests.get(url="http://airlineshub:5000/flight",params=query_params)

        sale.raise_for_status()

        transaction_id = sale.json().get('id_transaction')

        if transaction_id is None:
            return flask.jsonify({"error": "Response did not have an transaction id"}), 500
        
        response = {
            'id_transaction' : transaction_id
        }
        return flask.jsonify(response), 200
    except Exception as e:
        return flask.jsonify({'error': f'erro: {str(e)}'}), 500


    #if sale.status_code == requests.codes.ok:
    #    response = {
    #        'id_transaction' : sale.json().id_transaction
    #    }
    #    return flask.jsonify(response), 200
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)