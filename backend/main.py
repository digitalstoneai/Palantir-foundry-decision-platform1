from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import FRONTEND_URL
from routers import decisionroom, opsgraph

app = FastAPI(title="Palantir Foundry Operational Decision Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(opsgraph.router)
app.include_router(decisionroom.router)
