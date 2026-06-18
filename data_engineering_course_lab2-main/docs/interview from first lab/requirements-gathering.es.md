# Estudio de Caso de Levantamiento de Requisitos

Este documento presenta un escenario de entrevista con un stakeholder para que
los estudiantes practiquen el levantamiento de requisitos antes de disenar un
sistema de ingenieria de datos.

El objetivo no es solamente identificar lo que el stakeholder pide, sino tambien
separar sintomas, necesidades del negocio, restricciones tecnicas, preguntas
abiertas y posibles decisiones de arquitectura de datos.

## Escenario

Un nuevo ingeniero de datos se une a una empresa y se reune con una cientifica
de datos que apoya al equipo de marketing. El equipo de marketing quiere
analitica de ventas de productos mas fresca por region y, eventualmente,
recomendaciones de productos mas personalizadas para los clientes que navegan en
la plataforma de ventas.

Por el momento, la cientifica de datos recibe un volcado manual de datos una vez
al dia por parte del equipo de ingenieria de software. La base de datos de
produccion contiene los datos fuente de ventas, pero el equipo de software no
quiere dar acceso directo por riesgo operacional.

## Entrevista con el Stakeholder

**Ingeniero de datos:** Hola, soy Joe y me acabo de unir esta semana como nuevo
ingeniero de datos. Estoy emocionado de empezar a trabajar contigo en proyectos
de datos. Pense que seria muy util conversar sobre en que estas trabajando y
como puedo ayudarte.

**Cientifica de datos:** Si, absolutamente. Es un gusto conocerte y tenerte en
la empresa. Empece aqui como cientifica de datos hace unos meses, y ha sido
agotador, por decirlo suavemente.

**Ingeniero de datos:** ¿Agotador? Cuentame mas.

**Cientifica de datos:** Nuestro equipo de marketing esta pidiendo analisis en
tiempo real de las ventas de productos por region. Quieren ver cosas como que
productos compraron los clientes, donde estan ubicados los clientes y otros
comportamientos de ventas.

Ahora mismo, toda la informacion de ventas de productos esta en la base de datos
de produccion de nuestra plataforma de ventas. El equipo de ingenieria de
software no quiere darme acceso directo porque les preocupa que pueda romper
algo. Por eso, me entregan un volcado de datos una vez al dia, y yo lo descargo
manualmente.

**Ingeniero de datos:** Entonces estas obteniendo la informacion que necesitas,
pero el proceso es incomodo porque tienes que descargarla manualmente.

**Cientifica de datos:** Supongo que si estoy obteniendo la informacion, pero
tambien estoy recibiendo muchos datos que no necesito. Alrededor del 90% del
volcado no es necesario para mi trabajo. Los datos estan guardados en varios
archivos CSV y JSON. Tengo que ejecutar una serie de pasos de procesamiento para
extraer lo que necesito de cada archivo, limpiarlo, agregarlo y guardarlo en un
formato que pueda usar para dashboards.

**Ingeniero de datos:** Suena a que estas dedicando mucho tiempo a procesar los
datos antes de poder usarlos para analitica.

**Cientifica de datos:** Si. Probablemente dedico cerca del 80% de mi tiempo a
limpiar y procesar datos.

Muchas veces mis scripts de procesamiento fallan porque hay anomalias o entradas
inesperadas en los archivos del equipo de software. Algunas veces el equipo de
software ha cambiado el formato del volcado de datos, y solo me entero cuando
mis scripts dejan de correr. Luego tengo que refactorizar todo para que funcione
con el nuevo formato.

No es raro que pase un dia entero llevando los datos a un formato util para los
dashboards. Mientras tanto, el equipo de marketing quiere analitica regional de
ventas en tiempo real. Para cuando publico actualizaciones, la informacion a
menudo ya tiene dos dias de antiguedad.

**Ingeniero de datos:** Eso suena doloroso. Si entiendo correctamente, hay dos
problemas principales. Primero, solo recibes volcados de datos una vez al dia.
Segundo, los pasos de limpieza y procesamiento son manuales, laboriosos e
impredecibles.

