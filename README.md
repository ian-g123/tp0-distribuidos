# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un esqueleto básico de cliente/servidor, en donde todas las dependencias del mismo se encuentran encapsuladas en containers. Los alumnos deberán resolver una guía de ejercicios incrementales, teniendo en cuenta las condiciones de entrega descritas al final de este enunciado.

 El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target                | accion                                                                                                                                                                                                                                                                                                                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docker-compose-up`   | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers.                                                                                                                                                                                    |
| `docker-compose-down` | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
| `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose.                                                                                                                                                                                                                             |
| `docker-image`        | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto.                                                                                                                        |
| `build`               | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_.                                                                                                                                          |

### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```


## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).


### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `


### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).


### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Condiciones de Entrega
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios y que aprovechen el esqueleto provisto tanto (o tan poco) como consideren necesario.

Cada ejercicio deberá resolverse en una rama independiente con nombres siguiendo el formato `ej${Nro de ejercicio}`. Se permite agregar commits en cualquier órden, así como crear una rama a partir de otra, pero al momento de la entrega deberán existir 8 ramas llamadas: ej1, ej2, ..., ej7, ej8.
 (hint: verificar listado de ramas y últimos commits con `git ls-remote`)

Se espera que se redacte una sección del README en donde se indique cómo ejecutar cada ejercicio y se detallen los aspectos más importantes de la solución provista, como ser el protocolo de comunicación implementado (Parte 2) y los mecanismos de sincronización utilizados (Parte 3).

