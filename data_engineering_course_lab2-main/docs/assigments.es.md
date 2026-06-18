## Cinco Proyectos Grupales

Cada grupo deberia producir:

- Un diagrama de diseno del sistema.
- Un prototipo local pequeno o simulacion.
- Un README que explique como ejecutarlo.
- Una presentacion corta explicando los tradeoffs de la tecnologia.
- Un resultado final: dataset, reporte, respuesta de API, dashboard o salida de consola.

### Grupo 1: Proyecto Hadoop

Enfoque tecnologico: Hadoop, HDFS, MapReduce.

Idea del proyecto: conteo de votos de elecciones locales en diferentes ciudades.

Escenario:

Diferentes ciudades envian archivos de votos durante el dia de elecciones. Cada
ciudad produce un archivo CSV con registros de votacion. El objetivo es
almacenar todos los archivos de ciudades en HDFS y contar votos por candidato,
ciudad y region usando MapReduce.

Entrada de ejemplo:

```text
vote_id,city,region,candidate,party,event_time
1,Lima,Lima,Ana Torres,Blue,2026-05-29T08:01:00Z
2,Arequipa,Arequipa,Carlos Ruiz,Green,2026-05-29T08:02:00Z
3,Cusco,Cusco,Ana Torres,Blue,2026-05-29T08:03:00Z
```

Tareas requeridas:

- Disenar una arquitectura local de Hadoop con HDFS y un job MapReduce.
- Simular al menos 3 ciudades produciendo archivos de votos.
- Cargar los archivos en HDFS.
- Contar votos totales por candidato.
- Contar votos por ciudad y candidato.
- Producir un archivo final de resultados con el ganador.

Entregable esperado:

```text
candidate,total_votes,percentage
Ana Torres,15234,52.4
Carlos Ruiz,13841,47.6
```

Preguntas de discusion:

- ¿Por que HDFS divide los archivos en bloques?
- ¿De que es responsable el mapper?
- ¿De que es responsable el reducer?
- ¿Cuando seria Hadoop una mejor opcion que un script normal de Python?

### Grupo 2: Proyecto Spark

Enfoque tecnologico: Apache Spark, PySpark, Parquet.

Idea del proyecto: analitica de transporte urbano.

Escenario:

Un departamento de transporte recibe registros de viajes de taxi o bus. El equipo
necesita procesar los datos y generar salidas analiticas para planificadores.

Entrada de ejemplo:

```text
trip_id,city,route_id,start_time,end_time,passengers,distance_km
1,Lima,R101,2026-05-29T07:30:00Z,2026-05-29T08:05:00Z,32,11.4
```

Tareas requeridas:

- Construir un job PySpark que lea datos de viajes en CSV.
- Limpiar registros invalidos, como distancia negativa o ruta faltante.
- Calcular pasajeros totales por ruta.
- Calcular duracion promedio de viaje por ciudad.
- Escribir la salida como Parquet particionado por ciudad.
- Explicar como las particiones de Spark distribuyen el trabajo entre executors.

Entregable esperado:

```text
city,route_id,total_passengers,avg_duration_minutes
Lima,R101,18420,36.5
```

Preguntas de discusion:

- ¿Cual es la diferencia entre un Spark driver y Spark workers?
- ¿Por que Parquet es util para analitica?
- ¿En que se diferencia Spark de Hadoop MapReduce?

### Grupo 3: Proyecto Kafka

Enfoque tecnologico: conceptos de Kafka usando Redpanda, producers, consumers y topics.

Idea del proyecto: stream de actividad ecommerce en tiempo real.

Escenario:

Una tienda online emite eventos cuando los usuarios ven productos, agregan
productos al carrito o completan una compra. El equipo necesita transmitir esos
eventos y calcular metricas de actividad en vivo.

Evento de ejemplo:

```json
{
  "event_id": "evt-001",
  "customer_id": 276,
  "event_type": "product_view",
  "product_code": "S18_3029",
  "event_time": "2026-05-29T17:58:28Z"
}
```

Tareas requeridas:

- Crear un topic compatible con Kafka.
- Construir un producer que emita eventos ecommerce aleatorios.
- Construir un consumer que lea eventos continuamente.
- Contar eventos por tipo cada minuto.
- Detectar los 5 productos mas vistos.
- Explicar por que un broker es util entre la aplicacion y el procesador.

Entregable esperado:

```text
Window: 17:58-17:59
product_view: 320
add_to_cart: 44
purchase: 12
top_product: S18_3029
```

Preguntas de discusion:

- ¿Que es un topic?
- ¿Cual es la diferencia entre producer y consumer?
- ¿Por que los sistemas de streaming usan offsets?
- ¿Que pasa si el consumer esta fuera de linea durante unos minutos?

