import json

import jwt
import pytest

import handler as modulo
from os_service import Cliente

CHAVE = "chave-de-teste-com-mais-de-32-caracteres-ok"
CPF = "52998224725"


@pytest.fixture
def os_service(monkeypatch):
    """Substitui o OS Service por um dublê que registra o documento consultado."""
    estado = {"cliente": Cliente("c-1", "Ana", CPF, True), "erro": None, "consultado": None}

    def buscar(digitos):
        estado["consultado"] = digitos
        if estado["erro"]:
            raise estado["erro"]
        return estado["cliente"]

    monkeypatch.setattr(modulo, "buscar_cliente", buscar)
    return estado


def chamar(corpo=None, bruto=None):
    evento = {
        "body": bruto if bruto is not None else (json.dumps(corpo) if corpo is not None else None),
        "isBase64Encoded": False,
    }
    resposta = modulo.handler(evento, type("Contexto", (), {"aws_request_id": "req-1"})())
    return resposta["statusCode"], json.loads(resposta["body"]), resposta["headers"]


def test_cliente_ativo_recebe_token(os_service):
    status, corpo, _ = chamar({"cpf": CPF})
    assert status == 200
    assert corpo["cliente"] == {"id": "c-1", "nome": "Ana"}
    assert jwt.decode(corpo["access_token"], CHAVE, algorithms=["HS256"])["tipo"] == "cliente"


def test_cpf_pontuado_e_normalizado_antes_da_consulta(os_service):
    assert chamar({"cpf": "529.982.247-25"})[0] == 200
    assert os_service["consultado"] == CPF


def test_cpf_invalido_nao_chega_ao_os_service(os_service):
    assert chamar({"cpf": "11111111111"})[0] == 400
    assert os_service["consultado"] is None


def test_documento_ausente(os_service):
    status, corpo, _ = chamar({})
    assert status == 400
    assert "cpf" in corpo["detail"].lower()


def test_corpo_que_nao_e_json(os_service):
    assert chamar(bruto="isto não é json")[0] == 400


def test_cliente_inexistente(os_service):
    os_service["cliente"] = None
    assert chamar({"cpf": CPF})[:2] == (404, {"detail": "Cliente não encontrado"})


def test_cliente_inativo_nao_autentica(os_service):
    os_service["cliente"] = Cliente("c-1", "Ana", CPF, False)
    assert chamar({"cpf": CPF})[0] == 403


def test_os_service_indisponivel_responde_503_sem_vazar_detalhe(os_service):
    os_service["erro"] = ConnectionError("http://10.0.128.42:30080 token-interno=segredo")
    status, corpo, _ = chamar({"cpf": CPF})
    assert status == 503
    assert "10.0.128" not in json.dumps(corpo) and "segredo" not in json.dumps(corpo)


def test_request_id_volta_no_cabecalho(os_service):
    assert chamar({"cpf": CPF})[2]["x-request-id"] == "req-1"
