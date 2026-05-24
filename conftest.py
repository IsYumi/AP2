import pytest
import sqlite3
import os
from main import init_db

@pytest.fixture
def banco_de_testes(monkeypatch):
    nome_banco_teste = "test_geekstore.db"
    monkeypatch.setenv("DB_PATH", nome_banco_teste)    
    
    init_db()
    conn = sqlite3.connect(nome_banco_teste)
    conn.row_factory = sqlite3.Row
    
    yield conn
    conn.close()
    if os.path.exists(nome_banco_teste):
        os.remove(nome_banco_teste)