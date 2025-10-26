import flask
import requests

database = [
    { 
        "flight_num": "100", 
        "day": "25/10/2025", 
        "price_usd": 300.50 
    },
    { 
        "flight_num": "101", 
        "day": "25/10/2025", 
        "price_usd": 320.00 
    },
    { 
        "flight_num": "250", 
        "day": "26/10/2025", 
        "price_usd": 80.75 
    },
    { 
        "flight_num": "255", 
        "day": "26/10/2025", 
        "price_usd": 80.75 
    },
    { 
        "flight_num": "700", 
        "day": "27/10/2025",  
        "price_usd": 950.00 
    },
    { 
        "flight_num": "701", 
        "day": "27/10/2025", 
        "price_usd": 980.00 
    }
]

app = flask.Flask(__name__)

@app.route('/flight', methods=['GET'])
def flight():
    params = flask.request.args

    if not params:
        return flask.jsonify({"error": "Invalid request"}), 400

    flight_num =params.get('flight')
    day = params.get('day')
    user = params.get('user')

    if flight_num is None or day is None:
        return flask.jsonify({"error": "All fields 'flight_num', 'day' are obrigatory"}), 400
        
    try:
        dolar_today_request = requests.get(url="http://exchange:5000/exchange") #implementar Exchange

        dolar_today_request.raise_for_status()

        dolar_today = dolar_today_request.json().get('value')

        if dolar_today is None:
            return flask.jsonify({"error": "Response did not have an dolar value"}), 500
        
        value = None
        for flight in database:
            if flight['flight_num'] == flight_num and flight['day'] == day:
                value = flight
                break
        
        if value is None:
            return flask.jsonify({"error": "flight was not found"}), 404


        #implementar o request para o id da transação

        response = {
            'flight' : value['flight_num'],
            'day' : value['day'],
            'price_brl' : (value['price_usd'] * dolar_today),
            'price_usd' : value['price_usd']
        }

        return flask.jsonify(response), 200
     
    except Exception as e:
        return flask.jsonify({'error': f'erro: {str(e)}'}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)