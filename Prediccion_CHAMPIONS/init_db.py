import csv
import sqlite3
from modelo import DB_PATH, recalcular_elo_desde_historial

EQUIPOS_16 = [
    "Real Madrid", "Bayern Múnich", "Manchester City", "Arsenal",
    "FC Barcelona", "Paris Saint-Germain", "Inter de Milán", "Liverpool",
    "Atlético de Madrid", "Borussia Dortmund", "Juventus", "AC Milan",
    "FC Porto", "SL Benfica", "PSV Eindhoven", "Sporting CP"
]

def inicializar():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open("schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    for nombre in EQUIPOS_16:
        cursor.execute("INSERT OR IGNORE INTO Equipos (nombre) VALUES (?)", (nombre,))

    cursor.execute("SELECT id_equipo, nombre FROM Equipos")
    mapa_equipos = {nombre: id_eq for id_eq, nombre in cursor.fetchall()}

    cursor.execute("DELETE FROM Partidos_Historicos")
    partidos_cargados = 0

    with open("dataset_uefa.csv", "r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            id_local = mapa_equipos.get(fila["equipo_local"].strip())
            id_vis = mapa_equipos.get(fila["equipo_visitante"].strip())

            if id_local and id_vis:
                cursor.execute("""
                    INSERT INTO Partidos_Historicos
                    (temporada, fase, id_equipo_local, id_equipo_visitante, goles_local, goles_visitante)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    int(fila["temporada"]),
                    fila["fase"].strip(),
                    id_local,
                    id_vis,
                    int(fila["goles_local"]),
                    int(fila["goles_visitante"])
                ))
                partidos_cargados += 1

    conn.commit()
    conn.close()

    recalcular_elo_desde_historial(factor_f=32.0)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"Base de datos 'champions.db' lista con {partidos_cargados} partidos históricos.")
    print("Puntajes Elo calculados:")
    for row in cursor.execute("SELECT id_equipo, nombre, puntaje_poder FROM Equipos ORDER BY puntaje_poder DESC"):
        print(f"  {row[0]:2d}. {row[1]:<22} -> Elo: {row[2]}")
    conn.close()

if __name__ == "__main__":
    inicializar()