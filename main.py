from fastapi import FastAPI
from routers import players, teams, games

app = FastAPI()

app.include_router(players.router)
app.include_router(teams.router)
app.include_router(games.router)

