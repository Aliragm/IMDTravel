IMDTravel - Sistema Distribuído de Agência de Viagens
Projeto de um sistema distribuído que simula a arquitetura de microsserviços de uma agência de viagens.

O sistema é composto por quatro serviços independentes, cada um rodando em seu próprio contêiner Docker. A comunicação entre os serviços é feita via requisições HTTP (API REST) dentro de uma rede Docker customizada.

🚀 Como Rodar o Projeto
Esta é a seção mais importante. Para rodar o sistema completo, você só precisa ter o Docker e o Docker Compose instalados.

Passo 1: Clone o Repositório
Bash

git clone https://github.com/Aliragm/IMDTravel.git
Passo 2: Entre na Pasta do Projeto
Bash

cd IMDTravel
Passo 3: Suba todos os Serviços com um Comando
Este é o comando mágico. Ele vai construir a imagem de cada um dos 4 serviços (AirlinesHub, Exchange, Fidelity, ImdTravel) e iniciá-los todos juntos na mesma rede.

Bash

docker compose up --build
Você verá o log de todos os 4 serviços subindo no seu terminal.

Pronto! O sistema inteiro está no ar.

🧪 Como Testar
Você deve enviar uma requisição APENAS para o serviço imdtravel, que é o orquestrador. O docker-compose.yml mapeou a porta interna dele para a porta 5001 no seu localhost.

Use o Postman (ou curl, etc.) para enviar a requisição principal:

Endpoint Principal: POST /buyTicket
Este é o único endpoint que você, como usuário, precisa chamar. Ele vai disparar todo o fluxo de comunicação entre os outros microsserviços.

URL: http://localhost:5001/buyTicket

Método: POST

Body (raw, JSON):

JSON

{
  "flight": "100",
  "day": "25/10/2025",
  "user": 1
}

Ou qualquer json disponível no arquivo *airlineshub.py*

Respostas Possíveis
✅ Resposta de Sucesso (200 OK)
Se o voo for encontrado, o câmbio funcionar e o bônus for registrado, você receberá:

JSON

{
    "response": "Flight bought!",
    "flight": "100",
    "day": "25/10/2025",
    "user": 1,
    "price_usd": 300.5,
    "price_brl": 1650.14,
    "fidelity": "Bonus received for user andre: 301 points"
}
(Nota: O price_brl irá variar, pois o exchange gera um valor aleatório).

❌ Resposta de Erro (Voo não encontrado - 404)
Se você tentar comprar um voo que não está no banco de dados (ex: "999"):

Body (raw, JSON):

JSON

{
  "flight": "999",
  "day": "25/10/2025",
  "user": 1
}
Resposta (500 Internal Server Error):

JSON

{
  "error": "erro: 404 Client Error: NOT FOUND for url: http://airlineshub:5000/flight?flight=999&day=25%2F10%2F2025&user=1"
}
(Este erro é esperado. O imdtravel tentou buscar o voo, recebeu um 404 do airlineshub, e reportou o erro para você).

🏛️ Arquitetura e Serviços
O sistema é dividido em 4 microsserviços:

imdtravel (O Orquestrador)

Porta: 5001

Função: Recebe a requisição de compra e coordena todas as chamadas para os outros serviços para completar a transação.

airlineshub (O Banco de Voos)

Porta: 5002

Função: Armazena um banco de dados em memória de voos e seus preços em USD. Ele valida se um voo existe (GET /flight) e "vende" o ticket, gerando um ID de transação (POST /sell).

exchange (O Serviço de Câmbio)

Porta: 5003

Função: Simula um serviço de cotação. Retorna um valor aleatório entre 5.0 e 6.0 para a cotação do dólar.

fidelity (O Serviço de Bônus)

Porta: 5004

Função: Recebe o ID do usuário e um valor de bônus, e retorna uma mensagem de confirmação.

🔄 Fluxo da Requisição (POST /buyTicket)
Ao chamar o imdtravel, este é o fluxo de comunicação interna que acontece:

[POST] Usuário -> imdtravel (/buyTicket)

Payload: {flight, day, user}

[GET] imdtravel -> airlineshub (/flight)

Query: ?flight=...&day=...&user=...

Resposta: {flight, day, price_usd}

[GET] imdtravel -> exchange (/exchange)

Resposta: {value} (cotação do dólar)

[POST] imdtravel -> airlineshub (/sell)

Body: {flight, day}

Resposta: {transaction_id}

[POST] imdtravel -> fidelity (/bonus)

Body: {user, bonus}

Resposta: {message}

[200 OK] imdtravel -> Usuário

Resposta: {response, flight, day, user, price_usd, price_brl, fidelity}

🛠️ Detalhes dos Endpoints de Cada Serviço
imdtravel (Porta 5001)
POST /buyTicket: Ponto de entrada principal que orquestra todo o fluxo.

airlineshub (Porta 5002)
GET /flight: Consulta um voo por flight e day. Retorna os detalhes e o price_usd.

POST /sell: Confirma uma venda. Recebe flight e day e retorna um transaction_id único.

exchange (Porta 5003)
GET /exchange: Retorna a cotação do dólar.

fidelity (Porta 5004)
POST /bonus: Recebe user e bonus. Retorna uma mensagem de confirmação.