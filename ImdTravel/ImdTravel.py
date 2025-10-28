import flask
import requests

app = flask.Flask(__name__)

@app.route('/buyTicket', methods=['POST'])
def buyTicket():
    params = flask.request.get_json()

    if not params:
        return flask.jsonify({"error": "Invalid request"}), 400
    
    flight = params.get('flight')
    day = params.get('day')
    user = params.get('user')

    query_params = {
        'flight' : params.get('flight'),
        'day' : params.get('day'),
        'user' : params.get('user')
    }

    if not all(query_params.values()):
        return flask.jsonify({"error": "All fields 'flight', 'day', and 'user' are obrigatory"}), 400

    try:
        sale = requests.get(url="http://airlineshub:5000/flight",params=query_params)

        sale.raise_for_status()

        sale_response = sale.json()        

        sale_flight = sale_response.get('flight')

        sale_day = sale_response.get('day')

        sale_price_usd = sale_response.get('price_usd')

        params_sell = {
            "flight": sale_flight,
            "day": sale_day
        }
    
        sell_post = requests.post(url="http://airlineshub:5000/sell", json=flask.jsonify(params_sell))

        sell_post.raise_for_status()

        transaction_id = sell_post.get('http://transaction_id:5000/bonus')
        
        params_bonus = {
            "user" : user,
            "bonus" : round(sale_price_usd)
        }

        fidelity = requests.post(url=fidelity)

        fidelity.raise_for_status()
    except Exception as e:
        return flask.jsonify({'error': f'erro: {str(e)}'}), 500

    return flask.jsonify({"response": "Seu voo foi comprado com sucesso!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)