**Cientifica de datos:** Exactamente. Con el proceso actual, no veo como podria
entregar resultados mas rapido. Marketing quiere metricas actuales, no numeros
de hace dos dias.

**Ingeniero de datos:** Mencionaste que marketing quiere actualizaciones en
tiempo real. ¿Que esperan hacer con esa informacion?

**Cientifica de datos:** Estan enfocados en entender la efectividad de sus
campanas de marketing y en observar tendencias de corto y largo plazo en ventas
de productos para poder programar mejor sus campanas.

Tambien hemos estado trabajando en un motor de recomendaciones para el sitio web
que sugiera productos a los clientes cuando navegan o hacen una compra.

**Ingeniero de datos:** Entonces hay varios casos de uso distintos. Ahora mismo,
tu entregas dashboards y un motor de recomendaciones que cubren algunas de esas
necesidades.

**Cientifica de datos:** Si y no.

Para los dashboards, muestro ventas de productos por categoria y region durante
los ultimos 30 dias. El dashboard incluye totales de 30 dias y graficos de linea
con numeros diarios. Marketing pidio eso para poder ver tendencias generales de
una region a otra.

Tambien pueden profundizar en una region para ver un desglose mas fino por
producto individual o por una cadencia de tiempo mas pequena, como por hora en
lugar de por dia. Pero los datos normalmente tienen al menos dos dias de atraso,
asi que no muestran numeros actuales.

Para el recomendador, actualmente estoy analizando que productos han sido los
mas populares durante la ultima semana. Le paso esos IDs de producto al equipo
de software para que recomienden productos populares a todos los que navegan el
sitio web.

Todavia no esta personalizado para clientes individuales. Solo muestra productos
populares.

Estoy trabajando en entrenar un modelo para hacer recomendaciones
personalizadas usando un metodo de filtrado basado en contenido, pero todavia no
hay nada desplegado.

**Ingeniero de datos:** Para el sistema de recomendaciones, suena a que
necesitas mas datos para entrenamiento. Una vez que el modelo este listo para
desplegarse, necesitaras un sistema que envie datos de actividad de usuarios
desde la plataforma de ventas hacia el modelo y que envie recomendaciones de
productos de vuelta a la plataforma mientras el usuario esta navegando.

**Cientifica de datos:** Si, ese es el plan. Como en cualquier sitio o app de
ecommerce, cuando los usuarios navegan, agregan productos al carrito o hacen
compras, deberian ver recomendaciones de productos basadas en lo que han estado
viendo o comprando.

**Ingeniero de datos:** Para los dashboards, dijiste que marketing quiere datos
actuales. ¿Sabes que acciones esperan tomar con datos actuales que no pueden
tomar con datos de hace dos dias?

**Cientifica de datos:** Han hablado sobre orientar campanas publicitarias
basadas en datos actuales. Eso podria significar observar que estan haciendo los
clientes ahora mismo en terminos de compras u otra actividad en la plataforma de
ventas.

Pero no estoy segura de si necesitan saber lo que los clientes hacen en este
segundo, dentro de la ultima hora, o simplemente hoy en vez de ayer.

**Ingeniero de datos:** Eso ayuda. Puedo hacer seguimiento con marketing para
entender que acciones quieren tomar. Si conocemos la accion, podemos decidir
cuanta latencia puede tolerar el sistema.

**Cientifica de datos:** Tiene sentido. Avisame si hay algo mas que pueda hacer
para ayudar.

**Ingeniero de datos:** Esta conversacion ha sido muy util. Si entiendo bien,
ayudaria mucho crear un proceso de ingestion mas directo y oportuno desde la
base de datos donde se registran las ventas.

Luego necesitamos automatizar y orquestar la transformacion y entrega de esos
datos en el formato que necesitas para dashboards y recomendaciones.

**Cientifica de datos:** Si, definitivamente. Si la ingestion y el procesamiento
de datos pudieran manejarse automaticamente y almacenarse en el formato que
necesito, mi vida seria mucho mas facil y podria enfocarme en el analisis.

**Ingeniero de datos:** Perfecto. Un buen siguiente paso es conversar con el
equipo de marketing para entender mejor sus necesidades.
