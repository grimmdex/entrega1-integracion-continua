# Gestor de Tareas — Proyecto de software basado en herramientas de integración continua

**Politécnico Grancolombiano** — Módulo *Énfasis Profesional I (Integración Continua)*
**Entrega 1 — Semana 3 (Escenario 3)**

---

## 1. Descripción

API REST para la gestión de tareas de un equipo de desarrollo, construida como
plataforma de dos contenedores Docker que se comunican entre sí a través de una
red definida por el usuario.

| | Contenedor 1 | Contenedor 2 |
|---|---|---|
| **Servicio** | `web` | `db` |
| **Nombre** | `ci_web` | `ci_db` |
| **Tecnología** | Python 3.12 + Flask + Gunicorn | PostgreSQL 16 (Alpine) |
| **Origen de la imagen** | Construida con `app/Dockerfile` | Imagen oficial `postgres:16-alpine` |
| **Puerto interno** | 5000 | 5432 |
| **Publicado en el host** | 8080 | no se publica (solo red interna) |

## 2. Cómo se comunican los contenedores

Ambos servicios se conectan a la red bridge **`red-ci`** declarada en
`docker-compose.yml`. Docker provee resolución DNS interna dentro de esa red,
de modo que el contenedor `web` alcanza al contenedor `db` usando el **nombre
del servicio como nombre de host**:

```
DB_HOST = db      →  db:5432/tareasdb
```

No se usa `localhost` porque dentro de un contenedor `localhost` apunta al
propio contenedor. El contenedor `db` **no publica puertos al host**: solo es
accesible desde dentro de la red `red-ci`, lo que demuestra que la comunicación
ocurre de contenedor a contenedor y no a través de la máquina anfitriona.

El arranque está ordenado con `depends_on` + `condition: service_healthy`, de
forma que `web` solo inicia cuando PostgreSQL ya responde a `pg_isready`.

## 3. Estructura del repositorio

```
entrega1-integracion-continua/
├── app/                        # CONTENEDOR 1 (servicio web)
│   ├── app.py                  # API REST en Flask
│   ├── requirements.txt        # dependencias de Python
│   ├── Dockerfile              # construcción de la imagen del servicio web
│   ├── .dockerignore
│   └── tests/
│       └── test_app.py         # pruebas unitarias
├── db/                         # CONTENEDOR 2 (base de datos)
│   └── init.sql                # creación de la tabla y datos iniciales
├── .github/
│   └── workflows/
│       └── ci.yml              # pipeline de integración continua
├── evidencias/                 # capturas y salidas de la ejecución
├── docs/                       # documento de la entrega
├── docker-compose.yml          # orquestación de los dos contenedores
├── env.example                 # plantilla de variables de entorno
├── .gitignore
└── README.md
```

## 4. Requisitos

- Docker Engine 20.10 o superior
- Docker Compose v2 (`docker compose`)

## 5. Puesta en marcha

```bash
git clone <URL-DEL-REPOSITORIO>
cd entrega1-integracion-continua
cp env.example .env          # opcional: si no existe se usan los valores por defecto
docker compose up --build -d
```

Verificar que ambos contenedores están arriba:

```bash
docker compose ps
```

## 6. Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Identificación del servicio |
| GET | `/health` | **Prueba de comunicación entre contenedores** |
| GET | `/api/tareas` | Lista todas las tareas (lee de PostgreSQL) |
| GET | `/api/tareas/<id>` | Consulta una tarea |
| POST | `/api/tareas` | Crea una tarea (escribe en PostgreSQL) |
| DELETE | `/api/tareas/<id>` | Elimina una tarea |

## 7. Pruebas de la comunicación

**a) Estado de la conexión entre los dos contenedores**

```bash
curl http://localhost:8080/health
```

**b) Lectura de datos desde el contenedor de base de datos**

```bash
curl http://localhost:8080/api/tareas
```

**c) Escritura desde el contenedor web hacia el contenedor de base de datos**

```bash
curl http://localhost:8080/api/tareas \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"titulo":"Nueva tarea","descripcion":"Creada desde la API","responsable":"Equipo"}'
```

**d) Resolución DNS del contenedor `db` desde el contenedor `web`**

```bash
docker compose exec web getent hosts db
```

**e) Verificación directa en el motor de base de datos**

```bash
docker compose exec db psql -U ciuser -d tareasdb -c "SELECT id, titulo, estado FROM tareas;"
```

**f) Inspección de la red compartida**

```bash
docker network inspect entrega1-integracion-continua_red-ci
```

## 8. Pruebas unitarias

```bash
cd app && python -m pytest tests/ -v
```

También se ejecutan automáticamente en el pipeline de GitHub Actions
(`.github/workflows/ci.yml`) en cada *push* y *pull request*.

## 9. Detener el entorno

```bash
docker compose down        # detiene y elimina los contenedores
docker compose down -v     # además elimina el volumen de datos
```

## 10. Flujo de trabajo en el repositorio

- `main` — rama estable; solo recibe cambios por *pull request*.
- `develop` — rama de integración del equipo.
- `feature/<nombre>` — ramas de trabajo individuales.

Cada *pull request* dispara el pipeline de integración continua, que debe pasar
en verde antes de poder fusionar.
