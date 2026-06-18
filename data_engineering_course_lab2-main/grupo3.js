const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageBreak, VerticalAlign, Header, Footer, PageNumber
} = require('docx');
const fs = require('fs');

// ── Colores ──────────────────────────────────────────────────────────────────
const BLUE_NAVY     = "0F2C59"; // Encabezados principales, acentos fuertes
const BLUE_STEEL    = "2E75B6"; // Subtítulos, bordes de llamadas
const BLUE_LIGHT    = "D5E8F0"; // Fondo claro auxiliar
const BLUE_HDR      = "1F4E79"; // Cabecera de tablas
const BLUE_CALLOUT  = "F4F7F9"; // Fondo de cajas de llamadas
const GRAY_ROW      = "F2F6FA"; // Alternancia en tablas
const GRAY_BG       = "F8F9FA"; // Fondo de bloques de código
const GRAY_BORDER   = "CCCCCC"; // Bordes de tablas y cajas
const WHITE         = "FFFFFF"; // Blanco
const TEXT_DARK     = "222222"; // Gris oscuro para texto general (más suave)

const border = { style: BorderStyle.SINGLE, size: 4, color: GRAY_BORDER };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// ── Helpers de Formato ────────────────────────────────────────────────────────
function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 180 },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 12, color: BLUE_NAVY, space: 6 } // Línea inferior de acento
    },
    children: [new TextRun({ text, font: "Arial", size: 28, bold: true, color: BLUE_NAVY })],
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 260, after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: BLUE_STEEL })],
  });
}

function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 180, after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 18, bold: true, color: BLUE_NAVY })],
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120, line: 276 }, // Spacing 1.15x
    children: [new TextRun({ text, font: "Arial", size: 21, color: TEXT_DARK, ...opts })],
  });
}

function paraRuns(runs) {
  return new Paragraph({
    spacing: { after: 120, line: 276 },
    children: runs.map(r =>
      new TextRun({ font: "Arial", size: 21, color: TEXT_DARK, ...r })
    ),
  });
}

function spacer(pts = 160) {
  return new Paragraph({ spacing: { after: pts }, children: [] });
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { after: 80, line: 240 },
    children: [new TextRun({ text, font: "Arial", size: 21, color: TEXT_DARK })],
  });
}

// Bloque de Código estilo "Tarjeta"
function codeBlockBox(lines) {
  const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: "DDDDDD" };
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder },
            shading: { fill: GRAY_BG, type: ShadingType.CLEAR },
            margins: { top: 140, bottom: 140, left: 180, right: 180 },
            children: lines.map(line =>
              new Paragraph({
                spacing: { before: 0, after: 0, line: 200 },
                children: [new TextRun({ text: line, font: "Courier New", size: 17, color: "2E2E2E" })]
              })
            )
          })
        ]
      })
    ]
  });
}

// Caja de Información / Callout
function calloutBox(title, paragraphLines) {
  const leftBorder = { style: BorderStyle.SINGLE, size: 24, color: BLUE_STEEL }; // Borde grueso lateral
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: { left: leftBorder, top: noBorder, right: noBorder, bottom: noBorder },
            shading: { fill: BLUE_CALLOUT, type: ShadingType.CLEAR },
            margins: { top: 160, bottom: 160, left: 200, right: 200 },
            children: [
              new Paragraph({
                spacing: { after: 80 },
                children: [new TextRun({ text: title, font: "Arial", size: 19, bold: true, color: BLUE_NAVY })]
              }),
              ...paragraphLines.map((line, idx) => new Paragraph({
                spacing: { after: idx === paragraphLines.length - 1 ? 0 : 60, line: 240 },
                children: [new TextRun({ text: line, font: "Arial", size: 19, color: "333333", italic: true })]
              }))
            ]
          })
        ]
      })
    ]
  });
}

// Filas de Tablas Rediseñadas
function tableHeaderRow(cells) {
  return new TableRow({
    tableHeader: true,
    children: cells.map(({ text, width }) =>
      new TableCell({
        borders,
        width: { size: width, type: WidthType.DXA },
        shading: { fill: BLUE_HDR, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text, font: "Arial", size: 20, bold: true, color: WHITE })],
        })],
      })
    ),
  });
}

function tableDataRow(cells, even) {
  return new TableRow({
    children: cells.map(({ text, width }) =>
      new TableCell({
        borders,
        width: { size: width, type: WidthType.DXA },
        shading: { fill: even ? GRAY_ROW : WHITE, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text, font: "Arial", size: 19, color: TEXT_DARK })],
        })],
      })
    ),
  });
}

