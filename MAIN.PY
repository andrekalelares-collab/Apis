import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import os

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
security = HTTPBasic()

# --- CONFIGURAÇÃO "SPEEDSTER" (LIMITADA) ---
CACHE_DB = {}
MAX_ITEMS = 100 
NODE_INFO = {
    "node": "Graciano",
    "ip": "beta.gratian.pro",
    "port": "26366",
    "domain": "apis.gratianweb.site"
}

class CacheItem(BaseModel):
    key: str
    value: str | int | dict | list

def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password != "Apifast":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- ROTAS DE DOCUMENTAÇÃO (PROTEGIDAS) ---
@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(check_credentials)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Kalel Speedster API")

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(check_credentials)):
    return get_openapi(title="Kalel Speedster API", version="1.0.0", routes=app.routes)

# --- DASHBOARD VISUAL (INDEX) ---
# Serve o arquivo HTML que criamos
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    # Garante que vai ler o arquivo index.html na mesma pasta
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Arquivo index.html não encontrado!</h1>")

# --- ROTAS FUNCIONAIS (API) ---

# Rota para o botão 'API Fast' funcionar
@app.get("/apifast")
async def api_fast():
    return {
        "mensagem": "Eu sou a velocidade!", 
        "node": NODE_INFO["node"],
        "status": "online"
    }

@app.post("/api/v1/cache/set")
async def set_cache(item: CacheItem):
    if len(CACHE_DB) >= MAX_ITEMS:
        # Remove o item mais antigo inserido (FIFO)
        first_key = next(iter(CACHE_DB))
        del CACHE_DB[first_key]
    
    CACHE_DB[item.key] = item.value
    return {"status": "ok", "saved": True}

@app.get("/api/v1/cache/get/{key}")
async def get_cache(key: str):
    if key in CACHE_DB:
        return {"found": True, "key": key, "value": CACHE_DB[key]}
    return {"found": False, "value": None}

# Para rodar: uvicorn main:app --reload --port 26366