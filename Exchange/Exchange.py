from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Olá de Exchange!"

if __name__ == '__main__':
    # ISSO É OBRIGATÓRIO PARA O DOCKER FUNCIONAR:
    app.run(host='0.0.0.0', port=5000)