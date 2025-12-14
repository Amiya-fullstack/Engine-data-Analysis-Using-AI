from fastapi import FastAPI
from api.routes.health import router as health_router

app = FastAPI(title="Industrial AI MCP API")

app.include_router(health_router)


@app.get("/status")
async def status():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, log_level="info")
