from fastapi import FastAPI
from routers import access, players, teams, games
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(access.router)
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(games.router)

origins = [
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
