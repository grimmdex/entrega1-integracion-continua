-- ============================================================================
-- CONTENEDOR 2 - Base de datos PostgreSQL
-- Script de inicializacion: se ejecuta automaticamente la primera vez que
-- arranca el contenedor (se monta en /docker-entrypoint-initdb.d/).
-- ============================================================================

CREATE TABLE IF NOT EXISTS tareas (
    id          SERIAL PRIMARY KEY,
    titulo      VARCHAR(150) NOT NULL,
    descripcion TEXT         DEFAULT '',
    estado      VARCHAR(30)  NOT NULL DEFAULT 'pendiente',
    responsable VARCHAR(100) DEFAULT 'sin asignar',
    creada_en   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tareas_estado ON tareas (estado);

-- Datos de prueba para evidenciar la comunicacion entre contenedores
INSERT INTO tareas (titulo, descripcion, estado, responsable) VALUES
    ('Crear repositorio en GitHub',
     'Inicializar el repositorio remoto del proyecto y definir ramas main y develop',
     'completada', 'Equipo'),
    ('Construir contenedor de aplicacion',
     'Escribir el Dockerfile del servicio web en Flask',
     'completada', 'Equipo'),
    ('Construir contenedor de base de datos',
     'Configurar la imagen de PostgreSQL y el script de inicializacion',
     'completada', 'Equipo'),
    ('Verificar comunicacion entre contenedores',
     'Probar el endpoint /health y la consulta a la tabla tareas',
     'en progreso', 'Equipo'),
    ('Preparar entrega de la semana 3',
     'Documentar arquitectura, evidencias y conclusiones',
     'pendiente', 'Equipo');