### Grupo 4: Proyecto de Base de Datos Vectorial

Enfoque tecnologico: PostgreSQL, pgvector, embeddings, busqueda por similitud.

Idea del proyecto: busqueda semantica de productos.

Escenario:

Un equipo ecommerce quiere que los usuarios busquen productos por significado,
no solo por palabras clave exactas. Las descripciones de productos se convierten
en embeddings y se almacenan en una base de datos vectorial.

Entrada de ejemplo:

```text
product_id,name,description
S18_3029,1999 Yamaha Speed Boat,High-speed collectible boat model
S10_4698,Harley-Davidson Drag Bike,Collectible motorcycle model
```

Tareas requeridas:

- Crear una tabla PostgreSQL con una columna vectorial.
- Cargar embeddings de productos desde un archivo CSV.
- Consultar productos similares para un producto seleccionado.
- Devolver los 5 productos mas cercanos con distance y score.
- Explicar como la distancia vectorial se usa para recomendaciones.

Entregable esperado:

```json
[
  {"id": "S10_4698", "name": "Harley-Davidson Drag Bike", "score": 0.752},
  {"id": "S18_3685", "name": "Porsche Type 356 Roadster", "score": 0.728}
]
```

Preguntas de discusion:

- ¿Que es un embedding?
- ¿Por que items similares aparecen cerca en el espacio vectorial?
- ¿Que significa distance?
- ¿Por que una base de datos vectorial es mas rapida que comparar manualmente todos los items?

### Grupo 5: Proyecto de Data Lake Enriquecido con IA y API

Enfoque tecnologico: MinIO, object storage, FastAPI, API externa de IA, contratos de datos.

Idea del proyecto: inteligencia de reviews de productos usando una API de enriquecimiento con IA.

Escenario:

Una empresa ecommerce recibe reviews de productos de sus clientes. El equipo
almacena las reviews crudas en MinIO, envia cada review a una API de IA como
Gemini para extraer informacion estructurada, almacena el resultado enriquecido
de vuelta en MinIO y expone los datos enriquecidos mediante FastAPI.

La idea clave de ingenieria de datos es que la API de IA enriquece el pipeline,
pero no reemplaza el pipeline. El servicio FastAPI deberia leer datos ya
procesados desde MinIO en lugar de llamar a la API de IA por cada solicitud de
usuario.

Entrada de ejemplo:

```json
{
  "review_id": "rev-001",
  "product_code": "S18_3029",
  "customer_id": 276,
  "rating": 4,
  "review_text": "The boat model looks beautiful, but the packaging arrived damaged.",
  "event_time": "2026-05-29T10:15:00Z"
}
```

Salida enriquecida de ejemplo:

```json
{
  "review_id": "rev-001",
  "product_code": "S18_3029",
  "sentiment": "mixed",
  "main_topic": "packaging",
  "summary": "Customer liked the model but complained about damaged packaging.",
  "urgency": "medium"
}
```

Tareas requeridas:

- Disenar una estructura de buckets en MinIO para reviews crudas y reviews enriquecidas.
- Generar o recolectar al menos 50 reviews de productos de ejemplo.
- Escribir archivos JSON de reviews crudas en MinIO.
- Crear un job de enriquecimiento que llame a una API de IA como Gemini.
- Extraer campos estructurados como sentiment, topic, summary y urgency.
- Almacenar registros JSON enriquecidos de vuelta en MinIO.
- Construir un servicio FastAPI que lea registros enriquecidos y exponga endpoints de consulta.
- Definir claramente el esquema crudo, el esquema enriquecido y los contratos de respuesta de API.
- Explicar como las API keys deben manejarse de forma segura usando variables de entorno.

Endpoints de ejemplo:

```text
GET /health
GET /reviews/product/{product_code}
GET /reviews/sentiment/{sentiment}
GET /reviews/topics
GET /reviews/summary/{review_id}
```

Entregable esperado:

```json
{
  "product_code": "S18_3029",
  "review_count": 24,
  "sentiment_breakdown": {
    "positive": 15,
    "mixed": 6,
    "negative": 3
  },
  "top_topics": ["packaging", "quality", "shipping"]
}
```

Preguntas de discusion:

- ¿Por que las reviews crudas deberian almacenarse antes del enriquecimiento con IA?
- ¿Por que la salida enriquecida por IA deberia almacenarse en vez de generarse en cada solicitud de API?
- ¿Que puede salir mal cuando una API externa de IA no esta disponible o responde lento?
- ¿Como se deben proteger las API keys?
- ¿Que campos deberian incluirse para que la salida de IA sea auditable?
- ¿Como manejarian respuestas de IA malas o de baja confianza?

