import sqlite3
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from typing import Optional

app = FastAPI()

# Configuração do Banco (Permite sobrescrever via variável de ambiente para testes)
DB_PATH = os.getenv("DB_PATH", "geekstore.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria a tabela e insere dados iniciais se o banco estiver vazio."""
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS produtos (nome TEXT PRIMARY KEY, preco REAL, estoque INTEGER)')
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM produtos')
    if cursor.fetchone()[0] == 0:
        conn.execute("INSERT INTO produtos (nome, preco, estoque) VALUES ('teclado', 200.0, 10)")
        conn.execute("INSERT INTO produtos (nome, preco, estoque) VALUES ('mouse', 100.0, 5)")
    conn.commit()
    conn.close()

# --- Dependências Externas ---
class GatewayPagamento:
    """Simula uma API externa de cartão de crédito"""
    def cobrar(self, cartao: str, valor: float):
        # Na vida real faria request HTTP
        return True

# Função para Injeção de Dependência do Gateway
def get_gateway():
    return GatewayPagamento()

# --- Regras de Negócio ---
def calcular_desconto(valor: float, cupom: str) -> float:
    if cupom == "GEEK20":
        return valor * 0.8
    return valor

def processar_pedido(valor: float, cartao: str, gateway: GatewayPagamento):
    if valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    sucesso = gateway.cobrar(cartao, valor)
    if not sucesso:
        raise ValueError("Pagamento recusado pelo Gateway.")
    return "Compra aprovada!"

# --- Rotas da API ---
class CompraRequest(BaseModel):
    produto: str
    cartao: str
    cupom: Optional[str] = ""

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/produtos")
def listar_produtos():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return [dict(p) for p in produtos]

@app.post("/api/comprar")
def comprar(req: CompraRequest, gateway: GatewayPagamento = Depends(get_gateway)):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE nome = ?', (req.produto.lower(),)).fetchone()

    if not produto:
        conn.close()
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if produto["estoque"] <= 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Sem estoque")

    valor_final = calcular_desconto(produto["preco"], req.cupom)

    try:
        mensagem = processar_pedido(valor_final, req.cartao, gateway)
        # Reduz o estoque no banco
        conn.execute('UPDATE produtos SET estoque = estoque - 1 WHERE nome = ?', (req.produto.lower(),))
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": mensagem, "valor_pago": valor_final}
    except ValueError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

# Rota do Frontend
@app.get("/", response_class=HTMLResponse)
def frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()