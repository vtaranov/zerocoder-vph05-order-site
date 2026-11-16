from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.database import Base, engine
from app.routes import services, applications

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield
    engine.dispose()

app = FastAPI(title="Atelier - заявки и услуги", version="1.0.0", docs_url=None, redoc_url=None, openapi_url="/api/openapi.json", lifespan=lifespan)
app.include_router(services.router)
app.include_router(applications.router)
app.mount("/api/static", StaticFiles(directory=Path(__file__).parent / "static"), name="swagger-static")

@app.get("/docs", include_in_schema=False)
def docs():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title, swagger_js_url="/api/static/swagger-ui-bundle.js", swagger_css_url="/api/static/swagger-ui.css", swagger_favicon_url="/favicon.svg")

@app.get("/api/health", tags=["Состояние"])
def health():
    with engine.connect() as conn: conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
