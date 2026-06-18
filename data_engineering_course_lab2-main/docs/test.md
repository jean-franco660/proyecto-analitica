# Asignaciones y Notas Para el Profesor

Este archivo mantiene el material orientado al profesor separado del README
principal para estudiantes. Usalo para planificar trabajo por grupos, puntos de
control en clase y extensiones opcionales.

## Material de Ensenanza

Material sugerido para estudiantes:

- Comparacion entre batch y streaming.
- Contratos de datos para cada servicio.
- Asignaciones grupales que se puedan realizar en paralelo.
- Checklist de calidad de datos.
- Diagrama de arquitectura.
- Guia de solucion de problemas.
- Estudio de caso de levantamiento de requisitos: `docs/requirements-gathering.md`.
- Estudio de caso de requisitos con CTO: `docs/cto-requirements-gathering.md`.
- Estudio de caso de requisitos con marketing: `docs/marketing-requirements-gathering.md`.
- Estudio de caso de requisitos con ingenieria de software: `docs/software-engineering-requirements-gathering.md`.
- Estudio de caso de requisitos del recomendador con data scientist: `docs/data-scientist-recommender-requirements.md`.

## Datos Fuente y Artefactos

Los datos principales necesarios para el laboratorio local ya fueron recopilados:

- DDL y datos de la tabla `ratings` en `db/classicmodels_lab2.sql`.
- `item_embeddings.csv` y `user_embeddings.csv` cargados en MinIO y `vector_db`.
- Artefactos del modelo copiados a `ml-artifacts/` y subidos a MinIO:
  - `best_model.pth`
  - `item_ohe.pkl`
  - `item_std_scaler.pkl`
  - `user_ohe.pkl`
  - `user_std_scaler.pkl`

Mejoras futuras opcionales:

- Usar el modelo PyTorch y los archivos de scalers en `recommendation_api/`.
- Agregar diagramas mas completos y hojas de trabajo para estudiantes.

## Estrategia de Asignaciones Para Estudiantes

Como las clases de fin de semana hacen que las dependencias secuenciales sean
riesgosas, cada grupo deberia poder trabajar en paralelo usando entradas de
ejemplo preparadas.

La idea es darle a cada grupo una familia tecnologica y un mini proyecto
realista. Los proyectos no deberian depender entre si, pero todos deberian
conectarse conceptualmente con el mismo tema del curso: mover, almacenar,
procesar y servir datos.

## Tecnologias Usadas en Este Laboratorio

Este laboratorio toca las siguientes tecnologias y conceptos de ingenieria de
datos:

| Tecnologia | Donde aparece en el laboratorio | Concepto principal |
| --- | --- | --- |
| Docker Compose | Cada carpeta de servicio | Orquestacion local de infraestructura |
| MySQL | `db/` | Base de datos relacional operacional |
| MinIO / almacenamiento compatible con S3 | `min_io/` | Object storage y diseno de data lake |
| PySpark / Apache Spark | `etl/` | Procesamiento batch distribuido |
| Parquet | Salida del ETL en MinIO | Almacenamiento columnar analitico |
| PostgreSQL + pgvector | `vector_db/` | Base de datos vectorial y busqueda por similitud |
| FastAPI | `recommendation_api/`, `event_producer/` | APIs HTTP para servicios de datos |
| Redpanda / protocolo Kafka | `streaming_broker/` | Streaming de eventos y topics |
| Consumidores/productores Python | `event_producer/`, `stream_processor/` | Produccion y procesamiento de streams |
| ML embeddings | `ml-artifacts/`, `vector_db/` | Representaciones numericas aprendidas |

Hadoop no es necesario para ejecutar este laboratorio, pero es una tecnologia
util para asignar porque introduce HDFS y MapReduce, que son parte de la base
historica del procesamiento distribuido de datos.





## Rubrica de Evaluacion Sugerida

| Categoria | Puntos |
| --- | ---: |
| El diagrama de diseno del sistema es claro y realista | 19 |
| El prototipo local corre correctamente | 24 |
| El flujo de datos se explica correctamente | 19 |
| La salida final es facil de inspeccionar | 14 |
| El README y la presentacion son claros | 14 |
| El equipo puede explicar tradeoffs y limitaciones | 4 |

## Sesion de Integracion

Al final, cada grupo deberia presentar como su tecnologia se conecta con el
ecosistema mas amplio de ingenieria de datos:

- Hadoop explica almacenamiento distribuido y MapReduce.
- Spark explica procesamiento batch distribuido moderno.
- Kafka explica streaming orientado a eventos.
- Las bases de datos vectoriales explican busqueda por similitud y recomendaciones.
- Los data lakes enriquecidos con IA explican como servicios externos de IA
  pueden transformar datos crudos en productos de datos estructurados servidos
  mediante APIs.

Luego la clase puede comparar las cinco arquitecturas y discutir que tecnologia
encaja mejor con cada problema.

## Checklist de Preparacion Para el Profesor

Antes de asignar los proyectos:

0. Dar a cada grupo un dataset inicial pequeno.
1. Dar a cada grupo un formato de salida objetivo.
2. Pedir a cada grupo que cree un diagrama de diseno del sistema antes de programar.
3. Pedir a cada grupo que incluya un `README.md` con comandos de ejecucion.
4. Reservar tiempo de clase para una revision corta de arquitectura antes de la demo final.
