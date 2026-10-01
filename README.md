# Casvi para Home Assistant

Integración personalizada para Home Assistant Container. Conecta directamente con la intranet, sin otro contenedor ni broker MQTT. Cada entrada utiliza una cuenta familiar y el centro predeterminado de esa sesión.

Integración comunitaria no oficial, sin vinculación con el colegio Casvi. Cada familia utiliza su propia cuenta; el acceso se realiza directamente desde su Home Assistant a la intranet. No hay un servidor intermediario ni telemetría.

## Instalación con HACS

Requiere Home Assistant 2025.1 o posterior y HACS instalado. Probada con Home Assistant 2025.1.4; la compatibilidad con otras versiones se comprueba progresivamente.

1. Abre HACS y entra en el menú de **Repositorios personalizados**.
2. Añade `https://github.com/cmunozgar/ha-casvi` con tipo **Integración**.
3. Busca **Casvi**, descárgala y reinicia Home Assistant.
4. Abre **Ajustes → Dispositivos y servicios → Añadir integración → Casvi**.
5. Introduce tus propias credenciales y selecciona los hijos.

HACS permite instalar las siguientes versiones desde el mismo repositorio. Esta integración todavía no pertenece al catálogo predeterminado de HACS.

Si ya instalaste la versión manual con dominio `casvi`, haz una copia de seguridad y descarga desde HACS en esa misma instalación. No crees otra cuenta: se conservan la configuración y los identificadores de las entidades al reemplazar los archivos y reiniciar.

## Instalación manual

1. Localiza la carpeta del servidor que tienes montada como `/config` en el contenedor de Home Assistant.
2. Copia la carpeta `custom_components/casvi` de este paquete a `<tu_config>/custom_components/casvi`. El resultado debe contener `/config/custom_components/casvi/manifest.json`.
3. Reinicia el contenedor de Home Assistant.
4. Abre **Ajustes → Dispositivos y servicios → Añadir integración → Casvi**. Si no aparece, recarga el navegador después del reinicio.
5. Introduce usuario y contraseña de Casvi. Selecciona los hijos cuyas agendas quieres añadir.

No copies el APK, los informes de ingeniería inversa ni el directorio de trabajo. No necesitas editar `configuration.yaml`. No requiere Supervisor ni una instalación HACS. También se puede instalar desde HACS como repositorio personalizado.

## Panel Colegio

Después de instalar o actualizar, reinicia Home Assistant y recarga el navegador o la app para cargar el panel nuevo. **Colegio** aparece en el menú lateral. Requiere un usuario administrador de Home Assistant; las entidades mantienen los permisos habituales de Home Assistant. Si hay varias cuentas, puedes elegir la familia.

En ordenador, las secciones se muestran como pestañas con iconos. En móvil se agrupan en un selector con iconos y la sección activa resaltada, junto al botón para abrir el menú lateral de Home Assistant. Los paneles tienen fondo blanco, estados vacíos explicativos y cargadores centrados.

### Inicio

Las secciones aparecen en este orden:

1. **Comedor:** ayer, hoy y mañana; hoy está centrado en escritorio. En móvil cada tarjeta ocupa todo el ancho, empieza en hoy y permite deslizar o tocar los tres indicadores circulares.
2. **Eventos del último día:** las anotaciones del día más reciente con eventos hasta hoy, indicando el alumno. No es una lista de próximos eventos.
3. **Mensajes no leídos (N):** pendientes entre los mensajes recientes consultados, a todo el ancho. El número no representa necesariamente todos los pendientes del buzón.
4. **Clases de hoy por hijo:** horario diario e indicadores de piscina y educación física; en Infantil se muestra psicomotricidad.

### Mensajes y eventos

Las tarjetas del comedor y de clases tienen bordes completos y esquinas redondeadas.

Las tarjetas de eventos y mensajes comparten estructura: título, etiquetas de alumnos y fecha/hora, seguidos de una vista previa de dos líneas. Los mensajes incluyen el remitente y un clip si tienen adjuntos. Cada alumno se identifica con una etiqueta de color y solo su nombre; el color se mantiene entre vistas. Si Casvi no indica alumno, no se deduce del asunto ni se reserva un hueco para la etiqueta.

Al pulsar una tarjeta se abre una modal con el contenido completo, fecha y alumnos. Los enlaces se abren en otra pestaña. Los mensajes conservan párrafos, saltos, listas y formato permitido, omitiendo contenido oculto y HTML activo.

La pestaña **Mensajes** permite recorrer el buzón completo con paginación del servidor, 20 mensajes por página. Al abrir un mensaje se solicita marcarlo como leído en Casvi. Si la confirmación falla, se muestra un aviso y se conserva como pendiente. El sondeo automático no abre ni marca mensajes pendientes.

