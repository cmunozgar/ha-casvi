# Cambios

## 0.6.1

- Incluye el README actualizado con todas las funciones de 0.6.0 en la versión descargada por HACS.
- Elimina el número de versión del título del README para evitar confundirlo con la versión instalada.
- Sin cambios de funcionamiento respecto a 0.6.0.

El icono de Casvi está incluido en el paquete. Su visualización en la tienda sigue pendiente de la corrección de HACS: https://github.com/hacs/frontend/pull/937.

## 0.6.0

- Nueva sección Eventos: calendario mensual de lunes a viernes en escritorio y agenda diaria en móvil.
- Inicio muestra los eventos del último día con anotaciones hasta hoy, antes de los mensajes.
- Eventos compactos con vista previa y contenido completo en una modal.
- Título real o tipo de evento, fecha y hora; se recuperan también los eventos pasados que devuelve Casvi.
- Etiquetas de color con el nombre de cada alumno en mensajes y eventos, incluidos los detalles.
- Estructura visual compartida para eventos y mensajes, sin huecos cuando no hay alumno asociado.
- Paneles blancos y estados vacíos con iconos y textos claros.
- Validación: 64 pruebas Python y 3 pruebas JavaScript, además de comprobaciones locales con datos reales.

Después de actualizar en HACS, reinicia Home Assistant y recarga el panel.

## 0.5.2

- Comedor en formato agenda diaria en móvil, conservando el calendario mensual en escritorio.
- Desplazamiento al día actual al abrir el comedor; si no aparece, al siguiente día mostrado o al último del mes.
- Corrección de los iconos de las entidades de mensajes pendientes.

El logo de la tienda HACS sigue pendiente de la corrección de HACS para marcas locales.

Después de actualizar en HACS, reinicia Home Assistant y recarga el panel.

## 0.5.1

- Carrusel de menús en móvil: hoy ocupa todo el ancho, con desplazamiento a ayer y mañana.
- Indicadores circulares para cambiar de día y señalar la tarjeta visible.
- Selector móvil de secciones con iconos, sección activa resaltada y acceso al menú lateral.
- Se mantienen las pestañas y las tres tarjetas en escritorio.

Después de actualizar en HACS, reinicia Home Assistant y recarga el panel.

## 0.5.0

- Comedor con calendario del mes actual de lunes a viernes y título centrado.
- Mensajes no leídos entre comedor y clases, con contador en el título.
- Lectura confirmada en Casvi al abrir un mensaje y actualización del estado en el panel.
- Mensajes con formato, enlaces en otra pestaña, fecha y cierre de modal compacto.
- Indicador de adjuntos y vista previa autenticada de imágenes y PDF de hasta 5 MB (hasta 10 páginas), con descarga.
- Nuevas entidades de mensajes pendientes para widgets: tres mensajes recientes globales y contador y último pendiente por alumno.
- Fichas de alumnos en caché persistente por curso, compartida con la lectura de horarios; acción casvi.refresh_school_data para renovar los datos.
- Nombres de pila en las pestañas y tarjetas, menú lateral en móvil y cargadores centrados.
- Validación: 63 pruebas Python y 3 pruebas JavaScript.

## 0.4.0

- Inicio con menús de ayer, hoy y mañana, horarios diarios por hijo y mensajes no leídos a todo el ancho.
- Panel sin cabecera, navegación con iconos y actualización al entrar en cada sección.
- Fichas con tabla semanal visible, profesores por asignatura y compañeros numerados.
- Extractos de mensajes disponibles tras su lectura, sin abrir automáticamente los pendientes.
- Dos entidades por hijo: Piscina hoy y Educación física hoy (incluye psicomotricidad).
- Extracción local de los PDF y almacenamiento persistente de los horarios en Home Assistant.
- Acción casvi.refresh_schedules para forzar una nueva lectura del PDF.
- Los horarios se comprueban diariamente y se actualizan cuando cambia el documento o el curso. EF/NAT se mantiene como desconocido; no se aplican festivos.
- 48 pruebas Python y 3 pruebas del analizador de horarios, además de validación local de ambos PDF reales.

## 0.3.1

- Sección Profesores en cada ficha de alumno, con fotos y asignaturas agrupadas por docente.
- Carga autenticada de imágenes y estado «Sin foto» cuando no están disponibles.
- Un fallo al consultar profesores no impide ver el resto de la ficha.
- 36 pruebas y validación de profesores y fotos en ambos grupos de una cuenta real.

## 0.3.0

- Logotipo de Casvi para identificar el servicio.
- Inicio con los últimos 10 mensajes y pestaña de buzón completo paginada.
- Alumnos destinatarios en las filas y en la lectura de mensajes.
- Pestaña por hijo con grupo, tutor, tutorías, compañeros y documentos.
- Horario PDF dentro del panel mediante visor local PDF.js.
- Acceso bajo demanda y respeto de la visibilidad para familias.
- 31 pruebas automatizadas, verificación de consultas reales y pruebas del navegador con datos inventados.

## 0.2.0

- Panel Colegio automático: menú, agenda y mensajes recientes con filtro de pendientes.
- Lectura de texto bajo demanda y enlace a la intranet para adjuntos.
- Avisos a móviles seleccionados en las opciones, con enlace directo al mensaje.
- Detección persistente, primera carga silenciosa y reintentos limitados.
- Acceso al panel y cuerpos de mensajes restringido a administradores.
- 23 pruebas automatizadas y revisión del panel en navegador con datos sintéticos.

## 0.1.1

- Distribución como repositorio personalizado HACS.
- Documentación de instalación para familias, licencia MIT e icono propio.
- Validaciones automáticas de HACS, Home Assistant y pruebas sin credenciales.
- Conserva el dominio y las entidades de 0.1.0.

## 0.1.0

- Login con renovación de sesión.
- Calendario por alumno, menú del día y sensores de mensajes recientes.
