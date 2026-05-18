import requests

BASE_URL = "http://127.0.0.1:8000"

def menu():
    print("\n🎬 ====== CATÁLOGO DE PELÍCULAS ======")
    print("1. Ver todas las películas")
    print("2. Buscar película por ID")
    print("3. Filtrar por género")
    print("4. Agregar nueva película")
    print("5. Actualizar película")
    print("6. Eliminar película")
    print("7. Salir")

def ver_todas():
    r = requests.get(f"{BASE_URL}/peliculas")
    peliculas = r.json()
    print(f"\n✅ {len(peliculas)} películas en catálogo:")
    for p in peliculas:
        print(f"   [{p['id']}] {p['titulo']} ({p['anio']}) ⭐ {p['rating']} - {p['genero']}")

def buscar_por_id():
    id = int(input("Ingresa el ID: "))
    r = requests.get(f"{BASE_URL}/peliculas/{id}")
    if r.status_code == 200:
        p = r.json()
        print(f"\n✅ Película encontrada:")
        print(f"   🎬 Título    : {p['titulo']}")
        print(f"   🎥 Director  : {p['director']}")
        print(f"   📅 Año       : {p['anio']}")
        print(f"   🏷️  Género    : {p['genero']}")
        print(f"   ⭐ Rating    : {p['rating']}/10")
        print(f"   📝 Reseña    : {p.get('resena', 'Sin reseña')}")
    else:
        print("❌", r.json()["detail"])

def filtrar_genero():
    genero = input("Ingresa el género (Drama / Acción / Ciencia Ficción): ")
    r = requests.get(f"{BASE_URL}/peliculas/genero/{genero}")
    if r.status_code == 200:
        peliculas = r.json()
        print(f"\n✅ Películas de {genero}:")
        for p in peliculas:
            print(f"   [{p['id']}] {p['titulo']} ⭐ {p['rating']}")
    else:
        print("❌", r.json()["detail"])

def agregar_pelicula():
    print("\n── Nueva Película ──")
    id       = int(input("ID: "))
    titulo   = input("Título: ")
    director = input("Director: ")
    anio     = int(input("Año: "))
    genero   = input("Género: ")
    rating   = float(input("Rating (1.0 - 10.0): "))
    resena   = input("Reseña (Enter para omitir): ").strip() or None

    payload = {"id": id, "titulo": titulo, "director": director,
               "anio": anio, "genero": genero, "rating": rating, "resena": resena}
    r = requests.post(f"{BASE_URL}/peliculas", json=payload)
    if r.status_code == 200:
        print("✅", r.json()["mensaje"])
    else:
        print("❌", r.json()["detail"])

def actualizar_pelicula():
    id = int(input("ID de la película a actualizar: "))
    print("── Nuevos datos ──")
    titulo   = input("Título: ")
    director = input("Director: ")
    anio     = int(input("Año: "))
    genero   = input("Género: ")
    rating   = float(input("Rating: "))
    resena   = input("Reseña: ").strip() or None

    payload = {"id": id, "titulo": titulo, "director": director,
               "anio": anio, "genero": genero, "rating": rating, "resena": resena}
    r = requests.put(f"{BASE_URL}/peliculas/{id}", json=payload)
    if r.status_code == 200:
        print("✅", r.json()["mensaje"])
    else:
        print("❌", r.json()["detail"])

def eliminar_pelicula():
    id = int(input("ID de la película a eliminar: "))
    r = requests.delete(f"{BASE_URL}/peliculas/{id}")
    if r.status_code == 200:
        print("✅", r.json()["mensaje"])
    else:
        print("❌", r.json()["detail"])

def main():
    while True:
        menu()
        opcion = input("\nElige una opción: ").strip()
        opciones = {
            "1": ver_todas,
            "2": buscar_por_id,
            "3": filtrar_genero,
            "4": agregar_pelicula,
            "5": actualizar_pelicula,
            "6": eliminar_pelicula,
        }
        if opcion == "7":
            print("👋 Hasta luego.")
            break
        elif opcion in opciones:
            opciones[opcion]()
        else:
            print("⚠️ Opción no válida.")

if __name__ == "__main__":
    main()