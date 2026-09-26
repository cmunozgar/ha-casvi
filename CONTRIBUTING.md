# Contribuir

Las pruebas usan ejemplos inventados y no requieren cuenta del colegio. No subir respuestas reales, identificadores de alumnos, cookies, contraseñas, APKs ni capturas privadas.

Con Python 3.13, instala `requirements-test.txt` en un entorno virtual y ejecuta `python -m pytest -q`. Propón cambios mediante una pull request explicando el comportamiento y la prueba realizada.

El cliente usa operaciones de consulta, comprueba la sesión antes y después de cada ciclo y limita los reintentos. Mantén ese comportamiento. Los errores no deben incluir cuerpos de respuesta ni credenciales.

Cada versión publicada debe actualizar `manifest.json` y `CHANGELOG.md`. Espera a que las comprobaciones HACS, hassfest y tests pasen antes de crear la etiqueta correspondiente. No subir los archivos privados empleados para desarrollar la integración.
