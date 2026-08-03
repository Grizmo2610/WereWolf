import os

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db.database import init_db
from room_manager import RoomManager
from scenarios import SCENARIOS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Ma Sói Online")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend/templates"))

room_manager = RoomManager()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def lobby(request: Request):
    return templates.TemplateResponse(request, "lobby.html", {
        "scenarios": SCENARIOS.values(),
    })


@app.post("/rooms")
async def create_room(request: Request):
    form = await request.form()
    scenario_id = form.get("scenario_id", "classic_9")
    total_players = int(form.get("total_players", 9))

    room = room_manager.create_room(scenario_id=scenario_id, total_players=total_players, provider_keys=None)
    room_manager.start_game(room.room_code)
    return RedirectResponse(f"/game/{room.room_code}", status_code=303)


@app.get("/game/{room_code}")
def game_page(request: Request, room_code: str):
    room = room_manager.get_room(room_code)
    return templates.TemplateResponse(request, "game.html", {
        "room_code": room_code,
        "room": room,
    })


@app.websocket("/ws/{room_code}")
async def game_ws(websocket: WebSocket, room_code: str):
    await websocket.accept()
    room = room_manager.get_room(room_code)
    if room is None:
        await websocket.close()
        return
    room.websockets.append(websocket)
    await room.broadcast_state()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in room.websockets:
            room.websockets.remove(websocket)
