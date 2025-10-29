import flask
import requests
import uuid

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
            'price_usd' : value['price_usd']
        }

        return flask.jsonify(response), 200
     
    except Exception as e:
        return flask.jsonify({'error': f'erro: {str(e)}'}), 500
    
@app.route('/sell', methods=['POST'])
def sell():
    params = flask.request.get_json()
    
    flight = params.get('flight')

    day = params.get('day')

    if flight is None or day is None:
        return flask.jsonify({"error": "All fields 'flight_num', 'day' are obrigatory"}), 400
    
    transaction_id = uuid.uuid4()

    response = {
        "transaction_id" : transaction_id
    }

    return flask.jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)