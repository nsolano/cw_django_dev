# Claritywave challenge

Author: CW-TEAM

## Instrucciones:

### How to
1. Genera un fork de este proyecto para que puedas trabajar en tu propio espacio.
2. Una vez finalizado, esperamos que nos envíes el enlace a tu repositorio y el tiempo estimado que te llevó hacerlo. Si no quieres hacer público tu fork, nos puedes contactar y te decimos como lo solucionamos.

### Constraints

Esperamos que dejes una app funcional. 
* En la página principal se tienen que mostrar las mejores 20 preguntas ordenadas según el siguiente ranking:
    1. Cada respuesta suma 10 puntos al ranking
    2. Cada like suma 5 puntos al ranking
    3. Cada dislike resta 3 puntos al ranking
    4. Las preguntas del día de hoy, tienen un extra de 10 puntos
    

_Ejemplo_:
Una pregunta que tiene 6 respuesta de usuarios, 2 likes y 1 dislike:  
ranking: `6*10 + 2*5 - 1*3 = 60 + 10 - 3 = 67`  
Si además es del día de la hoy:  
ranking: `6*10 + 2*5 - 1*3 + 10 = 60 + 10 - 3 +10 = 77`

### A tener en cuenta:
- Modifica todo lo que creas necesario. Dejamos errores voluntariamente.
- Evaluaremos no solo la funcionalidad, también esperamos una buena performance ante la posibilidad de que escale el proyecto
- El sistema de login/logout no es necesario modificarlo. Genera los usuarios para probar desde la consola.

### Extras
- Si puedes levantar un entorno con docker, te invitamos a que lo hagas.
- Nos gustaría ver que puedes generar un test con los casos de usos básicos.

### 

### Ejemplo
Este es un ejemplo de como queda el listado con su ranking y se ve como respondió/votó el usuario actual.

![Example](example.png)

### Levantar el proyecto

Para ejecutar el proyecto, deberás construir el archivo Dockerfile. Puedes hacerlo ejecutando el siguiente comando en la terminal dentro del directorio principal donde se encuentra el Dockerfile:

`sudo docker build -t <nombre_contenedor> .`

Debes ejecutar la imagen generada por el comando anterior. Para lograr esto, primero necesitas buscar el ID de la imagen. Puedes hacerlo ejecutando:

`sudo docker run -p 8080:8080 <nombre_contenedor`

Finalmente, dirígete a `http://localhost:8000/` y verás que está en funcionamiento.

Ten en cuenta que necesitarás tener Docker instalado y en ejecución. En caso de que ya esté instalado, puedes iniciarlo simplemente ejecutando:

`sudo systemctl start docker `

Ten en cuenta que necesitarás tener Docker instalado y en ejecución. En caso de que ya esté instalado, puedes iniciarlo simplemente ejecutando:

`sudo systemctl start docker`

No dudes en contactarme para solucionar problemas o hacer preguntas.

