"""
API REST - Gestor de Tareas
Proyecto de software basado en herramientas de integracion continua
Politecnico Grancolombiano - Enfasis Profesional I

Contenedor 1 (este): servicio web Flask.
Se comunica por red Docker con el Contenedor 2 (PostgreSQL)
usando el nombre de servicio 'db' como host.
"""
import os
import time

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)

# --- Parametros de conexion al Contenedor 2 (PostgreSQL) ---------------------
# DB_HOST = 'db' -> nombre del servicio en docker-compose. Docker lo resuelve
# por DNS interno dentro de la red 'red-ci', por eso NO se usa localhost.
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tareasdb")
DB_USER = os.getenv("DB_USER", "ciuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cipassword")


def get_connection(reintentos: int = 10, espera: int = 3):
    """Abre conexion con el contenedor de PostgreSQL.

    Reintenta porque al levantar el stack el contenedor web puede quedar
    listo antes que el motor de base de datos.
    """
    ultimo_error = None
    for intento in range(1, reintentos + 1):
        try:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=5,
            )
        except psycopg2.OperationalError as exc:
            ultimo_error = exc
            app.logger.warning(
                "Intento %s/%s: base de datos no disponible aun (%s)",
                intento, reintentos, exc,
            )
            time.sleep(espera)
    raise ultimo_error


# --- Endpoints ---------------------------------------------------------------
@app.route("/", methods=["GET"])
def inicio():
    """Identifica el servicio."""
    return jsonify({
        "servicio": "API Gestor de Tareas",
        "contenedor": "web (Flask)",
        "se_conecta_a": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "endpoints": ["/health", "/api/tareas", "/api/tareas/<id>"],
    })


@app.route("/health", methods=["GET"])
def health():
    """Prueba de comunicacion entre los dos contenedores.

    Consulta la version del motor al Contenedor 2. Si responde, la
    comunicacion por la red Docker esta operativa.
    """
    try:
        conn = get_connection(reintentos=2, espera=1)
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
        conn.close()
        return jsonify({
            "estado": "ok",
            "comunicacion_contenedores": "establecida",
            "host_base_datos": DB_HOST,
            "motor": version,
        }), 200
    except Exception as exc:  # noqa: BLE001
        return jsonify({
            "estado": "error",
            "comunicacion_contenedores": "fallida",
            "detalle": str(exc),
        }), 503


@app.route("/api/tareas", methods=["GET"])
def listar_tareas():
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, titulo, descripcion, estado, responsable, creada_en "
            "FROM tareas ORDER BY id;"
        )
        filas = cur.fetchall()
    conn.close()
    return jsonify({"total": len(filas), "tareas": filas})


@app.route("/api/tareas/<int:tarea_id>", methods=["GET"])
def obtener_tarea(tarea_id):
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, titulo, descripcion, estado, responsable, creada_en "
            "FROM tareas WHERE id = %s;",
            (tarea_id,),
        )
        fila = cur.fetchone()
    conn.close()
    if fila is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(fila)


@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    datos = request.get_json(silent=True) or {}
    titulo = datos.get("titulo")
    if not titulo:
        return jsonify({"error": "El campo 'titulo' es obligatorio"}), 400

    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO tareas (titulo, descripcion, estado, responsable) "
            "VALUES (%s, %s, %s, %s) "
            "RETURNING id, titulo, descripcion, estado, responsable, creada_en;",
            (
                titulo,
                datos.get("descripcion", ""),
                datos.get("estado", "pendiente"),
                datos.get("responsable", "sin asignar"),
            ),
        )
        nueva = cur.fetchone()
    conn.commit()
    conn.close()
    return jsonify(nueva), 201


@app.route("/api/tareas/<int:tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tareas WHERE id = %s RETURNING id;", (tarea_id,))
        borrada = cur.fetchone()
    conn.commit()
    conn.close()
    if borrada is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify({"eliminada": tarea_id}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