// ── Construcción de Tablas ────────────────────────────────────────────────────
function componentesTable() {
  const cols = [2000, 2800, 2500, 2060];
  const headers = ["Componente", "Tecnología", "Rol", "Puerto"];
  const rows = [
    ["Broker", "Redpanda v24 (Docker)", "Reemplaza Amazon Kinesis / MSK", "19092 (ext)"],
    ["Topic", "user-activity (3 particiones)", "Canal de eventos ecommerce", "—"],
    ["Producer", "Python + confluent-kafka", "Genera ~5 eventos/segundo", "—"],
    ["Consumer", "Python + confluent-kafka", "Lee y agrega métricas y las exporta", "—"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: cols,
    rows: [
      tableHeaderRow(headers.map((text, i) => ({ text, width: cols[i] }))),
      ...rows.map((r, ri) => tableDataRow(r.map((text, i) => ({ text, width: cols[i] })), ri % 2 === 0)),
    ],
  });
}

function tradeoffsTable() {
  const cols = [2600, 3380, 3380];
  const headers = ["Característica", "Kafka / Redpanda", "HTTP directo / cola simple"];
  const rows = [
    ["Durabilidad", "Mensajes en disco; sobreviven caídas", "Pérdida si el receptor cae"],
    ["Desacoplamiento", "Producer y consumer independientes", "Acoplamiento temporal"],
    ["Escalabilidad", "Particiones permiten múltiples consumers", "Cuello de botella en un servidor"],
    ["Replay", "Resetear offset → reprocesar histórico", "Imposible sin BD adicional"],
    ["Backpressure", "El broker absorbe picos de tráfico", "El producer puede saturar al receptor"],
    ["Múltiples consumers", "N consumers independientes del mismo topic", "Fan-out manual"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: cols,
    rows: [
      tableHeaderRow(headers.map((text, i) => ({ text, width: cols[i] }))),
      ...rows.map((r, ri) => tableDataRow(r.map((text, i) => ({ text, width: cols[i] })), ri % 2 === 0)),
    ],
  });
}

function redpandaVsKafkaTable() {
  const cols = [2400, 3480, 3480];
  const headers = ["Aspecto", "Redpanda", "Apache Kafka"];
  const rows = [
    ["Dependencias", "Binario único, sin JVM, sin ZooKeeper", "Requiere JVM + ZooKeeper / KRaft"],
    ["Latencia", "Más baja (C++, thread-per-core)", "Mayor overhead de JVM"],
    ["API", "100% compatible con Kafka", "—"],
    ["Dev local", "docker run con 512 MB RAM", "Más pesado para laptops"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: cols,
    rows: [
      tableHeaderRow(headers.map((text, i) => ({ text, width: cols[i] }))),
      ...rows.map((r, ri) => tableDataRow(r.map((text, i) => ({ text, width: cols[i] })), ri % 2 === 0)),
    ],
  });
}

function requerimientosTable() {
  const cols = [3200, 3200, 2960];
  const headers = ["Requerimiento Grupo 3", "Componente del lab", "Estado"];
  const rows = [
    ["Topic compatible con Kafka", "streaming_broker/docker-compose.yml → user-activity", "✅ Ya existe"],
    ["Producer que emita eventos ecommerce", "event_producer/ecommerce_producer.py", "✅ Creado"],
    ["Consumer que lea eventos continuamente", "stream_processor/ecommerce_metrics_consumer.py", "✅ Creado"],
    ["Contar eventos por tipo cada minuto", "ecommerce_metrics_consumer.py — MetricsWindow", "✅ Implementado"],
    ["Top 5 productos más vistos", "ecommerce_metrics_consumer.py — Counter", "✅ Implementado"],
    ["Resultados guardados (Dataset físico)", "docs/resultados_metricas.csv", "✅ Implementado"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: cols,
    rows: [
      tableHeaderRow(headers.map((text, i) => ({ text, width: cols[i] }))),
      ...rows.map((r, ri) => tableDataRow(r.map((text, i) => ({ text, width: cols[i] })), ri % 2 === 0)),
    ],
  });
}

function csvSchemaTable() {
  const cols = [2400, 1800, 5160];
  const headers = ["Columna CSV", "Tipo", "Descripción"];
  const rows = [
    ["window_start", "DateTime", "Fecha y hora del inicio de la ventana de agregación (formato YYYY-MM-DD HH:MM:SS)"],
    ["window_end", "DateTime", "Fecha y hora del fin de la ventana de agregación (formato YYYY-MM-DD HH:MM:SS)"],
    ["total_events", "Integer", "Número total de eventos procesados en la ventana"],
    ["product_view", "Integer", "Conteo total de vistas de productos (product_view) en la ventana"],
    ["add_to_cart", "Integer", "Conteo total de adiciones al carrito (add_to_cart) en la ventana"],
    ["purchase", "Integer", "Conteo total de transacciones de compra (purchase) en la ventana"],
    ["top_product", "String (SKU)", "Código del producto con la mayor cantidad de vistas en la ventana"],
    ["top_5_products", "String", "Listado de los 5 productos más vistos con sus marcas de conteo (código(vistas); ...)"]
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: cols,
    rows: [
      tableHeaderRow(headers.map((text, i) => ({ text, width: cols[i] }))),
      ...rows.map((r, ri) => tableDataRow(r.map((text, i) => ({ text, width: cols[i] })), ri % 2 === 0)),
    ],
  });
}

