from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from main import app, get_gateway
from unittest.mock import MagicMock

client = TestClient(app)

scenarios('compra.feature')

@given(parsers.parse('que o sistema possui o produto "{produto}" em estoque'))
def produto_em_estoque(banco_de_testes, produto):
    pass

@when(parsers.parse('o cliente realiza a compra do "{produto}" com o cartão "{cartao}"'), target_fixture="resposta_compra")
def realizar_compra(produto, cartao):
    mock_gateway = MagicMock()
    mock_gateway.cobrar.return_value = True
    app.dependency_overrides[get_gateway] = lambda: mock_gateway
    
    response = client.post("/api/comprar", json={
        "produto": produto,
        "cartao": cartao,
        "cupom": ""
    })
    
    app.dependency_overrides.clear()
    
    return response

@then('a resposta da API deve ser de sucesso')
def verificar_sucesso(resposta_compra):
    assert resposta_compra.status_code == 200
    assert resposta_compra.json()["status"] == "sucesso"

@then(parsers.parse('o valor pago na resposta deve ser {valor:f}'))
def verificar_valor(resposta_compra, valor):
    assert resposta_compra.json()["valor_pago"] == valor