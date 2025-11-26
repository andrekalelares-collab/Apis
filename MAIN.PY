import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
security = HTTPBasic()

# --- CONFIGURAÇÃO "SPEEDSTER" (LIMITADA) ---
CACHE_DB = {}
MAX_ITEMS = 100 # Limite para não sobrecarregar a memória
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
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Painel GratianWeb</title>
        <style>
            body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background-color: #1e293b; width: 400px; padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }}
            h2 {{ color: #fff; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-top: 0; }}
            .status-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
            .label {{ font-size: 0.9em; color: #94a3b8; }}
            .value {{ font-weight: bold; color: #38bdf8; }}
            .badge {{ background-color: #22c55e; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
            .btn {{ display: block; width: 100%; padding: 10px; background-color: #3b82f6; color: white; text-align: center; text-decoration: none; border-radius: 6px; margin-top: 20px; transition: 0.3s; }}
            .btn:hover {{ background-color: #2563eb; }}
            .info-group {{ background-color: #0f172a; padding: 10px; border-radius: 6px; margin-top: 15px; font-family: monospace; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Status da Instância</h2>
            
            <div class="status-row">
                <span class="label">Ative/desative o site</span>
                <span class="badge">Habilitado</span>
            </div>
            
            <div class="status-row">
                <span class="label">Última atualização</span>
                <span class="value">25/11/2025, 20:18:09</span>
            </div>
            
            <hr style="border-color: #334155; opacity: 0.3;">
            
            <div class="status-row" style="flex-direction: column; align-items: flex-start;">
                <span class="label">Domínio Padrão</span>
                <span style="color: #cbd5e1; font-size: 0.85em; margin-top: 5px;">Acesso automático por subdomínio gerado.</span>
                <div class="info-group" style="width: 93%; color: #38bdf8;">
                    {NODE_INFO['domain']}
                </div>
                <div style="font-size: 0.7em; color: #64748b; margin-top: 5px;">
                    Formato: &lt;slug&gt;.gratianweb.site. TLS automático.
                </div>
            </div>

            <div class="info-group">
                <div>Node: <span style="color: #a5b4fc">{NODE_INFO['node']}</span></div>
                <div>IP: <span style="color: #a5b4fc">{NODE_INFO['ip']}</span></div>
                <div>Porta: <span style="color: #a5b4fc">{NODE_INFO['port']}</span></div>
            </div>

            <a href="/docs" class="btn">Abrir Documentação (API)</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- ROTAS FUNCIONAIS (API) ---

@app.post("/api/v1/cache/set")
async def set_cache(item: CacheItem):
    if len(CACHE_DB) >= MAX_ITEMS:
        # Remove o item mais antigo inserido (FIFO) para liberar espaço
        first_key = next(iter(CACHE_DB))
        del CACHE_DB[first_key]
    
    CACHE_DB[item.key] = item.value
    return {"status": "ok", "saved": True}

@app.get("/api/v1/cache/get/{key}")
async def get_cache(key: str):
    if key in CACHE_DB:
        return {"found": True, "key": key, "value": CACHE_DB[key]}
    return {"found": False, "value": None}

# Para rodar: uvicorn main:app --reload --port 26366 Valor Atual: requirements.txt



