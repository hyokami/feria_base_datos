from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from modelo import DB_PATH, simular_torneo_completo, simulacion_monte_carlo

app = FastAPI(title="API Predicción UEFA Champions League 2027-2028")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimularRequest(BaseModel):
    temporada: int = 2027
    n_simulaciones: int = 5000

class PrediccionRequest(BaseModel):
    id_usuario_global: str
    id_equipo_campeon: int
    temporada: int = 2027

def obtener_equipos_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id_equipo, nombre, puntaje_poder FROM Equipos LIMIT 16")
    equipos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return equipos

@app.get("/api/champions/equipos")
def listar_equipos():
    equipos = obtener_equipos_db()
    return {"equipos": equipos}

@app.post("/api/champions/simular")
def ejecutar_simulacion(req: SimularRequest):
    if req.temporada not in (2027, 2028):
        raise HTTPException(status_code=400, detail="La temporada debe ser 2027 o 2028.")

    equipos = obtener_equipos_db()
    if len(equipos) != 16:
        raise HTTPException(status_code=400, detail="Se requieren exactamente 16 equipos en la base de datos.")

    resultado = simular_torneo_completo(equipos)
    campeon_id = resultado["campeon"]["id_equipo"]
    probabilidades = simulacion_monte_carlo(equipos, req.n_simulaciones)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Llaves_Torneo WHERE temporada = ?", (req.temporada,))

    for fase, cruces in resultado["arbol"].items():
        for c in cruces:
            cursor.execute("""
                INSERT INTO Llaves_Torneo (temporada, fase, id_equipo_a, id_equipo_b, id_ganador)
                VALUES (?, ?, ?, ?, ?)
            """, (req.temporada, fase, c["equipo_a"]["id_equipo"], c["equipo_b"]["id_equipo"], c["ganador"]["id_equipo"]))

    cursor.execute("""
        UPDATE Predicciones
        SET acierto = CASE WHEN id_equipo_campeon = ? THEN 1 ELSE 0 END
        WHERE temporada = ?
    """, (campeon_id, req.temporada))

    conn.commit()
    conn.close()

    return {
        "temporada": req.temporada,
        "campeon": resultado["campeon"],
        "arbol": resultado["arbol"],
        "probabilidades_campeon": probabilidades
    }

@app.post("/api/champions/predecir")
def guardar_prediccion(req: PrediccionRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Predicciones (id_usuario_global, id_equipo_campeon, temporada)
        VALUES (?, ?, ?)
    """, (req.id_usuario_global, req.id_equipo_campeon, req.temporada))
    conn.commit()
    id_creado = cursor.lastrowid
    conn.close()

    return {
        "mensaje": "Predicción registrada correctamente",
        "id_prediccion": id_creado,
        "temporada": req.temporada
    }