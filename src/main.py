from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)

app = FastAPI(
    docs_url = None,
    redoc_url = None,
    debug = True
)

app.mount(
    path = "/static",
    app = StaticFiles(directory = "src/static"),
    name = "static"
)

@app.get(
    path = "/docs",
    include_in_schema = False,
)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url = "/openapi.json",
        title = "pdfwn app",
        oauth2_redirect_url = "/docs/oauth2-redirect",
        swagger_js_url = "/static/swagger-ui-bundle.js",
        swagger_css_url = "/static/swagger-ui.css"
)

@app.get(
    "/",
    include_in_schema = False,
)
async def get_root():
    return RedirectResponse("docs")

url_sql =  URL.create(
        drivername = 'mssql+aioodbc',
        username = 'sa',
        password = 'Pass!word',
        host = 'sqldata',
        database = 'test',
        query = {"driver": "ODBC Driver 17 for SQL Server"}
)

async_engine: AsyncEngine = create_async_engine(
    url = url_sql,
    pool_pre_ping = True
)

SessionLocal = async_sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = async_engine,
)

async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@app.get(
    "/test"
)
async def get_test(
    session: AsyncSession = Depends(get_session)
):
    result = (await session.scalars(text("select 1"))).all()
    return result
    