"""Consulta do cliente no OS Service, dono do cadastro (ADR-022); a Lambda não lê banco de outro serviço."""
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Cliente:
    id: str
    nome: str
    cpf_cnpj: str
    ativo: bool


def buscar_cliente(digitos: str) -> Cliente | None:
    """Pergunta pela rota interna do OS Service; None quando o cliente não existe."""
    requisicao = urllib.request.Request(
        f"{os.environ['OS_SERVICE_URL'].rstrip('/')}/interno/clientes/autenticar",
        data=json.dumps({"cpf_cnpj": digitos}).encode(),
        headers={"content-type": "application/json", "x-token-interno": os.environ["TOKEN_INTERNO"]},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=5) as resposta:
            dados = json.load(resposta)
    except urllib.error.HTTPError as erro:
        if erro.code == 404:
            return None
        raise
    return Cliente(dados["id"], dados["nome"], dados["cpf_cnpj"], dados["ativo"])
