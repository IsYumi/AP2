## Como configurar o ambiente local

**1. Criar e ativar o ambiente virtual:**

# Criar o ambiente
python -m venv venv

# Ativar no Windows:
venv\Scripts\activate
# Ativar no Linux/Mac:
source venv/bin/activate


**2. Instalar as dependências:**

pip install -r requirements.txt


## Como correr a aplicação

A aplicação utiliza o **FastAPI** para o backend e serve um ficheiro estático `index.html` para o frontend.


uvicorn main:app --reload


* **Frontend:** Acede a `http://localhost:8000` no navegador.
* **Documentação da API:** Acede a `http://localhost:8000/docs`.

*(Nota: Na primeira execução, o ficheiro do banco de dados `geekstore.db` será criado automaticamente).*

## Como correr os testes

Deixa o servidor (comando acima) a executando num terminal e **abra um segundo terminal** (ativar o ambiente virtual novamente) para executar os comandos dos testes.

**Para correr todos os testes:**

pytest


**Para correr os testes e validar a meta de cobertura (Obrigatório para a entrega):**

pytest --cov=. --cov-fail-under=90
