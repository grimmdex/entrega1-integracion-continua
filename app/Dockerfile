# ============================================================================
# CONTENEDOR 1 - Servicio web (API REST en Flask)
# Proyecto de software basado en herramientas de integracion continua
# ============================================================================

# Imagen base ligera y oficial de Python
FROM python:3.12-slim

# Metadatos de la imagen
LABEL proyecto="Gestor de Tareas - Integracion Continua"
LABEL institucion="Politecnico Grancolombiano"
LABEL contenedor="web"

# Evita archivos .pyc y fuerza salida sin buffer (logs en tiempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Dependencias del sistema necesarias para psycopg2 y para el healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Se copian primero las dependencias para aprovechar la cache de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Se copia el codigo fuente de la aplicacion
COPY . .

# Usuario sin privilegios (buena practica de seguridad)
RUN useradd --create-home appuser && chown -R appuser:appuser /usr/src/app
USER appuser

# Puerto que expone el contenedor
EXPOSE 5000

# Verificacion de salud del contenedor
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1

# Servidor de produccion WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