Los adjuntos PDF e imágenes se descargan con la sesión de la integración y se muestran dentro de la modal, sin necesitar un login de Casvi en el navegador. La vista previa admite hasta 5 MB y las primeras 10 páginas de cada PDF. Los archivos previsualizados también pueden descargarse. Para otros formatos o si falla la vista previa, se mantiene el enlace original de descarga cuando está disponible; ese enlace puede requerir iniciar sesión en la intranet. El visor PDF.js está incluido y no envía documentos a servicios externos.

### Eventos

La pestaña **Eventos** muestra un calendario mensual de lunes a viernes en escritorio y una agenda por días con eventos en móvil, ordenada del más reciente al más antiguo (también dentro de cada día). Permite cambiar de mes dentro de los datos recibidos de Casvi. Las tarjetas compactas abren el detalle en una modal.

Se usa el título del evento o, si está vacío, su tipo, como «Actividades» u «Otros», junto con la fecha y hora. Se incluyen los eventos pasados que devuelve la intranet. No se garantiza un histórico completo ni se solicitan meses adicionales mediante una API de histórico. La vista de calendario omite sábado y domingo.

### Comedor

La pestaña **Comedor** muestra únicamente el mes actual: calendario de lunes a viernes en escritorio y agenda diaria en móvil. Al entrar desde móvil se desplaza hacia hoy; si ese día no aparece, busca el siguiente día mostrado o el último del mes. No tiene navegación a otros meses.

### Actualización del panel

Al entrar en una sección se solicita actualizar la información general y se carga la página o ficha correspondiente. El panel consulta el resumen cada 30 segundos; este intervalo no equivale a una consulta nueva de todos los datos a la intranet. El sondeo de la integración es configurable y las fichas reutilizan su caché.

## Avisos al móvil

Para activar avisos:

1. Instala y conecta la app **Home Assistant Companion** en el móvil y permite sus notificaciones.
2. En **Ajustes → Dispositivos y servicios → Casvi → Configurar**, selecciona uno o varios móviles en **Móviles para recibir avisos**.
3. Guarda. Los mensajes nuevos detectados en los siguientes ciclos generan un aviso; tocarlo abre el mensaje en Colegio. Para hacerlo fuera de casa, la app necesita acceso remoto a tu Home Assistant.

El aviso dice «Tienes un nuevo mensaje» y no incluye el asunto, remitente ni contenido en la pantalla bloqueada. La primera consulta establece una referencia y no notifica todo el buzón. Los identificadores ya detectados se conservan entre reinicios; los envíos fallidos se reintentan hasta tres veces. Un cierre justo después de enviar y antes de guardar puede repetir el aviso, con la misma etiqueta para reemplazarlo cuando lo permita el móvil.

Los avisos se comprueban cada 15 minutos por defecto (configurable). Solo abarcan la ventana de mensajes recientes; si entran más mensajes que el límite entre consultas, algunos pueden quedar fuera. Aumentar el límite no notifica el historial anterior a la primera consulta. La bandeja completa permite abrir también mensajes históricos después de cargar su página. Un aviso cuyo mensaje no esté en la lista reciente ni en las páginas cargadas puede requerir localizarlo en la pestaña Mensajes.

## Pestaña de cada hijo

Cada hijo tiene una pestaña con su nombre, grupo, **horario semanal completo**, profesores por asignatura y compañeros numerados a todo el ancho. No incluye secciones de tutorías, documentos, eventos o mensajes recientes.

La sección **Profesores** muestra una tarjeta por asignatura: el mismo docente puede repetirse si imparte varias. Los nombres aparecen con nombre y después apellidos. Las fotos se cargan al abrir la ficha a través de Home Assistant; no requieren sesión de Casvi en el navegador. Si no hay foto se indica «Sin foto». Un fallo de profesores no impide consultar el resto de la ficha.

Las fotos admiten JPEG, PNG, GIF y WebP de hasta 2 MB; no se siguen enlaces arbitrarios ni redirecciones externas. No se publican fotos de compañeros. Se utiliza el grupo que la intranet selecciona inicialmente para el alumno.

## Horarios y caché local

La integración extrae la tabla semanal del PDF del horario mediante `pdfplumber` en Home Assistant. El panel reutiliza esa tabla; dispone también de una lectura local con PDF.js como alternativa si no recibe un horario extraído. No usa OCR ni servicios externos. Se han comprobado formatos de Infantil y Primaria; los PDF escaneados u otros diseños pueden no reconocerse.