Se proveen [pruebas automáticas](https://github.com/7574-sistemas-distribuidos/tp0-tests) de caja negra. Se exige que la resolución de los ejercicios pase tales pruebas, o en su defecto que las discrepancias sean justificadas y discutidas con los docentes antes del día de la entrega. El incumplimiento de las pruebas es condición de desaprobación, pero su cumplimiento no es suficiente para la aprobación. Respetar las entradas de log planteadas en los ejercicios, pues son las que se chequean en cada uno de los tests.

La corrección personal tendrá en cuenta la calidad del código entregado y casos de error posibles, se manifiesten o no durante la ejecución del trabajo práctico. Se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección informados  [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).

---

# Ejecucion y consideraciones

## Parte 1: Introducción a Docker

### Ejercicio N°1:

Para ejecutar el script `generar-compose.sh` se debe correr el siguiente comando:

```bash
./generar-compose.sh <nombre_archivo_salida> <cantidad_clientes>
```

Si es que el archivo de salida tiene un nombre distinto a `docker-compose-dev.yaml`, tener en cuenta que el Makefile llama a `docker-compose-dev.yaml` por defecto, por lo que se deberá correr manualmente el archivo generado. Para ello primero debemos levantar las imágenes, corremos `make docker-image` y una vez finalizado, `docker compose -f <nombre_archivo_salida> up -d --build`.

Se contemplaron casos de errores en los parámetros de entrada, como por ejemplo si se ingresa un valor no numérico en la cantidad de clientes, o si se ingresa un valor negativo, o la cantidad de argumentos no es la correcta. En estos casos se imprimirá un mensaje de error y se finalizará la ejecución del script.
Además, si el usuario no ingresa la extensión del archivo de salida, se le agregará automáticamente `.yaml`.

### Ejercicio N°2:

Los archivos de configuración no son copiados al crear la imagen debido al .dockerignore que se ubica en la raíz del proyecto. Deberieron estar en la raíz porque si se ponían dentro de las respectivas carpetas, docker no los leía porque estamos corriendo docker-compose desde la raíz del proyecto. Los archivos son inyectados luego con volumes como lo indica en el archivo `docker-compose-dev.yaml`.

Para ejecutar el ejercicio se debe correr los contenedores normalmente con `make docker-compose-up`. Y para verificar que los contenedores sean modificados mientras están corriendo, se puede modificar los archivos de configuración y con `docker exec -it <nombre_container> sh` se puede verificar que los archivos fueron modificados.

### Ejercicio N°3:

Para ejecutar el script `validar-echo-server.sh` se debe correr el siguiente comando:

```bash
./validar-echo-server.sh
```

Se asume que el contenedor del server se llama `server` y el puerto por el cual se comunica es el `12345`. Se utilizó `https://hub.docker.com/r/gophernet/netcat` ya que en primera instancia hubieron problemas con `subfuzion`.

### Ejercicio N°4:

Para ejecutar el ejercicio se debe correr los contenedores normalmente con `make docker-compose-up`. Luego, para detener los contenedores de forma _graceful_ se debe correr `make docker-compose-down`. Se pueden ver los logs correspondientes a la finalización de los recursos con `docker-compose-logs` y su posterior graceful shutdown.

Si es necesario más tiempo para la detención de los contenedores, se puede correr el comando

```bash
docker-compose -f docker-compose-dev.yaml down -t <tiempo>
```

Para este ejercicio se decidió cerrar los sockets de los clientes y servidores de forma _graceful_. De manera que las siguientes operaciones en curso terminen o fallen de forma controlada.

### Ejercicio N°5:

Para ejecutar el programa se debe correr `make-docker-compose-up` que levantará una imagen con un apostor ya definido en docker-compose-dev.yaml y luego `make-docker-compose-logs` para ver los logs respectivos a la apuesta enviada y almacenada. Se debería ver parecido a lo siguiente:

```bash
docker compose -f docker-compose-dev.yaml logs -f
server  | 2025-03-19 17:56:31 INFO     action: accept_connections | result: in_progress
server  | 2025-03-19 17:56:31 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server  | 2025-03-19 17:56:31 INFO     action: apuesta_almacenada | result: success | dni: 30904465 | numero: 2201
server  | 2025-03-19 17:56:31 INFO     action: accept_connections | result: in_progress
client1  | 2025-03-19 17:56:31 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: INFO
client1  | 2025-03-19 17:56:31 INFO     action: apuesta_enviada | result: success | dni: 30904465 | numero: 2201
```

Además se puede ver el archivo `bets.csv` que guarda el servidor usando el comando `docker exec -it server bash` y luego `cat bets.csv`.

El protocolo de comunicación implementado es el siguiente. Para el tipo de conexión se utilizó TCP para la comunicación confiable y orientada a la conexión. Para el formato de los mensajes se utilizó el formato JSON, y de forma manual su respectiva serialización y deserialización. Además se consideró los casos en los que pueda haber un error en donde el servidor recibe un mensaje mal formado o que no cumple con el protocolo, en estos casos el servidor envía un simple mensaje de error al cliente y cierra su conexión con el mismo.

### Ejercicio N°6:

Para ejecutar el programa se debe generar un archivo docker compose con hasta 5 clientes o dejar el `docker-compose-dev.yaml` por defecto, luego correr `make-docker-compose-up` y `make-docker-compose-logs` para ver los logs respectivos de las apuestas tanto en el cliente como en el servidor. En el server, si salió todo de forma correcta, se verá algo parecido a lo siguiente:

```bash
server   | 2025-03-20 13:48:42 INFO     action: apuesta_recibida | result: success | cantidad: 9238
```

En el cliente, se podrá ver

```bash
client4  | 2025-03-20 13:48:42 INFO     action: wait_for_stats | result: success | stats: Se recibieron correctamente 9238 de 9238 apuestas
```

Se podrá observar si se ejecuta en bash en el servidor las apuestas guardadas en el archivo `bets.csv` con el comando `cat bets.csv`.

Sobre posibles errores que ocurran por envíos incorrectos de algunas apuestas dentro del batch, se decidió descartar aquellas incorrectas, pero persistir las correctas. Por eso es que el servidor responde cuántas apuestas recibió correctamente del total.

Si se desea observar el tamaño de los chunks y la cantidad de apuestas que se envían en cada uno, se puede bajar el nivel de log a `DEBUG`, donde se debería ver algo parecido a lo siguiente:

```bash
client1  | 2025-03-20 14:11:18 DEBUG     action: send_batch | batch size: 3026 | bets_sent: 23
```

La forma en la que el servidor sabe cuándo el cliente envió todos los batches es a través del mensaje de finish que envía el cliente al finalizar con todos los envíos. 

El protocolo de comunicación implementado es el siguiente. Para el tipo de conexión se utilizó TCP para la comunicación confiable y orientada a la conexión. Para el formato de los mensajes se utilizó el formato CSV, ya que primeramente se quiso utilizar JSON, pero debido al overhead que trae la serialización de keys-values se decidió implementar un simple CSV y de forma manual su respectiva serialización y deserialización. Además se consideró los casos en los que pueda haber un error en donde el servidor recibe un mensaje mal formado o que no cumple con el protocolo, en estos casos el servidor envía un simple mensaje de error al cliente y cierra su conexión con el mismo.

### Ejercicio N°7:

La forma en la que el cliente notifica la finalización de envío de apuestas es a través de un simple mensaje "finish" al servidor, es aprovechado este mensaje porque quiere decir también que se enviaron todos los batches. Como la acción posterior a esta es la consulta de lista de ganadores, se lo toma como implícito y el cliente sólo espera los resultados.
En el servidor, se espera a que todos los clientes envíen sus apuestas. Cuando esto sucede se procede a realizar el sorteo y se responde a las consultas de los clientes.

Para ejecutar el programa se debe correr `make docker-compose-up` y posteriormente podemos ver los logs con `make docker-compose-logs`. En resumen se tendría que observar entre los logs:

```bash
server   | 2025-03-23 18:37:37 INFO     action: notify_winners | result: success | agency: 4 | winners: 35635602,34963649
server   | 2025-03-23 18:37:37 INFO     action: notify_winners | result: success | agency: 3 | winners: 28188111,23328212,22737492
server   | 2025-03-23 18:37:37 INFO     action: notify_winners | result: success | agency: 1 | winners: 24807259,30876370
server   | 2025-03-23 18:37:37 INFO     action: notify_winners | result: success | agency: 2 | winners: 24813860,31660107,33791469
server   | 2025-03-23 18:37:37 INFO     action: notify_winners | result: success | agency: 5 | winners: 
server   | 2025-03-23 18:37:37 INFO     action: notify_winners | result: success
client1  | 2025-03-23 18:37:37 INFO     action: consulta_ganadores | result: success | cant_ganadores: 2
client2  | 2025-03-23 18:37:37 INFO     action: consulta_ganadores | result: success | cant_ganadores: 3
client3  | 2025-03-23 18:37:37 INFO     action: consulta_ganadores | result: success | cant_ganadores: 3
client4  | 2025-03-23 18:37:37 INFO     action: consulta_ganadores | result: success | cant_ganadores: 2
client5  | 2025-03-23 18:37:37 INFO     action: consulta_ganadores | result: success | cant_ganadores: 0
```

### Ejercicio N°8:

Para este ejercicio se probó usar async, pero debido a que el código cambiaba mucho entre lo que teníamos y lo que se necesitaba, se decantó en usar threads o multiprocessing. Con threads iba a ser la solución más sencilla, ya que el proceso de sincroniazción era mediante joins, pero ya que he trabajado en el pasado con threads, por mera razón académica decidí usar multiprocessing. Aclaración: no hay razón alguna por la que crea que multiprocessing es mejor que multithreading para este ejercicios, de hecho creo que es mejor multithreading porque hay operaciones de I/O y por como funciona el intérprete de Python, creo que sería mejor usar threads.

Debido al uso de multiprocessing, como mecanismo de sincronización se usaron barriers, para que los procesos esperen a que todas las apuestas de todos los clientes fueran enviadas, creando un proceso por cada cliente y usando un barrier para determinar cuando se recibieron correctamente todas las apuestas de los clientes. Luego cada proceso avisaría a su respectivo cliente.
Lo más importante a destacar de la solución es cuándo se crean los procesos, que es luego de hacer el bind. Esto se hizo solamente por simplicidad, ya que el SO maneja los procesos como una cola FIFO, y permite así que por cada cliente que se conecte, se cree un proceso sea el encargado de aceptarlo (lo hablamos un poco al final de la clase del martes con el profe Pablo). Se podría crear procesos después de aceptar la conexión, pero lo primero hace que sea más sencillo el código.

La ejecución es la misma que en el ejercicio 7.
