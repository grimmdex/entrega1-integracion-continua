"""Pruebas unitarias basicas. Se ejecutan en el pipeline de GitHub Actions."""
import app as aplicacion


def test_endpoint_inicio_responde():
    cliente = aplicacion.app.test_client()
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["contenedor"] == "web (Flask)"


def test_host_base_datos_es_el_servicio_docker():
    """El host debe ser el nombre del servicio, no localhost."""
    assert aplicacion.DB_HOST == "db"


def test_crear_tarea_sin_titulo_devuelve_400():
    cliente = aplicacion.app.test_client()
    respuesta = cliente.post("/api/tareas", json={})
    assert respuesta.status_code == 400