// ── Documento Principal ───────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 21, color: TEXT_DARK } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: BLUE_NAVY },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: BLUE_STEEL },
        paragraph: { spacing: { before: 260, after: 120 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
      titlePage: true, // Habilita que la portada no tenga encabezado/pie de página
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [
              new TextRun({ text: "Proyecto Kafka con Redpanda — Grupo 3", font: "Arial", size: 16, color: "888888" })
            ]
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [
              new TextRun({ text: "Entregable Técnico | Pág. ", font: "Arial", size: 16, color: "888888" }),
              new TextRun({
                children: [PageNumber.CURRENT],
                font: "Arial",
                size: 16,
                color: "888888"
              })
            ]
          })
        ]
      })
    },
    children: [

      // ── PORTADA PREMIUM ────────────────────────────────────────────────────
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 1800, after: 120 },
        children: [new TextRun({ text: "INFORME TÉCNICO", font: "Arial", size: 40, bold: true, color: BLUE_NAVY })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [new TextRun({ text: "PROYECTO KAFKA CON REDPANDA", font: "Arial", size: 32, bold: true, color: BLUE_STEEL })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 600 },
        children: [new TextRun({ text: "Simulación de Procesamiento de Stream de Eventos de E-commerce en Tiempo Real", font: "Arial", size: 22, italic: true, color: "555555" })],
      }),

      // Separador visual: Barra Navy Sólida
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders: noBorders,
                shading: { fill: BLUE_NAVY, type: ShadingType.CLEAR },
                margins: { top: 40, bottom: 40 },
                children: [new Paragraph({ children: [] })]
              })
            ]
          })
        ]
      }),
      spacer(1800),

      // Datos de Entrega Estilizados en Caja Callout
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders: {
                  left: { style: BorderStyle.SINGLE, size: 24, color: BLUE_STEEL },
                  top: noBorder, right: noBorder, bottom: noBorder
                },
                shading: { fill: BLUE_CALLOUT, type: ShadingType.CLEAR },
                margins: { top: 200, bottom: 200, left: 240, right: 240 },
                children: [
                  new Paragraph({
                    spacing: { after: 120 },
                    children: [new TextRun({ text: "DATOS DEL ENTREGABLE", font: "Arial", size: 18, bold: true, color: BLUE_NAVY })]
                  }),
                  new Paragraph({
                    spacing: { after: 60 },
                    children: [
                      new TextRun({ text: "Curso: ", font: "Arial", size: 19, bold: true, color: TEXT_DARK }),
                      new TextRun({ text: "Ingeniería de Datos y Analítica Digital (Lab 2)", font: "Arial", size: 19, color: TEXT_DARK })
                    ]
                  }),
                  new Paragraph({
                    spacing: { after: 60 },
                    children: [
                      new TextRun({ text: "Caso: ", font: "Arial", size: 19, bold: true, color: TEXT_DARK }),
                      new TextRun({ text: "Stream de Actividad y Cálculo de Métricas en Vivo", font: "Arial", size: 19, color: TEXT_DARK })
                    ]
                  }),
                  new Paragraph({
                    spacing: { after: 60 },
                    children: [
                      new TextRun({ text: "Integrantes: ", font: "Arial", size: 19, bold: true, color: TEXT_DARK }),
                      new TextRun({ text: "Grupo 3 (Ingeniería de Datos)", font: "Arial", size: 19, color: TEXT_DARK })
                    ]
                  }),
                  new Paragraph({
                    spacing: { after: 0 },
                    children: [
                      new TextRun({ text: "Fecha: ", font: "Arial", size: 19, bold: true, color: TEXT_DARK }),
                      new TextRun({ text: "Junio de 2026", font: "Arial", size: 19, color: TEXT_DARK })
                    ]
                  })
                ]
              })
            ]
          })
        ]
      }),
      spacer(1000),

      // ── INDICE / GUIA TEMÁTICA ──────────────────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading2("Guía Temática del Reporte"),
      spacer(120),
      para("Este reporte técnico detalla la arquitectura, el código de simulación y los resultados obtenidos en el laboratorio. Está estructurado en las siguientes secciones claves:"),
      bullet("Sección 1: Introducción y Resumen Ejecutivo — Contextualización del negocio y arquitecturas reactivas."),
      bullet("Sección 2: Diseño del Sistema y Flujo de Datos — Esquema de mensajes y flujo del stream."),
      bullet("Sección 3: Prototipo Local y Detalle de Implementación — Stack tecnológico y código fuente."),
      bullet("Sección 4: Guía de Ejecución y Pruebas — Comandos para levantar e iniciar la simulación local."),
      bullet("Sección 5: Análisis Técnico de Tradeoffs y Tecnologías — Comparativa de herramientas de streaming."),
      bullet("Sección 6: Resultados del Prototipo Local — Registros de consola del agregador y formato del dataset CSV generado."),
      bullet("Sección 7: Cuestionario de Discusión Técnica — Respuestas conceptuales a preguntas teóricas del laboratorio."),
      spacer(480),

      // Mapa de requerimientos cubiertos
      heading2("Mapa de Cumplimiento de Requerimientos"),
      spacer(120),
      requerimientosTable(),
      spacer(480),

      // ── SECCIÓN 1: INTRODUCCIÓN ──────────────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading1("1. Introducción y Resumen Ejecutivo"),
      spacer(120),
      para("Las plataformas modernas de comercio electrónico operan en entornos altamente de interacción instantánea. Los sistemas tradicionales de procesamiento de datos por lotes (batch processing), que recopilan información durante horas para procesarla en la noche, introducen latencias inaceptables para las demandas de negocio actuales. Para resolver este desafío, la arquitectura de datos del proyecto adopta un enfoque orientado a eventos (Event-Driven Architecture) con procesamiento de streams en tiempo real."),
      para("Este informe técnico presenta el diseño y la implementación de un prototipo local completo desarrollado por el Grupo 3. La solución simula la actividad web de los clientes y procesa los eventos sobre la marcha para calcular métricas de actividad en vivo. Mediante el uso de Redpanda como un broker compatible con la API de Kafka, y de scripts optimizados en Python con la biblioteca confluent-kafka, hemos construido un canal resistente y desacoplado capaz de reportar conteos y tendencias de productos minuto a minuto de manera ininterrumpida. Esto permite habilitar capacidades reactivas inmediatas, como alertas de inventario crítico, monitoreo de la tasa de conversión y analítica en caliente de comportamiento de navegación."),
      spacer(240),

      // ── SECCIÓN 2: DISEÑO DEL SISTEMA ──────────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading1("2. Diseño del Sistema y Flujo de Datos"),
      spacer(120),
      para("El sistema sigue una topología de streaming unidireccional desacoplada, donde el flujo de información transita por tres etapas diferenciadas: Producción, Intermediación (Broker) y Consumo/Procesamiento. A continuación se esquematiza el pipeline de datos del prototipo:"),
      spacer(120),

      // Diagrama de arquitectura
      codeBlockBox([
        "┌─────────────────────┐     JSON event      ┌───────────────────────┐",
        "│  Tienda Online       │  ────────────────►  │  Topic: user-activity  │",
        "│  (simulada)          │  customer_id         │  Redpanda — 3 partici. │",
        "│  ecommerce_          │  event_type          │  broker local          │",
        "│  producer.py         │  product_code        │  localhost:19092       │",
        "│  ~5 eventos/seg      │  event_time          │                        │",
        "└─────────────────────┘                      └──────────┬─────────────┘",
        "                                                         │ offset por partición",
        "                                                         ▼",
        "                                             ┌───────────────────────┐",
        "                                             │  ecommerce_metrics_    │",
        "                                             │  consumer.py           │",
        "                                             │  Ventana de 1 minuto   │",
        "                                             │  Counter por tipo      │",
        "                                             │  Top 5 productos       │",
        "                                             └──────────┬─────────────┘",
        "                                                         │",
        "                                                         ▼",
        "                                             Window: HH:MM-HH:MM",
        "                                             product_view: N",
        "                                             add_to_cart:  N",
        "                                             purchase:     N",
        "                                             top_product:  SXX_XXXX",
      ]),
      spacer(240),

      heading2("Esquema del Evento de Streaming"),
      para("Para cumplir con los requerimientos específicos del Grupo 3, se ha modelado un esquema JSON simplificado e informativo que representa fielmente una transacción web. Cada mensaje emitido al topic 'user-activity' contiene los siguientes campos obligatorios:"),
      bullet("event_id: Identificador único universal (UUID) para cada interacción. Es fundamental para la trazabilidad y la deduplicación de eventos en etapas posteriores."),
      bullet("customer_id: Identificador numérico del cliente (del 100 al 999). Permite realizar análisis de afinidad y segmentación del recorrido de compra."),
      bullet("event_type: Tipo de evento. Toma uno de tres valores: 'product_view' (vista de producto), 'add_to_cart' (adición al carrito) o 'purchase' (compra)."),
      bullet("product_code: SKU de producto. Representado por códigos del catálogo histórico (ej. S18_3029)."),
      bullet("event_time: Timestamp en formato estándar ISO 8601 en zona horaria UTC, que registra la marca de tiempo exacta del cliente."),
      spacer(120),

      para("A continuación se presenta un ejemplo real del payload JSON del evento:"),
      codeBlockBox([
        "{",
        "  \"event_id\": \"evt-e0c242a3-89bd-49a7-ba0e-36c1e550974f\",",
        "  \"customer_id\": 276,",
        "  \"event_type\": \"product_view\",",
        "  \"product_code\": \"S18_3029\",",
        "  \"event_time\": \"2026-06-15T01:49:36Z\"",
        "}"
      ]),
      spacer(480),

      // ── SECCIÓN 3: PROTOTIPO LOCAL ─────────────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading1("3. Prototipo Local y Detalle de Implementación"),
      spacer(120),
      para("El prototipo se compone de scripts estructurados que interactúan directamente con un entorno local en contenedores. El stack se compone de la siguiente forma:"),
      spacer(120),
      componentesTable(),
      spacer(240),

      heading2("Arquitectura de Archivos del Entregable"),
      para("El código fuente desarrollado para el entregable del Grupo 3 está organizado de la siguiente manera dentro del repositorio del laboratorio:"),
      codeBlockBox([
        "data_engineering_course_lab2-main/",
        "├── streaming_broker/",
        "│   └── docker-compose.yml             ← Orquestación de Redpanda",
        "├── event_producer/",
        "│   └── ecommerce_producer.py          ← Productor de eventos en Python (Grupo 3)",
        "├── stream_processor/",
        "│   └── ecommerce_metrics_consumer.py  ← Agregador de métricas y exportador de CSV (Grupo 3)",
        "├── run_grupo3_demo.py                 ← Orquestador y ejecutor de demo",
        "└── docs/",
        "    ├── Grupo3_Kafka_Proyecto.docx     ← Entregable Técnico Oficial generado",
        "    ├── resultados_metricas.csv        ← Dataset físico consolidado de métricas (CSV)",
        "    └── grupo3_respuestas.md           ← Respuestas de discusión académica"
      ]),
      spacer(240),

      heading2("Detalle del Producer (ecommerce_producer.py)"),
      para("El productor simula el tráfico continuo de un e-commerce real. Genera eventos asíncronos y los publica en el topic 'user-activity' a una tasa de aproximadamente 5 mensajes por segundo. Para lograr realismo, implementa una ponderación probabilística en los eventos: el 70% corresponde a vistas de productos (product_view), el 20% a adiciones al carrito (add_to_cart) y el 10% a transacciones de compra (purchase)."),
      para("El código utiliza el cliente de alto rendimiento confluent_kafka.Producer y registra una función callback llamada 'delivery_report'. Esta función actúa de forma no bloqueante para recibir la confirmación de entrega (ack) del broker Redpanda, notificando el offset y la partición asignada o reportando errores si el envío falla, garantizando que el bucle de eventos no se congele ante problemas de red."),
      spacer(240),

      heading2("Detalle del Consumer (ecommerce_metrics_consumer.py) y Persistencia"),
      para("El procesador de streams consume los eventos de las 3 particiones del topic 'user-activity'. Su objetivo es agregar métricas en ventanas de tiempo de un minuto sin solapamiento (Tumbling Windows). Utiliza estructuras en memoria (collections.Counter) para llevar la cuenta de la actividad de los productos. Además de imprimir en consola el informe, el consumer escribe de forma automática cada ventana terminada en el archivo docs/resultados_metricas.csv, permitiendo la creación de un dataset histórico permanente de las ejecuciones."),
      spacer(480),

      // ── SECCIÓN 4: GUÍA DE EJECUCIÓN ───────────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading1("4. Guía de Ejecución y Pruebas"),
      spacer(120),
      para("Para validar y reproducir el prototipo en cualquier máquina local (Windows o macOS) con Docker Desktop instalado, siga las siguientes instrucciones paso a paso:"),
      spacer(120),

      heading2("Prerrequisitos del Entorno"),
      bullet("Docker Desktop en ejecución."),
      bullet("Python 3.10 o superior instalado en el host local."),
      bullet("Instalación de las dependencias requeridas ejecutando:"),
      spacer(80),
      codeBlockBox(["pip install confluent-kafka"]),
      spacer(200),

      heading2("Paso 1 — Inicializar la Infraestructura del Broker"),
      para("Abra una terminal y navegue al directorio del broker para iniciar Redpanda en segundo plano:"),
      codeBlockBox([
        "cd streaming_broker",
        "docker-compose up -d",
        "",
        "# Validar que el topic 'user-activity' con 3 particiones fue creado correctamente",
        "docker exec lab2-redpanda rpk topic list",
        "",
        "# Salida esperada:",
        "# NAME           PARTITIONS  REPLICAS",
        "# user-activity  3           1"
      ]),
      spacer(200),

      heading2("Paso 2 — Ejecutar Simulación Automática (Modo Demo)"),
      para("Desde la raíz del proyecto, ejecute el script unificado que inicializa tanto el productor de eventos como el consumidor de métricas en paralelo durante 130 segundos (suficiente para capturar al menos dos ventanas completas de un minuto):"),
      codeBlockBox([
        "python run_grupo3_demo.py"
      ]),
      spacer(200),

      heading2("Paso 3 — Ejecución Manual Detallada (Terminales Separadas)"),
      para("Si desea inspeccionar el comportamiento de cada componente de manera independiente, ejecútelos en terminales separadas de la siguiente forma:"),
      para("Terminal 1 — Generador de Tráfico (Producer):"),
      codeBlockBox([
        "cd event_producer",
        "python ecommerce_producer.py"
      ]),
      spacer(120),
      para("Terminal 2 — Procesador de Métricas (Consumer con salida de consola y CSV):"),
      codeBlockBox([
        "cd stream_processor",
        "python ecommerce_metrics_consumer.py"
      ]),
      spacer(200),

      heading2("Paso 4 — Limpieza del Entorno"),
      para("Una vez finalizadas las pruebas, apague los contenedores de Docker para liberar memoria ram en su sistema:"),
      codeBlockBox([
        "cd streaming_broker",
        "docker-compose down"
      ]),
      spacer(480),

      // ── SECCIÓN 5: ANÁLISIS DE TRADEOFFS ───────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading1("5. Análisis Técnico de Tradeoffs y Tecnologías"),
      spacer(120),
      para("La selección de arquitecturas de mensajería basadas en logs distribuidos en lugar de arquitecturas HTTP directas responde a necesidades claras de escalabilidad, durabilidad y tolerancia a fallos. La siguiente tabla resume los tradeoffs evaluados para el proyecto:"),
      spacer(120),
      tradeoffsTable(),
      spacer(240),

      heading2("Redpanda frente a Apache Kafka Tradicional"),
      para("Redpanda es una recreación moderna del motor de almacenamiento de Apache Kafka, escrito en C++ y diseñado específicamente para infraestructuras de alto rendimiento. Las diferencias técnicas clave evaluadas son:"),
      spacer(120),
      redpandaVsKafkaTable(),
      spacer(240),

      heading2("Consideraciones de Diseño: Cuándo NO usar Redpanda/Kafka"),
      para("A pesar de sus ventajas, los sistemas de streaming introducen complejidad y no son una bala de plata. Se recomienda evitar su uso en:"),
      bullet("Bajo volumen de datos: si el sistema procesa menos de 100 peticiones por minuto, una cola simple como SQS o una base de datos relacional tradicional es suficiente y más fácil de mantener."),
      bullet("Requerimientos estrictos de transaccionalidad ACID clásica: aunque Kafka admite transacciones, las bases de datos SQL tradicionales son más adecuadas para flujos de caja o contabilidad dura."),
      bullet("Requisitos de latencia por debajo del milisegundo: para arquitecturas que requieran latencias ultrabajas de microsegundos, protocolos como gRPC directo o colas in-memory sin persistencia a disco (como ZeroMQ) son opciones óptimas."),
      spacer(480),

      // ── SECCIÓN 6: RESULTADOS ──────────────────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading1("6. Resultados del Prototipo Local"),
      spacer(120),
      para("El script orquestador 'run_grupo3_demo.py' fue ejecutado exitosamente en el entorno de desarrollo de Windows. A continuación, se muestra el registro real de la consola capturado durante la simulación activa:"),
      spacer(120),

      codeBlockBox([
        "==================================================",
        "Window: 02:52-02:53",
        "Total eventos en ventana: 312",
        "",
        "  product_view: 206",
        "  add_to_cart: 74",
        "  purchase: 32",
        "",
        "top_product: S24_2360",
        "",
        "  Top 5 productos (product_view):",
        "    1. S24_2360 — 9 vistas",
        "    2. S18_4027 — 7 vistas",
        "    3. S18_2870 — 5 vistas",
        "    4. S18_2319 — 5 vistas",
        "    5. S24_1578 — 5 vistas",
        "==================================================",
        "",
        "==================================================",
        "Window: 02:53-02:54",
        "Total eventos en ventana: 299",
        "",
        "  product_view: 210",
        "  add_to_cart: 59",
        "  purchase: 30",
        "",
        "top_product: S18_3482",
        "",
        "  Top 5 productos (product_view):",
        "    1. S18_3482 — 8 vistas",
        "    2. S18_4027 — 7 vistas",
        "    3. S18_3259 — 6 vistas",
        "    4. S18_3140 — 6 vistas",
        "    5. S700_3962 — 6 vistas",
        "=================================================="
      ]),
      spacer(240),

      heading2("Estructura de Datos Resultante (docs/resultados_metricas.csv)"),
      para("El procesamiento continuo de eventos persiste los datos resultantes consolidados en un archivo CSV estructurado. El esquema y descripción de las columnas de este dataset resultante es el siguiente:"),
      spacer(120),
      csvSchemaTable(),
      spacer(240),

      heading2("Análisis Estadístico de los Resultados"),
      para("El análisis de los resultados en consola y en el archivo CSV generado valida el pipeline de streaming:"),
      bullet("Consistencia de Volumen de Datos: La Ventana Completa (02:53 a 02:54) registró 299 eventos procesados en 60 segundos. Con una tasa de simulación de 5 eventos por segundo, se ratifica la entrega exacta de mensajes sin encolamiento ni pérdidas en la capa del broker Redpanda."),
      bullet("Validación Probabilística de Eventos: Los conteos acumulados (vistas ~70%, adición al carrito ~20%, transacciones ~10%) confirman que la capa del producer está distribuyendo el flujo de eventos según las reglas de negocio especificadas."),
      bullet("Detección de SKUs Estrella: El reporte identifica dinámicamente qué productos están teniendo mayor visibilidad instantánea (ej. S24_2360 en la primera ventana, S18_3482 en la segunda), permitiendo alimentar paneles de visualización dinámicos."),
      spacer(480),

      // ── SECCIÓN 7: PREGUNTAS DE DISCUSIÓN ──────────────────────────────────
      new Paragraph({ children: [new PageBreak()] }),
      heading1("7. Cuestionario de Discusión Técnica"),
      spacer(120),

      // Pregunta 1
      heading2("¿Qué es un topic?"),
      para("En los sistemas de mensajería orientados a eventos, un topic representa un canal lógico o una categoría de comunicación donde se organizan e identifican los mensajes. A diferencia de las colas de mensajería tradicionales que eliminan los datos inmediatamente después de que un receptor los lee, un topic en Kafka o Redpanda se comporta como un registro de confirmación (commit log) append-only, estructurado y persistente en disco físico."),
      para("Las características esenciales de un topic son:"),
      bullet("Particionamiento: Para lograr escalabilidad horizontal, un topic se divide en múltiples 'particiones'. Cada partición es una secuencia ordenada e inmutable de mensajes. Las particiones permiten distribuir un único topic entre varios brokers del cluster, permitiendo lecturas y escrituras paralelas a gran escala."),
      bullet("Persistencia y Retención: Los mensajes que llegan al topic se guardan en disco de forma secuencial y duradera. No se eliminan al consumirse; se retienen según las políticas de tiempo (ej. 7 días) o tamaño configuradas, permitiendo que múltiples sistemas independientes lean los mismos datos en momentos distintos."),
      bullet("Inmutabilidad: Una vez que un mensaje ha sido escrito en una partición, no puede ser modificado ni alterado. Esto proporciona una fuente de verdad única para auditoría e históricos."),
      spacer(80),
      codeBlockBox([
        "Topic: user-activity",
        "  Partición 0: [msg 0][msg 1][msg 2][msg 3]...",
        "  Partición 1: [msg 0][msg 1][msg 2]...",
        "  Partición 2: [msg 0][msg 1][msg 2][msg 3][msg 4]..."
      ]),
      spacer(200),

      // Pregunta 2
      heading2("¿Cuál es la diferencia entre producer y consumer?"),
      para("La diferencia fundamental radica en la dirección de la transmisión de datos y el nivel de control sobre el broker:"),
      bullet("Producer (Productor): Es el emisor de los datos. Funciona bajo un modelo 'push'. Se conecta al broker, determina a qué partición del topic debe enviar un mensaje (basándose en un algoritmo de reparto como Round-Robin o un hash de la clave del mensaje como 'customer_id') y lo empuja al broker de manera activa. No tiene conocimiento de qué consumidores están leyendo el topic o si existen en absoluto."),
      bullet("Consumer (Consumidor): Es el receptor de los datos. Funciona bajo un modelo 'pull'. Se conecta al broker Redpanda y solicita activamente lotes de mensajes cuando tiene capacidad de procesamiento disponible. Esto evita que el broker abrume al consumidor (inundación de memoria). Los consumidores pueden agruparse en 'Consumer Groups' para repartirse la lectura de las particiones de un topic, permitiendo escalar el procesamiento de forma balanceada."),
      spacer(80),
      calloutBox("Modelo Push vs Pull", [
        "El Producer empuja (push) datos hacia el cluster Redpanda a máxima velocidad.",
        "El Consumer jala (pull) datos desde el cluster según sus propios recursos de hardware.",
        "Esto evita cuellos de botella y permite que el procesador trabaje de forma estable."
      ]),
      spacer(200),

      // Pregunta 3
      heading2("¿Por qué los sistemas de streaming usan offsets?"),
      para("Un offset es un número entero secuencial asignado de forma única a cada mensaje dentro de una partición específica. El offset actúa como un cursor o puntero que indica la posición exacta de un mensaje en la partición."),
      para("El uso de offsets es una de las mayores innovaciones de diseño en Kafka/Redpanda por los siguientes motivos:"),
      bullet("Desacoplamiento del Estado: En los brokers tradicionales, el servidor debe recordar qué mensajes leyó cada cliente. Esto no escala. Con offsets, el consumidor gestiona su propio progreso de lectura y confirma periódicamente su posición al broker (auto-commit o commits manuales). El broker se mantiene sin estado en este aspecto, maximizando el rendimiento."),
      bullet("Tolerancia a Fallas: Si un consumidor se apaga debido a un error, al reiniciarse consulta al broker Redpanda cuál fue el último offset que confirmó (almacenado en el topic interno '__consumer_offsets') y reanuda el procesamiento desde ese punto exacto, garantizando consistencia."),
      bullet("Replay de Eventos: Debido a que los datos permanecen físicamente en el log, un consumidor puede resetear su offset hacia atrás (por ejemplo, a cero o a un timestamp de hace 3 horas) para volver a procesar datos históricos ante cambios de lógica o recuperación de errores."),
      spacer(200),

      // Pregunta 4
      heading2("¿Qué pasa si el consumer está fuera de línea durante unos minutos?"),
      para("Si el procesador de métricas (`ecommerce_metrics_consumer.py`) se desconecta o cae durante unos minutos, **no ocurre ninguna pérdida de información**. El sistema está diseñado para tolerar fallas de forma nativa:"),
      bullet("Persistencia en el Broker: El productor (`ecommerce_producer.py`) continuará funcionando y publicando eventos al topic de manera habitual. Redpanda recibirá estos eventos y los escribirá inmediatamente en el almacenamiento de disco de las particiones correspondientes."),
      bullet("Incremento del Lag: El 'Consumer Lag' (la distancia entre el offset del último mensaje producido y el último offset leído por el consumidor) comenzará a crecer de forma lineal, reflejando el trabajo acumulado."),
      bullet("Recuperación en Ráfaga (Catch-up): Cuando el consumidor vuelva a estar en línea, leerá su último offset confirmado y comenzará a consumir en lotes masivos a máxima velocidad. Procesará el historial rezagado rápidamente en ráfaga hasta que el lag vuelva a cero, momento en el cual volverá a operar en tiempo real. Este comportamiento protege la integridad del análisis de datos."),
      spacer(80),
      codeBlockBox([
        "01:55 PM — Producer publica 300 eventos/minuto a Redpanda",
        "01:58 PM — El Consumer cae temporalmente (reinicio de servidor)",
        "02:02 PM — El Consumer se reconecta.",
        "           ↓",
        "           Consulta el offset guardado (01:58 PM)",
        "           Consume ráfaga de ~1,200 mensajes almacenados en disco",
        "           Procesa las ventanas rezagadas en segundos.",
        "02:03 PM — Consumer al día. Lag = 0. Operando en tiempo real de nuevo."
      ]),
      spacer(200),

      // Pregunta 5
      heading2("¿Por qué el broker es útil entre la aplicación y el procesador?"),
      para("El broker de mensajería (Redpanda) actúa como una capa intermedia crucial de desacoplamiento y amortiguación en la arquitectura de datos corporativa. Sus ventajas se agrupan en tres pilares:"),
      bullet("1. Desacoplamiento Temporal y Tolerancia a Fallos: Elimina el acoplamiento directo entre el emisor y el receptor. El productor de la tienda web no necesita saber si el agregador de métricas está activo o caído para seguir registrando las interacciones de los usuarios. Esto previene fallos en cascada."),
      bullet("2. Control de Flujo y Mitigación de Picos (Backpressure): Las aplicaciones de e-commerce experimentan grandes variaciones en el tráfico (ej. campañas publicitarias o Black Friday). Si el productor llamara directamente al procesador a través de API HTTP, el servidor de analítica colapsaría. Redpanda actúa como un buffer absorbente de alta velocidad, almacenando millones de eventos por segundo en disco, permitiendo que el consumidor extraiga los datos a un ritmo seguro y controlado según sus recursos de hardware."),
      bullet("3. Extensibilidad y Consumo Multidifusión (Fan-out): Un único topic de eventos ('user-activity') puede ser consumido simultáneamente por múltiples sistemas independientes (ej. el procesador de métricas del Grupo 3, un motor de machine learning de recomendaciones en tiempo real y una base de datos analítica como ClickHouse) sin que el productor deba duplicar los envíos o modificar su código. El broker gestiona los offsets de cada grupo de consumidores de forma aislada."),
      spacer(240),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("docs/Grupo3_Kafka_Proyecto.docx", buffer);
  console.log("✅ Documento técnico premium generado exitosamente en: docs/Grupo3_Kafka_Proyecto.docx");
});