import { check, sleep } from 'k6';
import http from 'k6/http'

export const options ={
    stages: [
        { duration: '30s', target:50},
        { duration: '1m', target: 50},
        { duration: '30s', target: 0}
    ],
    thresholds: {
        http_req_duration: ['p(99)<500']
    }
};

export default () => {
    const url = "http://localhost:5001/buyTicket";
    
    const payload = JSON.stringify({
        "flight": "100",
        "day": "25/10/2025",
        "user": 1
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const res = http.post(url, payload, params);
    // Verificação
    const checkRes = check(res, {
        'status is 200 or 202': (r) => r.status === 200 || r.status === 202,
    });

    // DEBUG: Se falhar, imprime o erro no terminal (apenas nas primeiras vezes para não floodar)
    if (!checkRes) {
        // Imprime o status code e o corpo da resposta para sabermos o motivo
        console.error(`FALHA | Status: ${res.status} | Erro: ${res.body}`);
    }
    sleep(1)
}