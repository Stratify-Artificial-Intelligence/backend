"""Implementations of entrypoint methods of Backend."""

import json
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.routers import (
    admin_router,
    business_router,
    business_research_router,
    chats_router,
    plans_router,
    subscriptions_router,
    tests_router,
    users_router,
)
from app.settings import FirebaseAuthSettings

firebase_auth_settings = FirebaseAuthSettings()

app = FastAPI(
    title='Veyra Backend API',
    description='Backend module of Veyra Artificial Intelligence.',
    root_path=os.getenv('ROOT_PATH', ''),
    docs_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='app/static'), name='static')


@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html():
    html = get_swagger_ui_html(
        openapi_url='/openapi.json',
        title='Veyra Backend API - Swagger UI',
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_favicon_url='/static/veyra_logo.ico',
    ).body.decode()

    if firebase_auth_settings.API_KEY == {}:
        logging.warning(
            'Firebase Auth API_KEY is None. Therefore, Google login button will not be '
            'injected to Swagger UI.'
        )
    else:
        # We have to inject:
        # - Firebase Auth JS SDK
        # - Variables used in custom_swagger_init.js
        # - Custom JS and CSS to render the login with Google button.
        injected_scripts = f"""
            <script src='https://www.gstatic.com/firebasejs/10.10.0/firebase-app-compat.js'></script>
            <script src='https://www.gstatic.com/firebasejs/10.10.0/firebase-auth-compat.js'></script>
            <script>const FIREBASE_CONFIG = '{json.dumps(firebase_auth_settings.API_KEY)}'</script>
            <script src='/static/custom_swagger_ui/custom_swagger_init.js'></script>
            <link rel='stylesheet' href='/static/custom_swagger_ui/google_login_styles.css'/>
            """  # noqa: E501
        html = html.replace('</body>', f'{injected_scripts}</body>')
    return HTMLResponse(html)


app.include_router(admin_router)
app.include_router(business_router)
app.include_router(business_research_router)
app.include_router(chats_router)
app.include_router(plans_router)
app.include_router(subscriptions_router)
app.include_router(tests_router)
app.include_router(users_router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', log_level='debug', port=8080, reload=True)
