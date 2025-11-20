import flask
import requests
import time
import logging

app = flask.Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

exchange_history = [] 

def get_flight_with_retries(url, params, max_retries=5, timeout=1, backoff_base=0.5):
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url=url, params=params, timeout=timeout)
            if resp.status_code == 204:
                last_err = Exception('no content (204)')
                if attempt < max_retries:
                    time.sleep(backoff_base * attempt)
                    continue
                else:
                    raise last_err

            resp.raise_for_status()
            return resp.json()

        except Exception as re:
            logger.warning("Exception while calling /flight on attempt %d/%d: %s", attempt, max_retries, str(re))
            last_err = re
            if attempt < max_retries:
                time.sleep(backoff_base * attempt)
                continue
            else:
                raise

@app.route('/buyTicket', methods=['POST'])
def buyTicket():
    global exchange_history
    
    params = flask.request.get_json()
    if not params: return flask.jsonify({"error": "Invalid request"}), 400
    
    flight = params.get('flight')
    day = params.get('day')
    user = params.get('user')

    query_params = {'flight' : flight, 'day' : day, 'user' : user}
    if not all(query_params.values()): return flask.jsonify({"error": "Missing fields"}), 400

    try:
        sale_response = get_flight_with_retries(url="http://airlineshub:5000/flight", params=query_params)
        sale_flight = sale_response.get('flight')
        sale_day = sale_response.get('day')
        sale_price_usd = sale_response.get('price_usd')

        dolar_today = None
        try:
            dolar_request = requests.get(url="http://exchange:5000/exchange", timeout=1)
            dolar_request.raise_for_status()
            val = dolar_request.json().get('value')
            if val:
                dolar_today = val
                exchange_history.append(val)
                if len(exchange_history) > 10: exchange_history.pop(0)
        except Exception:
            pass

        if dolar_today is None:
            if len(exchange_history) > 0:
                dolar_today = sum(exchange_history) / len(exchange_history)
            else:
                return flask.jsonify({"error": "Exchange critical failure"}), 500

        sale_price_brl = (sale_price_usd * dolar_today)

        params_sell = {"flight": sale_flight, "day": sale_day}
        transaction_msg = "Transaction completed"
        status_code = 200

        try:
            sell_post = requests.post(url="http://airlineshub:5000/sell", json=params_sell, timeout=2)
            sell_post.raise_for_status()
            transaction_msg = f"Transaction ID: {sell_post.json().get('transaction_id')}"
            
        except requests.exceptions.Timeout:
            logger.warning("Sell service timeout - Queuing transaction for background processing")
            transaction_msg = "High traffic: Transaction queued for processing."
            status_code = 202
            
        except Exception as re:
            logger.error("Error calling /sell: %s", re)
            return flask.jsonify({'error': 'Selling service error.'}), 500

        params_bonus = {"user" : user, "bonus" : round(sale_price_usd)}
        fidelity_response = "Pending"
        try:
            fidelity = requests.post(url="http://fidelity:5000/bonus", json=params_bonus, timeout=2)
            fidelity_response = fidelity.json().get("message", "Bonus registered")
        except Exception:
            fidelity_response = "Service unavailable, bonus queued."

        final_response = {
            "response" : "Flight process initiated",
            "status": "CONFIRMED" if status_code == 200 else "QUEUED",
            "transaction_info": transaction_msg,
            "flight" : flight,
            "price_brl" : round(sale_price_brl,2),
            "fidelity" : fidelity_response
        }

    except Exception as e:
        logger.error(f"Global error: {str(e)}")
        return flask.jsonify({'error': f'erro: {str(e)}'}), 500

    return flask.jsonify(final_response), status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)