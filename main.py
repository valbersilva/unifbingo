from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import random
import uuid

app = FastAPI()

# Armazena os jogos ativos
bingo_games = {}

# Estrutura para armazenar conexões WebSocket
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

class CreateGameRequest(BaseModel):
    user_name: str

class JoinGameRequest(BaseModel):
    user_name: str
    room_code: str

class MarkNumberRequest(BaseModel):
    user_name: str
    room_code: str
    number: int

@app.post("/create_game")
async def create_game(request: CreateGameRequest):
    room_code = str(random.randint(10000, 99999))
    bingo_games[room_code] = {
        "host": request.user_name,
        "players": {},
        "drawn_numbers": [],
        "winner": None
    }
    return {"room_code": room_code}

@app.post("/join_game")
async def join_game(request: JoinGameRequest):
    if request.room_code not in bingo_games:
        return {"error": "Sala não encontrada"}

    user_cartela = random.sample(range(1, 76), 25)  # Simulação de cartela
    bingo_games[request.room_code]["players"][request.user_name] = {
        "cartela": user_cartela,
        "marked_numbers": set()
    }
    return {"message": "Entrou na sala", "cartela": user_cartela}

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await manager.connect(websocket, room_code)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)

@app.post("/draw_number/{room_code}")
async def draw_number(room_code: str):
    if room_code not in bingo_games:
        return {"error": "Sala não encontrada"}

    game = bingo_games[room_code]
    if len(game["drawn_numbers"]) >= 75:
        return {"error": "Todos os números já foram sorteados"}

    new_number = random.choice([i for i in range(1, 76) if i not in game["drawn_numbers"]])
    game["drawn_numbers"].append(new_number)

    await manager.broadcast({"type": "new_number", "number": new_number}, room_code)

    return {"new_number": new_number, "drawn_numbers": game["drawn_numbers"]}

@app.post("/mark_number")
async def mark_number(request: MarkNumberRequest):
    game = bingo_games.get(request.room_code)
    if not game:
        return {"error": "Sala não encontrada"}

    player = game["players"].get(request.user_name)
    if not player:
        return {"error": "Usuário não encontrado na sala"}

    if request.number not in player["cartela"]:
        return {"error": "Número não está na cartela"}

    player["marked_numbers"].add(request.number)

    # Verifica se o jogador ganhou
    if player["marked_numbers"] == set(player["cartela"]):
        game["winner"] = request.user_name
        await manager.broadcast({"type": "winner", "winner": request.user_name}, request.room_code)

    return {"message": "Número marcado"}

@app.get("/game_status/{room_code}")
async def game_status(room_code: str):
    game = bingo_games.get(room_code)
    if not game:
        return {"error": "Sala não encontrada"}

    return {
        "drawn_numbers": game["drawn_numbers"],
        "winner": game["winner"]
    }
