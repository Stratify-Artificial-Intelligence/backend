"""Implementations of entrypoint methods of Stratify Backend."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin_router, chats_router, tests_router, users_router

app = FastAPI(
    title='Stratify Backend API',
    description='Backend module of Stratify Artificial Intelligence.',
    root_path=os.getenv('ROOT_PATH', ''),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(admin_router)
app.include_router(chats_router)
app.include_router(tests_router)
app.include_router(users_router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', log_level='debug', port=8080, reload=True)
