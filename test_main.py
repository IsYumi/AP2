from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import pytest
from main import app, get_gateway, processar_pedido

client = TestClient(app)

def test_processar_pedido_sucesso():
    mock_gateway = MagicMock()
    mock_gateway.cobrar.return_value = True
    resultado = processar_pedido(150.0, "1234-5678", mock_gateway)

    assert resultado == "Compra aprovada!"
    mock_gateway.cobrar.assert_called_once_with("1234-5678", 150.0)

def test_processar_pedido_recusado():
    mock_gateway = MagicMock()
    mock_gateway.cobrar.return_value = False
    
    with pytest.raises(ValueError, match="Pagamento recusado pelo Gateway."):
        processar_pedido(150.0, "1234-5678", mock_gateway)

def test_listar_produtos(banco_de_testes):
    response = client.get("/api/produtos")
    assert response.status_code == 200
    produtos = response.json()
    assert len(produtos) >= 2
    assert produtos[0]["nome"] == "teclado"

def test_comprar_sucesso_sem_cupom(banco_de_testes):
    mock_gateway = MagicMock()
    mock_gateway.cobrar.return_value = True
    app.dependency_overrides[get_gateway] = lambda: mock_gateway
    
    response = client.post("/api/comprar", json={
        "produto": "teclado",
        "cartao": "1234",
        "cupom": ""
    })
    
    assert response.status_code == 200
    assert response.json()["valor_pago"] == 200.0
    mock_gateway.cobrar.assert_called_once()
    
    cursor = banco_de_testes.cursor()
    estoque = cursor.execute("SELECT estoque FROM produtos WHERE nome = 'teclado'").fetchone()[0]
    assert estoque == 9
    
    app.dependency_overrides.clear()

def test_comprar_com_cupom_valido(banco_de_testes):
    mock_gateway = MagicMock()
    mock_gateway.cobrar.return_value = True
    app.dependency_overrides[get_gateway] = lambda: mock_gateway
    
    response = client.post("/api/comprar", json={
        "produto": "mouse",
        "cartao": "1111",
        "cupom": "GEEK20"
    })
    
    assert response.status_code == 200
    assert response.json()["valor_pago"] == 80.0
    app.dependency_overrides.clear()

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

def test_comprar_produto_nao_encontrado(banco_de_testes):
    response = client.post("/api/comprar", json={
        "produto": "inexistente",
        "cartao": "1111",
        "cupom": ""
    })
    assert response.status_code == 404