# Casvi para Home Assistant — 0.1.1

Integración personalizada para Home Assistant Container. Conecta directamente con la intranet, sin otro contenedor ni broker MQTT. Primera versión para una cuenta familiar y el centro predeterminado de esa sesión.

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

## Entidades

- Calendario de agenda por hijo, con los eventos que devuelve la intranet.
- Sensor de comedor de hoy. Su estado indica disponibilidad; el atributo `menu` contiene el texto.
- Total de mensajes recibidos.
- Número de mensajes no leídos **entre los últimos 50**. No es el total de pendientes de todo el buzón. Los atributos indican el tamaño de la muestra.
- Último mensaje: asunto, remitente, fecha, estado de lectura y nombres de adjuntos. El contenido completo se obtiene únicamente si ya está leído; si está pendiente, `contenido_disponible` será falso.

La actualización predeterminada es cada 15 minutos. En **Configurar** puedes elegir entre 5 y 120 minutos y entre 10 y 100 mensajes recientes. El menú mensual se consulta en cada ciclo. Esta versión no importa todos los mensajes históricos ni descarga archivos adjuntos.

No envía, borra, acepta ni marca explícitamente mensajes; tampoco modifica agenda o incidencias. No hay un listado separado de comunicados en esta versión: solo aparecen los registros que la bandeja recibida devuelva.

## Login y renovación

El cliente crea su propia sesión, envía el formulario de login y verifica `controles/sesion.php` con `accion=check`. Antes y después de cada consulta conjunta comprueba la sesión. Si caduca, descarta los datos parciales, inicia sesión y reintenta una vez. Esto evita confundir una sesión caducada con un buzón vacío.

Si las credenciales se rechazan, Home Assistant solicitará reautenticación. Un fallo de conexión no dispara bucles de login. Las cookies solo viven en memoria y se cierran al descargar la integración. Usuario y contraseña se guardan en la configuración de Home Assistant; protege también sus copias de seguridad. No se incluyen credenciales en este paquete.

## Límites conocidos

- El servidor no documenta cuánto historial devuelve la agenda. El calendario filtra la lista recibida; no puede prometer otros meses ni expandir recurrencias no proporcionadas por Casvi.
- `start` no lleva zona en la muestra observada: se interpreta en `Europe/Madrid`.
- La API no proporciona hora de fin. Se utiliza **un minuto** como duración técnica para representar el evento, no como duración escolar real. No usar el fin para deducir cuándo termina una actividad.
- No incluye notas, ausencias como entidades independientes ni horario lectivo.
- El descubrimiento de hijos lee los enlaces familiares del escritorio; si cambia el HTML o la cuenta no tiene esa navegación, puede necesitar adaptación.
- No cambia de centro ni de ficha multicentro. El menú corresponde al centro predeterminado al iniciar sesión.
- Los cambios en la lista de hijos requieren volver a configurar la cuenta.
- Datos de mensajes y calendario pueden quedar en el historial y copias de Home Assistant. La integración no publica cookies, URLs autenticadas ni bloques médicos adicionales como atributos.

## Desarrollo y pruebas

Las pruebas usan datos inventados. Desde esta carpeta, con Python y las dependencias de Home Assistant disponibles:

```sh
python -m pytest -q
```

No ejecutar pruebas con credenciales reales. La validación de acceso real se realiza aparte, con almacenamiento temporal privado.

Referencias de implementación: [configuración de integraciones](https://developers.home-assistant.io/docs/core/integration/config_flow/), [actualizaciones coordinadas](https://developers.home-assistant.io/docs/integration_fetching_data/) y [calendarios](https://developers.home-assistant.io/docs/core/entity/calendar/).

Validación realizada: 15 pruebas aprobadas con Home Assistant 2025.1.4 y Python 3.13.1, más acceso real y recuperación tras pérdida de cookie. La instalación y el funcionamiento en otras familias todavía requieren validación. No se garantiza el funcionamiento de cuentas o centros todavía no probados.

## Soporte y contribuciones

Abre una incidencia con las versiones de Home Assistant y Casvi, los pasos y el error sin datos personales. No adjuntes contraseñas, cookies, archivos HAR, mensajes del colegio ni nombres o identificadores de menores. Consulta [CONTRIBUTING.md](CONTRIBUTING.md).

Código bajo licencia MIT. El icono representa una agenda genérica y no es el logotipo del colegio.
