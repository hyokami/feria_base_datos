import csv
import os
import re

CARPETA_CRUDOS = "datos_crudos"
ARCHIVO_LIMPIO = "dataset_uefa.csv"

TEMPORADAS = {
    "2021-22": 2022,
    "2022-23": 2023,
    "2023-24": 2024,
    "2024-25": 2025,
    "2025-26": 2026,
}

# Diccionario actualizado con todos los nombres exactos que aparecen en tus cl.txt
UNIFICAR_NOMBRES = {
    "Real Madrid": "Real Madrid",
    "Real Madrid CF": "Real Madrid",
    "Bayern München": "Bayern Múnich",
    "FC Bayern München": "Bayern Múnich",
    "Bayern Munich": "Bayern Múnich",
    "Manchester City": "Manchester City",
    "Manchester City FC": "Manchester City",
    "Man City": "Manchester City",
    "Arsenal": "Arsenal",
    "Arsenal FC": "Arsenal",
    "FC Barcelona": "FC Barcelona",
    "Barcelona": "FC Barcelona",
    "Paris Saint-Germain": "Paris Saint-Germain",
    "Paris Saint-Germain FC": "Paris Saint-Germain",
    "PSG": "Paris Saint-Germain",
    "Inter": "Inter de Milán",
    "Inter Milan": "Inter de Milán",
    "FC Internazionale Milano": "Inter de Milán",
    "Liverpool": "Liverpool",
    "Liverpool FC": "Liverpool",
    "Atlético Madrid": "Atlético de Madrid",
    "Atlético de Madrid": "Atlético de Madrid",
    "Club Atlético de Madrid": "Atlético de Madrid",
    "Atletico Madrid": "Atlético de Madrid",
    "Borussia Dortmund": "Borussia Dortmund",
    "Juventus": "Juventus",
    "Juventus FC": "Juventus",
    "AC Milan": "AC Milan",
    "Milan": "AC Milan",
    "FC Porto": "FC Porto",
    "Porto": "FC Porto",
    "SL Benfica": "SL Benfica",
    "Sport Lisboa e Benfica": "SL Benfica",
    "Benfica": "SL Benfica",
    "PSV Eindhoven": "PSV Eindhoven",
    "PSV": "PSV Eindhoven",
    "Sporting CP": "Sporting CP",
    "Sporting Clube de Portugal": "Sporting CP",
    "Sporting Lisbon": "Sporting CP",
}

def limpiar_nombre(nombre: str) -> str:
    nombre = re.sub(r"\([A-Z]{3}\)", "", nombre)
    nombre = re.sub(r"^\d{1,2}[.:]\d{2}\s+", "", nombre.strip())
    nombre = nombre.strip(" -–\t")
    return UNIFICAR_NOMBRES.get(nombre, nombre)

def ejecutar_etl():
    filas_limpias = []
    vistos = set()

    for carpeta, anio in TEMPORADAS.items():
        ruta_txt = os.path.join(CARPETA_CRUDOS, carpeta, "cl.txt")
        if not os.path.exists(ruta_txt):
            print(f"Aviso: No se encontró {ruta_txt}, se omite.")
            continue

        fase_actual = "Fase de Liga/Grupos"
        with open(ruta_txt, "r", encoding="utf-8") as f:
            for linea in f:
                linea_strip = linea.strip()
                if not linea_strip or linea_strip.startswith("#"):
                    continue

                if linea_strip.startswith("»") or linea_strip.startswith("="):
                    texto_fase = linea_strip.lstrip("»= ").strip()
                    if "Round of 16" in texto_fase:
                        fase_actual = "Octavos"
                    elif "Quarter" in texto_fase:
                        fase_actual = "Cuartos"
                    elif "Semi" in texto_fase:
                        fase_actual = "Semifinal"
                    elif "Final" in texto_fase:
                        fase_actual = "Final"
                    else:
                        fase_actual = texto_fase[:40]
                    continue

                # Formato real de tus archivos: [hora opcional] Equipo A  v  Equipo B  GolesL-GolesV ...
                match = re.search(
                    r"^(?:\s*\d{1,2}[.:]\d{2}\s+)?(.+?)\s+v\s+(.+?)\s+(\d+)-(\d+)(?:\s|$)",
                    linea_strip
                )
                if match:
                    local = limpiar_nombre(match.group(1))
                    visitante = limpiar_nombre(match.group(2))
                    goles_l = int(match.group(3))
                    goles_v = int(match.group(4))

                    if len(local) < 2 or len(visitante) < 2:
                        continue

                    clave = (anio, fase_actual, local, visitante, goles_l, goles_v)
                    if clave in vistos:
                        continue
                    vistos.add(clave)

                    filas_limpias.append({
                        "temporada": anio,
                        "fase": fase_actual,
                        "equipo_local": local,
                        "equipo_visitante": visitante,
                        "goles_local": goles_l,
                        "goles_visitante": goles_v
                    })

    with open(ARCHIVO_LIMPIO, "w", encoding="utf-8", newline="") as f:
        columnas = ["temporada", "fase", "equipo_local", "equipo_visitante", "goles_local", "goles_visitante"]
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas_limpias)

    print(f"ETL completado: {len(filas_limpias)} partidos limpios guardados en '{ARCHIVO_LIMPIO}'.")

if __name__ == "__main__":
    ejecutar_etl()