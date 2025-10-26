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
    flight_num =params.get('flight')
    day = params.get('day')
    dolar_today = requests.get(url="http://exchange:5000/exchange").json().value #implementar
    for flight in database:
        if flight['flight_num'] == flight_num and flight['day'] == day:
            value = flight
    response = {
        'flight' : value['flight_num'],
        'day' : value['day'],
        'price' : (value['price_usd'] * dolar_today),
        'price_usd' : value['price_usd']
    }
    return flask.jsonify(response), 200
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)