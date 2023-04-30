from fastapi import FastAPI
from routers import games_controller, login_controller, players_controller, teams_controller
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(login_controller.router)
app.include_router(players_controller.router)
app.include_router(teams_controller.router)
app.include_router(games_controller.router)

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
