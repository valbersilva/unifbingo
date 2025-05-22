from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import random
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Conexão com MongoDB via motor (async)
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.unibingo
games_collection = db.bingo_games

class CreateGameRequest(BaseModel):
    user_name: str

class JoinGameRequest(BaseModel):
    user_name: str
    room_code: str

class MarkNumberRequest(BaseModel):
    user_name: str
    room_code: str
    number: int

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, room_code: str):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = []
        self.active_connections[room_code].append(websocket)

    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.active_connections:
            self.active_connections[room_code].remove(websocket)
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]

    async def broadcast(self, message: dict, room_code: str):
        if room_code in self.active_connections:
            for connection in self.active_connections[room_code]:
                await connection.send_json(message)

manager = ConnectionManager()

@app.post("/create_game")
async def create_game(request: CreateGameRequest):
    room_code = str(random.randint(10000, 99999))
    game = {
        "room_code": room_code,
        "host": request.user_name,
        "players": {},
        "drawn_numbers": [],
        "winner": None
    }
    await games_collection.insert_one(game)
    return {"room_code": room_code}

@app.post("/join_game")
async def join_game(request: JoinGameRequest):
    game = await games_collection.find_one({"room_code": request.room_code})
    if not game:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

    user_cartela = random.sample(range(1, 76), 25)  # Simula cartela

    # Atualiza players no banco
    players = game.get("players", {})
    players[request.user_name] = {
        "cartela": user_cartela,
        "marked_numbers": []
    }
    await games_collection.update_one(
        {"room_code": request.room_code},
        {"$set": {"players": players}}
    )
    return {"message": "Entrou na sala", "cartela": user_cartela}

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await manager.connect(websocket, room_code)
    try:
        while True:
            data = await websocket.receive_text()
            # Aqui você pode tratar mensagens recebidas via WS
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)

@app.post("/draw_number/{room_code}")
async def draw_number(room_code: str):
    game = await games_collection.find_one({"room_code": room_code})
    if not game:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

    drawn_numbers = game.get("drawn_numbers", [])
    if len(drawn_numbers) >= 75:
        return {"error": "Todos os números já foram sorteados"}

    new_number = random.choice([i for i in range(1, 76) if i not in drawn_numbers])
    drawn_numbers.append(new_number)

    await games_collection.update_one(
        {"room_code": room_code},
        {"$set": {"drawn_numbers": drawn_numbers}}
    )

    await manager.broadcast({"type": "new_number", "number": new_number}, room_code)

    return {"new_number": new_number, "drawn_numbers": drawn_numbers}

@app.post("/mark_number")
async def mark_number(request: MarkNumberRequest):
    game = await games_collection.find_one({"room_code": request.room_code})
    if not game:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

    players = game.get("players", {})
    player = players.get(request.user_name)
    if not player:
        raise HTTPException(status_code=404, detail="Usuário não encontrado na sala")

    if request.number not in player["cartela"]:
        return {"error": "Número não está na cartela"}

    marked_numbers = set(player.get("marked_numbers", []))
    marked_numbers.add(request.number)
    players[request.user_name]["marked_numbers"] = list(marked_numbers)

    # Atualiza o player no banco
    await games_collection.update_one(
        {"room_code": request.room_code},
        {"$set": {"players": players}}
    )

    # Verifica se o jogador ganhou (marcou todos os números da cartela)
    if set(player["cartela"]) == marked_numbers:
        await games_collection.update_one(
            {"room_code": request.room_code},
            {"$set": {"winner": request.user_name}}
        )
        await manager.broadcast({"type": "winner", "winner": request.user_name}, request.room_code)

    return {"message": "Número marcado"}

@app.get("/game_status/{room_code}")
async def game_status(room_code: str):
    game = await games_collection.find_one({"room_code": room_code})
    if not game:
        raise HTTPException(status_code=404, detail="Sala não encontrada")

    return {
        "drawn_numbers": game.get("drawn_numbers", []),
        "winner": game.get("winner")
    }
