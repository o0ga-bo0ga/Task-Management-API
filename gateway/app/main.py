import httpx
from jose import jwt, JWTError
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from contextlib import asynccontextmanager
from .config import get_settings

env_settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}

async def verify_jwt(request: Request):
    if request.url.path in ["/auth/login", "/auth/register", "/health"]:
        return
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, env_settings.SECRET_KEY, algorithms=[env_settings.ALGORITHM])
        request.state.user = payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, _auth: None = Depends(verify_jwt)):
    path = request.url.path
    method = request.method

    if path.startswith("/auth/"):
        upstream_url = f"{env_settings.AUTH_SERVICE_URL}{path}"
    elif path.startswith("/tasks/"):
        upstream_url = f"{env_settings.TASK_SERVICE_URL}{path}"
    else:
        raise HTTPException(status_code=404,
                            detail="Not found")
    
    headers = dict(request.headers)
    headers.pop("host", None)

    content = await request.body()

    try:
        req = app.state.http_client.build_request(method,
                                        upstream_url,
                                        headers=headers,
                                        params=request.query_params,
                                        content=content)
        
        response = await app.state.http_client.send(req,
                                          stream=True)

        return StreamingResponse(response.aiter_raw(),
                                 status_code=response.status_code,
                                 headers=dict(response.headers),
                                 background=BackgroundTask(response.aclose))
    
    except httpx.ConnectError:
        raise HTTPException(status_code=502,
                            detail="Upstream service unavailable")