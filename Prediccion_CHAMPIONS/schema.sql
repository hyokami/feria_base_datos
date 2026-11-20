CREATE TABLE IF NOT EXISTS Equipos (
    id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    puntaje_poder REAL DEFAULT 1500.0
);

CREATE TABLE IF NOT EXISTS Partidos_Historicos (
    id_partido INTEGER PRIMARY KEY AUTOINCREMENT,
    temporada INTEGER NOT NULL,
    fase TEXT NOT NULL,
    id_equipo_local INTEGER NOT NULL,
    id_equipo_visitante INTEGER NOT NULL,
    goles_local INTEGER NOT NULL,
    goles_visitante INTEGER NOT NULL,
    FOREIGN KEY (id_equipo_local) REFERENCES Equipos(id_equipo),
    FOREIGN KEY (id_equipo_visitante) REFERENCES Equipos(id_equipo)
);

CREATE TABLE IF NOT EXISTS Llaves_Torneo (
    id_llave INTEGER PRIMARY KEY AUTOINCREMENT,
    temporada INTEGER NOT NULL,
    fase TEXT NOT NULL,
    id_equipo_a INTEGER NOT NULL,
    id_equipo_b INTEGER NOT NULL,
    id_ganador INTEGER,
    FOREIGN KEY (id_equipo_a) REFERENCES Equipos(id_equipo),
    FOREIGN KEY (id_equipo_b) REFERENCES Equipos(id_equipo),
    FOREIGN KEY (id_ganador) REFERENCES Equipos(id_equipo)
);

CREATE TABLE IF NOT EXISTS Predicciones (
    id_prediccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario_global TEXT NOT NULL,
    id_equipo_campeon INTEGER NOT NULL,
    temporada INTEGER NOT NULL,
    acierto INTEGER DEFAULT NULL,
    FOREIGN KEY (id_equipo_campeon) REFERENCES Equipos(id_equipo)
);