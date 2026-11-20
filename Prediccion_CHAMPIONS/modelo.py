import random
import sqlite3
from collections import Counter

DB_PATH = "champions.db"

def probabilidad_elo(score_a: float, score_b: float) -> float:
    """Fórmula 1: Probabilidad de que el equipo A elimine al equipo B."""
    return 1.0 / (1.0 + 10 ** ((score_b - score_a) / 400.0))

def recalcular_elo_desde_historial(factor_f: float = 32.0):
    """Fórmula 3: Recalcula el puntaje_poder desde Partidos_Historicos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id_equipo FROM Equipos")
    scores = {row[0]: 1500.0 for row in cursor.fetchall()}

    cursor.execute("""
        SELECT id_equipo_local, id_equipo_visitante, goles_local, goles_visitante
        FROM Partidos_Historicos
        ORDER BY temporada ASC, id_partido ASC
    """)
    partidos = cursor.fetchall()

    for local, visitante, g_local, g_vis in partidos:
        score_l = scores.get(local, 1500.0)
        score_v = scores.get(visitante, 1500.0)

        e_local = probabilidad_elo(score_l, score_v)
        e_vis = 1.0 - e_local

        if g_local > g_vis:
            s_local, s_vis = 1.0, 0.0
        elif g_local < g_vis:
            s_local, s_vis = 0.0, 1.0
        else:
            s_local, s_vis = 0.5, 0.5

        scores[local] = score_l + factor_f * (s_local - e_local)
        scores[visitante] = score_v + factor_f * (s_vis - e_vis)

    for id_eq, nuevo_score in scores.items():
        cursor.execute(
            "UPDATE Equipos SET puntaje_poder = ? WHERE id_equipo = ?",
            (round(nuevo_score, 2), id_eq)
        )

    conn.commit()
    conn.close()
    return scores

def simular_llave(equipo_a: dict, equipo_b: dict) -> dict:
    """Fórmula 2: Genera u entre 0.0 y 1.0; si u <= P(A) pasa A, si no pasa B."""
    p_a = probabilidad_elo(equipo_a["puntaje_poder"], equipo_b["puntaje_poder"])
    u = random.random()
    return equipo_a if u <= p_a else equipo_b

def simular_torneo_completo(equipos_16: list[dict]) -> dict:
    """Simula un árbol completo desde Octavos (16 equipos) hasta la Final."""
    ronda_actual = equipos_16[:]
    fases = ["Octavos", "Cuartos", "Semifinal", "Final"]
    arbol = {}

    for fase in fases:
        cruces = []
        ganadores = []
        for i in range(0, len(ronda_actual), 2):
            eq_a = ronda_actual[i]
            eq_b = ronda_actual[i + 1]
            ganador = simular_llave(eq_a, eq_b)
            cruces.append({
                "equipo_a": eq_a,
                "equipo_b": eq_b,
                "ganador": ganador,
                "prob_a": round(probabilidad_elo(eq_a["puntaje_poder"], eq_b["puntaje_poder"]) * 100, 2)
            })
            ganadores.append(ganador)
        arbol[fase] = cruces
        ronda_actual = ganadores

    return {
        "campeon": ronda_actual[0],
        "arbol": arbol
    }

def simulacion_monte_carlo(equipos_16: list[dict], n_simulaciones: int = 5000) -> list[dict]:
    """Fórmula 4: Repite el torneo N veces para calcular la probabilidad de campeón."""
    conteo_campeones = Counter()
    for _ in range(n_simulaciones):
        resultado = simular_torneo_completo(equipos_16)
        conteo_campeones[resultado["campeon"]["id_equipo"]] += 1

    probabilidades = []
    for eq in equipos_16:
        veces = conteo_campeones[eq["id_equipo"]]
        probabilidades.append({
            "id_equipo": eq["id_equipo"],
            "nombre": eq["nombre"],
            "puntaje_poder": eq["puntaje_poder"],
            "probabilidad_campeon": round((veces / n_simulaciones) * 100, 2)
        })

    return sorted(probabilidades, key=lambda x: x["probabilidad_campeon"], reverse=True)