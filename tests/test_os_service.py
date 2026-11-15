"""A consulta contra um servidor HTTP local que imita a rota interna do OS Service."""
import json
import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from os_service import Cliente, buscar_cliente

CPF = "52998224725"


class OSServiceFalso(BaseHTTPRequestHandler):
    respostas = {}
    recebidas = []

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["content-length"])))
        self.recebidas.append((self.path, self.headers.get("x-token-interno"), corpo))
        status, dados = self.respostas[corpo["cpf_cnpj"]]
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(dados).encode())

    def log_message(self, *args):
        pass


@pytest.fixture
def os_service(monkeypatch):
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), OSServiceFalso)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    monkeypatch.setenv("OS_SERVICE_URL", f"http://127.0.0.1:{servidor.server_port}/")
    monkeypatch.setenv("TOKEN_INTERNO", "token-de-teste")
    OSServiceFalso.respostas, OSServiceFalso.recebidas = {}, []
    yield OSServiceFalso
    servidor.shutdown()


def test_cliente_encontrado(os_service):
    os_service.respostas[CPF] = (200, {"id": "c-1", "nome": "Ana", "cpf_cnpj": CPF, "ativo": False})

    assert buscar_cliente(CPF) == Cliente("c-1", "Ana", CPF, False)
    assert os_service.recebidas == [("/interno/clientes/autenticar", "token-de-teste", {"cpf_cnpj": CPF})]


def test_cliente_inexistente_vira_none(os_service):
    os_service.respostas[CPF] = (404, {"detail": "Cliente não encontrado"})
    assert buscar_cliente(CPF) is None


@pytest.mark.parametrize("status", [403, 500, 503])
def test_outras_respostas_sao_falha_do_os_service(os_service, status):
    os_service.respostas[CPF] = (status, {"detail": "falha"})
    with pytest.raises(urllib.error.HTTPError):
        buscar_cliente(CPF)


def test_os_service_fora_do_ar(monkeypatch):
    monkeypatch.setenv("OS_SERVICE_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("TOKEN_INTERNO", "token-de-teste")
    with pytest.raises(urllib.error.URLError):
        buscar_cliente(CPF)
