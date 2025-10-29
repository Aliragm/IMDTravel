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
        'flight' : flight,
        'day' : day,
        'user' : user
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

        dolar_today_request = requests.get(url="http://exchange:5000/exchange", timeout=1)

        dolar_today_request.raise_for_status()

        dolar_today = dolar_today_request.json().get('value')

        if dolar_today is None:
            return flask.jsonify({"error": "Response did not have an dolar value"}), 500
        
        sale_price_brl = (sale_price_usd * dolar_today)

        params_sell = {
            "flight": sale_flight,
            "day": sale_day
        }
    
        sell_post = requests.post(url="http://airlineshub:5000/sell", json=params_sell)

        sell_post.raise_for_status()

        transaction_id = sell_post.json().get('transaction_id')
        
        params_bonus = {
            "user" : user,
            "bonus" : round(sale_price_usd)
        }

        fidelity = requests.post(url="http://fidelity:5000/bonus", json=params_bonus)

        fidelity.raise_for_status()

        fidelity_response = fidelity.json().get("message")

        final_response = {
            "response" : "Flight bought!",
            "flight" : flight,
            "day" : day,
            "user" : user,
            "price_usd" : sale_price_usd,
            "price_brl" : round(sale_price_brl,2),
            "fidelity" : fidelity_response
        }

    except Exception as e:
        return flask.jsonify({'error': f'erro: {str(e)}'}), 500

    return flask.jsonify(final_response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)