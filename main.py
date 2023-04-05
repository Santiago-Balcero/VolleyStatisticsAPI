from fastapi import FastAPI
from routers import accessController, playersController, teamsController, gamesController
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(accessController.router)
app.include_router(playersController.router)
app.include_router(teamsController.router)
app.include_router(gamesController.router)

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