from fastapi.testclient import TestClient
from main import app, get_gateway

client = TestClient(app)

class MockGatewayAprovado:
    def cobrar(self, cartao: str, valor: float):
        return True

class MockGatewayRecusado:
    def cobrar(self, cartao: str, valor: float):
        return False

def test_listar_produtos(banco_de_testes):
    response = client.get("/api/produtos")
    assert response.status_code == 200
    produtos = response.json()
    assert len(produtos) >= 2
    assert produtos[0]["nome"] == "teclado"

def test_comprar_sucesso_sem_cupom(banco_de_testes):
    app.dependency_overrides[get_gateway] = lambda: MockGatewayAprovado()
    response = client.post("/api/comprar", json={
        "produto": "teclado",
        "cartao": "1234 5678 9101 1121",
        "cupom": ""
    })
    
    assert response.status_code == 200
    assert response.json()["valor_pago"] == 200.0
    
    cursor = banco_de_testes.cursor()
    estoque = cursor.execute("SELECT estoque FROM produtos WHERE nome = 'teclado'").fetchone()[0]
    assert estoque == 9

def test_comprar_com_cupom_valido(banco_de_testes):
    app.dependency_overrides[get_gateway] = lambda: MockGatewayAprovado()
    response = client.post("/api/comprar", json={
        "produto": "mouse",
        "cartao": "1111",
        "cupom": "GEEK20"
    })
    
    assert response.status_code == 200
    assert response.json()["valor_pago"] == 80.0

def test_comprar_produto_nao_encontrado(banco_de_testes):
    response = client.post("/api/comprar", json={
        "produto": "monitor_inexistente",
        "cartao": "1111",
        "cupom": ""
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"

def test_comprar_sem_estoque(banco_de_testes):
    banco_de_testes.execute("UPDATE produtos SET estoque = 0 WHERE nome = 'mouse'")
    banco_de_testes.commit()
    response = client.post("/api/comprar", json={
        "produto": "mouse",
        "cartao": "1111",
        "cupom": ""
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Sem estoque"

def test_comprar_pagamento_recusado(banco_de_testes):
    app.dependency_overrides[get_gateway] = lambda: MockGatewayRecusado()
    response = client.post("/api/comprar", json={
        "produto": "teclado",
        "cartao": "cartao_clonado",
        "cupom": ""
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Pagamento recusado pelo Gateway."
    
    app.dependency_overrides.clear()