La tabla extraída se guarda en `.storage/casvi.schedules.<entry_id>` y las fichas en `.storage/casvi.profiles.<entry_id>`. La caché de fichas incluye profesores y compañeros, sobrevive a reinicios y se renueva al cambiar de curso, el 1 de septiembre. Las respuestas incompletas no se conservan como caché anual. Las fotos cargadas por separado no se guardan como archivos independientes ni atributos de entidades.

El horario se comprueba diariamente usando la ficha en caché; el PDF se reutiliza si su identidad no cambia. Un cambio durante el curso puede requerir actualización manual, porque los documentos de la ficha también están en la caché anual. En **Herramientas para desarrolladores → Acciones** puedes ejecutar:

| Acción | Efecto |
| --- | --- |
| `casvi.refresh_schedules` | Invalida la caché de fichas y fuerza una nueva descarga y lectura de los horarios. |
| `casvi.refresh_school_data` | Renueva las fichas escolares y vuelve a cargar los horarios. |

Los horarios son los habituales: no descuentan festivos, vacaciones ni cambios puntuales. `EF/NAT` se interpreta como natación. Al eliminar la cuenta de la integración se borran sus cachés persistentes y el historial de identificadores de avisos.

## Entidades

- Calendario de agenda por hijo, con los eventos que devuelve la intranet.
- Sensor de comedor de hoy. Su estado muestra el texto del menú en una línea, abreviado a 255 caracteres si es necesario; el atributo `menu` conserva el texto completo y `fecha` indica el día. Si no hay menú para hoy, muestra «Sin menú publicado».
- Total de mensajes recibidos.
- Número de mensajes no leídos **entre los últimos 50**. No es el total de pendientes de todo el buzón. Los atributos indican el tamaño de la muestra.
- Cuatro sensores binarios por hijo: **Piscina hoy**, **Educación física hoy**, **Piscina mañana** y **Educación física mañana** (incluye psicomotricidad). Inicio incluye un resumen «Para mañana» para preparar la mochila. Si falta el horario no están disponibles; `EF/NAT` activa Piscina hoy; Educación física hoy solo se activa si hay otra franja de educación física o psicomotricidad. Los fines de semana quedan desactivados.
- Tres sensores de mensajes pendientes recientes para widgets y, por alumno, un contador y el último pendiente.
- Último mensaje: asunto, remitente, fecha, estado de lectura y nombres de adjuntos. El contenido completo se obtiene únicamente si ya está leído; si está pendiente, `contenido_disponible` será falso.

La actualización predeterminada es cada 15 minutos. En **Configurar** puedes elegir entre 5 y 120 minutos y entre 10 y 100 mensajes recientes. El menú mensual se consulta en cada ciclo. El sondeo automático no importa todo el historial. La bandeja completa consulta el histórico por páginas bajo demanda; los adjuntos se descargan bajo demanda al abrir el mensaje.

No envía, borra ni acepta mensajes del colegio, ni modifica agenda o incidencias. La única modificación de mensajes es marcarlos como leídos al abrirlos en el panel. No hay un listado separado de comunicados en esta versión: solo aparecen los registros que la bandeja recibida devuelva.

### Entidades para widgets de mensajes

Además del contador general, se crean tres sensores de mensaje no leído (posiciones 1, 2 y 3, más reciente primero). Por alumno se crean un contador de pendientes recientes y un sensor del último pendiente. El estado del sensor de mensaje es su asunto; los atributos incluyen `fecha`, `remitente`, `alumnos`, `id`, `id_para` y `url` para abrir el mensaje en el panel. No se descarga el cuerpo ni se marca leído al consultar estas entidades.

Los contadores y posiciones se calculan sobre la ventana configurada de mensajes recientes (50 por defecto), no sobre todo el buzón. Los mensajes sin destinatario alumno explícito solo aparecen en los sensores generales. Al quedar vacía una posición muestra «Sin mensajes pendientes» y elimina los atributos del mensaje anterior.

