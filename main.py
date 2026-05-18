from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(
    title="🎬 API Catálogo de Películas",
    description="""
    API REST para gestionar un catálogo de películas con base de datos SQLite.
    
    ## Funcionalidades
    - **Ver** todas las películas o buscar por ID
    - **Filtrar** por género
    - **Agregar** nuevas películas
    - **Actualizar** información de una película
    - **Eliminar** películas del catálogo
    """,
    version="2.0"
)

# ─────────────────────────────────────────
# CONEXIÓN A BASE DE DATOS SQLITE
# ─────────────────────────────────────────
conn = sqlite3.connect("peliculas.db", check_same_thread=False)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS peliculas (
        id       INTEGER PRIMARY KEY,
        titulo   TEXT NOT NULL,
        director TEXT NOT NULL,
        anio     INTEGER NOT NULL,
        genero   TEXT NOT NULL,
        rating   REAL NOT NULL,
        resena   TEXT
    )
""")

# Insertar datos iniciales solo si la tabla está vacía
cursor.execute("SELECT COUNT(*) FROM peliculas")
if cursor.fetchone()[0] == 0:
    datos_iniciales = [
        (1, "Inception",         "Christopher Nolan",    2010, "Ciencia Ficción", 8.8, "Una obra maestra de la narrativa visual."),
        (2, "El Padrino",        "Francis Ford Coppola", 1972, "Drama",           9.2, "La mejor película de la historia del cine."),
        (3, "Interstellar",      "Christopher Nolan",    2014, "Ciencia Ficción", 8.6, "Emotiva y científicamente fascinante."),
        (4, "Joker",             "Todd Phillips",        2019, "Drama",           8.4, "Actuación impecable de Joaquin Phoenix."),
        (5, "Avengers: Endgame", "Russo Brothers",       2019, "Acción",          8.4, "El cierre épico del universo Marvel."),
    ]
    cursor.executemany(
        "INSERT INTO peliculas VALUES (?, ?, ?, ?, ?, ?, ?)",
        datos_iniciales
    )
    conn.commit()

# ─────────────────────────────────────────
# MODELO DE DATOS
# ─────────────────────────────────────────
class Pelicula(BaseModel):
    id: int
    titulo: str
    director: str
    anio: int
    genero: str
    rating: float
    resena: Optional[str] = None

# ─────────────────────────────────────────
# FUNCIÓN AUXILIAR — convierte fila a dict
# ─────────────────────────────────────────
def fila_a_dict(fila):
    return {
        "id":       fila[0],
        "titulo":   fila[1],
        "director": fila[2],
        "anio":     fila[3],
        "genero":   fila[4],
        "rating":   fila[5],
        "resena":   fila[6]
    }

# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────

# GET — Todas las películas
@app.get("/peliculas", summary="Ver todas las películas", tags=["Películas"])
def get_peliculas():
    """Retorna el catálogo completo de películas."""
    cursor.execute("SELECT * FROM peliculas")
    filas = cursor.fetchall()
    return [fila_a_dict(f) for f in filas]

# GET — Película por ID
@app.get("/peliculas/{pelicula_id}", summary="Buscar película por ID", tags=["Películas"])
def get_pelicula(pelicula_id: int):
    """Busca y retorna una película específica por su ID."""
    cursor.execute("SELECT * FROM peliculas WHERE id=?", (pelicula_id,))
    fila = cursor.fetchone()
    if not fila:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return fila_a_dict(fila)

# GET — Filtrar por género
@app.get("/peliculas/genero/{genero}", summary="Filtrar por género", tags=["Películas"])
def get_por_genero(genero: str):
    """Filtra películas por género."""
    cursor.execute("SELECT * FROM peliculas WHERE LOWER(genero)=LOWER(?)", (genero,))
    filas = cursor.fetchall()
    if not filas:
        raise HTTPException(status_code=404, detail=f"No hay películas del género '{genero}'")
    return [fila_a_dict(f) for f in filas]

# POST — Agregar película
@app.post("/peliculas", summary="Agregar película", tags=["Películas"])
def create_pelicula(pelicula: Pelicula):
    """Agrega una nueva película al catálogo."""
    try:
        cursor.execute(
            "INSERT INTO peliculas VALUES (?, ?, ?, ?, ?, ?, ?)",
            (pelicula.id, pelicula.titulo, pelicula.director,
             pelicula.anio, pelicula.genero, pelicula.rating, pelicula.resena)
        )
        conn.commit()
        return {"mensaje": "Película agregada con éxito", "pelicula": pelicula}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Ya existe una película con ese ID")

# PUT — Actualizar película
@app.put("/peliculas/{pelicula_id}", summary="Actualizar película", tags=["Películas"])
def update_pelicula(pelicula_id: int, pelicula: Pelicula):
    """Actualiza los datos de una película existente."""
    cursor.execute("""
        UPDATE peliculas
        SET titulo=?, director=?, anio=?, genero=?, rating=?, resena=?
        WHERE id=?
    """, (pelicula.titulo, pelicula.director, pelicula.anio,
          pelicula.genero, pelicula.rating, pelicula.resena, pelicula_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return {"mensaje": "Película actualizada con éxito", "pelicula": pelicula}

# DELETE — Eliminar película
@app.delete("/peliculas/{pelicula_id}", summary="Eliminar película", tags=["Películas"])
def delete_pelicula(pelicula_id: int):
    """Elimina una película del catálogo por su ID."""
    cursor.execute("SELECT titulo FROM peliculas WHERE id=?", (pelicula_id,))
    fila = cursor.fetchone()
    if not fila:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    cursor.execute("DELETE FROM peliculas WHERE id=?", (pelicula_id,))
    conn.commit()
    return {"mensaje": f"Película '{fila[0]}' eliminada con éxito"}