import flask
import requests
import time
import logging

app = flask.Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def get_flight_with_retries(url, params, max_retries=3, timeout=1, backoff_base=0.5):
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url=url, params=params, timeout=timeout)
            if resp.status_code == 204:
                last_err = Exception('no content (204)')
                if attempt < max_retries:
                    logger.info("/flight returned 204 (omission). retrying attempt %d/%d", attempt, max_retries)
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
        sale_response = get_flight_with_retries(url="http://airlineshub:5000/flight", params=query_params)

        sale_flight = sale_response.get('flight')
        sale_day = sale_response.get('day')
        sale_price_usd = sale_response.get('price_usd')

        # Implementação da tolerância a falhas para o Exchange (Retry)
        dolar_today = None
        max_retries_exchange = 3
        
        for attempt in range(max_retries_exchange):
            try:
                dolar_today_request = requests.get(url="http://exchange:5000/exchange", timeout=1)
                dolar_today_request.raise_for_status()
                value = dolar_today_request.json().get('value')
                
                if value is not None:
                    dolar_today = value
                    break
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Exchange service failed (Attempt {attempt+1}/{max_retries_exchange}): {e}")
                if attempt < max_retries_exchange - 1:
                    time.sleep(0.5)
        
        if dolar_today is None:
            return flask.jsonify({"error": "Exchange service unavailable after retries"}), 500

        sale_price_brl = (sale_price_usd * dolar_today)

        params_sell = {
            "flight": sale_flight,
            "day": sale_day
        }

        try:
            sell_post = requests.post(url="http://airlineshub:5000/sell", json=params_sell, timeout=2)
            sell_post.raise_for_status()
            transaction_id = sell_post.json().get('transaction_id')
        except requests.exceptions.Timeout as te:
            logger.error("/sell timed out (latency > 2s): %s", te)
            return flask.jsonify({'error': 'Selling service timed out (latency > 2s). Operation aborted.'}), 504
        except Exception as re:
            logger.error("Error calling /sell: %s", re)
            return flask.jsonify({'error': 'Selling service error. Operation aborted.'}), 500

        params_bonus = {
            "user" : user,
            "bonus" : round(sale_price_usd)
        }

        # Implementação da tolerância a falhas para o Fidelity (Degradação de Serviço)
        fidelity_response = None
        try:
            fidelity = requests.post(url="http://fidelity:5000/bonus", json=params_bonus, timeout=2)
            fidelity.raise_for_status()
            fidelity_response = fidelity.json().get("message")
        except Exception as e:
            logger.error(f"Fidelity service failed: {e}")
            fidelity_response = "Fidelity service unavailable, bonus not registered."

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
        logger.error(f"Global error: {str(e)}")
        return flask.jsonify({'error': f'erro: {str(e)}'}), 500

    return flask.jsonify(final_response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)