En la aplicación de Home Assistant para iOS, estos sensores se pueden seleccionar para mostrar su estado en un widget compatible. La actualización del widget depende de iOS y puede retrasarse respecto a Home Assistant. Consulta la [documentación de widgets iOS](https://companion.home-assistant.io/docs/integrations/ios-widgets/).

## Login y renovación

El cliente crea su propia sesión, envía el formulario de login y verifica `controles/sesion.php` con `accion=check`. Antes y después de cada consulta conjunta comprueba la sesión. Si caduca, descarta los datos parciales, inicia sesión y reintenta una vez. Esto evita confundir una sesión caducada con un buzón vacío.

Si las credenciales se rechazan, Home Assistant solicitará reautenticación. Un fallo de conexión no dispara bucles de login. Las cookies solo viven en memoria y se cierran al descargar la integración. Usuario y contraseña se guardan en la configuración de Home Assistant; protege también sus copias de seguridad. No se incluyen credenciales en este paquete.

## Límites conocidos

- El servidor no documenta cuánto historial devuelve la agenda. El calendario filtra la lista recibida; no puede prometer otros meses ni expandir recurrencias no proporcionadas por Casvi.
- `start` no lleva zona en la muestra observada: se interpreta en `Europe/Madrid`.
- La API no proporciona hora de fin. Se utiliza **un minuto** como duración técnica para representar el evento, no como duración escolar real. No usar el fin para deducir cuándo termina una actividad.
- No incluye notas ni ausencias como entidades independientes. La extracción del horario depende del formato del PDF publicado por el colegio.
- El logo está incluido en `brand/`, pero su aparición en la tienda depende del soporte de HACS para marcas locales; véase [hacs/frontend#937](https://github.com/hacs/frontend/pull/937).
- El descubrimiento de hijos lee los enlaces familiares del escritorio; si cambia el HTML o la cuenta no tiene esa navegación, puede necesitar adaptación.
- No cambia de centro ni de ficha multicentro. El menú corresponde al centro predeterminado al iniciar sesión.
- Los cambios en la lista de hijos requieren volver a configurar la cuenta.
- Datos de mensajes y calendario pueden quedar en el historial y copias de Home Assistant. La integración no publica cookies, URLs autenticadas ni bloques médicos adicionales como atributos.

## Desarrollo y pruebas

Las pruebas usan datos inventados. Desde esta carpeta, con Python y las dependencias de Home Assistant disponibles:

```sh
python -m pytest -q
node --test tests/test_schedule.mjs
```

No ejecutar pruebas con credenciales reales. La validación de acceso real se realiza aparte, con almacenamiento temporal privado.

Referencias de implementación: [configuración de integraciones](https://developers.home-assistant.io/docs/core/integration/config_flow/), [actualizaciones coordinadas](https://developers.home-assistant.io/docs/integration_fetching_data/) y [calendarios](https://developers.home-assistant.io/docs/core/entity/calendar/).

Validación de 0.6.0: **64 pruebas Python y 3 pruebas JavaScript**, además de HACS y hassfest en GitHub. Se han comprobado en local el acceso real, fichas, horarios, fotos, eventos y navegación móvil, sin incluir datos personales en el repositorio. El envío real a un móvil y la instalación en otras familias todavía requieren validación. No se garantiza el funcionamiento de cuentas o centros todavía no probados.

Consulta [CHANGELOG.md](CHANGELOG.md) para ver los cambios por versión.

## Soporte y contribuciones

Abre una incidencia con las versiones de Home Assistant y Casvi, los pasos y el error sin datos personales. No adjuntes contraseñas, cookies, archivos HAR, mensajes del colegio ni nombres o identificadores de menores. Consulta [CONTRIBUTING.md](CONTRIBUTING.md).

Código bajo licencia MIT. Se utiliza el logotipo de la intranet para identificar el servicio; no implica vinculación oficial. Las marcas y los recursos de terceros tienen sus propias condiciones, descritas en [NOTICE.md](NOTICE.md).

### Eventos nuevos y nombres de alumnos

Las entidades de alumnos muestran solo el nombre, sin apellidos, y conservan sus identificadores. Los nombres personalizados por el usuario en Home Assistant se mantienen.

**Eventos nuevos** está disponible para la cuenta y para cada hijo. Es un contador acumulado de identificadores nuevos desde la primera sincronización: el historial inicial no incrementa el contador. Conserva su valor tras reiniciar, no vuelve a contar eventos que desaparecen y reaparecen, y no cuenta ediciones de eventos existentes. No representa eventos sin leer. El total de la cuenta suma las detecciones por alumno. Puede usarse en automatizaciones comprobando que el nuevo valor sea mayor que el anterior. El seguimiento se elimina al borrar la integración.

Las opciones «Avisos y actualizaciones» permiten activar por separado mensajes y eventos nuevos, con los mismos móviles de destino. Los eventos están desactivados por defecto; los avisos de mensajes conservan el comportamiento anterior. Los avisos de eventos incluyen nombre, título y fecha y abren el panel Colegio. El historial de eventos inicial no se notifica; los eventos detectados mientras los avisos están desactivados tampoco se envían al activarlos. Los móviles se muestran por su nombre y los intervalos se editan con campos numéricos.
