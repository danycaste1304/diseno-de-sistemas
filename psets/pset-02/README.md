# PSet 2 — ReservaU

La carpeta `implementacion/` extiende en Python la implementación del PSet 1,
copiada aquí para mantener el PSet 1 intacto. Esta entrega cubre la parte 4:
implementación con patrones y concurrencia. No requiere servidor, base de
datos, interfaz gráfica, API ni pruebas automatizadas.

Para ejecutar la simulación:

```bash
cd implementacion
python simulacion.py
```

También se puede ejecutar con Docker desde `implementacion/`:

```bash
docker build -t reservau-v2 .
docker run --rm reservau-v2
```

## Estructura de los módulos

- `modelos.py`: usuarios, canchas, disponibilidad, reservas y administración.
- `reglas.py`: Singleton de configuración y estrategias de prioridad y
  cancelación.
- `patrones.py`: creadores de reservas, fábricas de sede, Builder y Prototype.
- `facade.py`: coordinación de los subsistemas y operaciones principales.
- `simulacion.py`: los escenarios ejecutables, con mensajes impresos en el
  orden del flujo.

Los patrones conservan la forma introductoria de los laboratorios: interfaces
abstractas para estrategias, fábricas y creadores; métodos encadenables en el
Builder; una fábrica que entrega productos relacionados; y una Facade que
coordina las operaciones del cliente.

## Tabla de patrones

| Patrón | Requerimiento que lo justifica | Problema que resuelve | Clases y métodos |
|---|---|---|---|
| Factory Method | RF-02, RF-03 | Centraliza la selección del tipo de reserva según el solicitante y asigna desde su creador la política de cancelación. | `FabricaReservas.elegir_creador()`, `CreadorReservaRegular.crear_reserva()`, `CreadorReservaEquipoOficial.crear_reserva()` |
| Abstract Factory | RF-21, RF-22 | Mantiene juntos el validador y el notificador de una sede para evitar usar productos de sedes distintas. | `FabricaSedeNorte.crear_servicios()`, `FabricaSedeSur.crear_servicios()`, `ServiciosSede` |
| Builder | RF-16, RF-18 | Construye una reserva recurrente con cuatro datos obligatorios y opciones para semanas, equipo y notas. | `ReservaRecurrenteBuilder.para_cancha()`, `desde()`, `con_franja()`, `solicitada_por()`, `por_semanas()`, `con_equipo_prestado()`, `con_notas()`, `construir()` |
| Prototype | RF-19, RF-20 | Reutiliza una plantilla de bloqueo para varias canchas y fechas, manteniendo independiente el equipo mutable de cada clon. | `Bloqueo.clonar_para()` |
| Singleton | RNF-16 | Proporciona una sola fuente para los umbrales de prioridad, cancelación y suspensión. | `ConfiguracionTecnologia.obtener_instancia()` |
| Strategy | RF-04, RF-05, RF-08, RF-13, RF-23 | Separa la prioridad y las tres políticas de cancelación de la clase `Reserva`. | `EstrategiaPrioridad.tiene_prioridad()`, `PrioridadAntes18`, `SinPrioridad`, `CancelacionEstudiante.cancelar()`, `CancelacionCapitan.cancelar()`, `CancelacionAdministrativa.cancelar()`, `Reserva.cancelar()` |
| Facade | RF-02, RF-04, RF-07, RF-13, RF-17, RF-20, RF-24, RF-26, RF-27 | Coordina las validaciones, disponibilidad, calendario, registros administrativos/no-shows y notificaciones desde una entrada única. | `ReservaFacade.reservar()`, `reservar_en_competencia()`, `reservar_recurrente()`, `cancelar()`, `bloquear()` |
| Concurrencia: locking pesimista | RF-17, RNF-05, RNF-09, RNF-14 | Hace atómica la verificación y confirmación de una franja o serie para evitar reservas duplicadas y cambios parciales. | `Cancha._lock`, `Cancha.tiene_reserva_en()`, `Cancha.tiene_bloqueo_en()`, `Disponibilidad.confirmar_si_disponible()`, `confirmar_varias()` |

### Trazabilidad de extremo a extremo

| Requerimiento | Caso de uso | Diagrama | Patrón o decisión | Clase / método | Simulación |
|---|---|---|---|---|---|
| RF-02, RF-03 | Reservar una cancha; reservar de forma recurrente | Flujos 05 y 08 | Factory Method | `FabricaReservas.crear_reserva()` | `[1.3]`, `[3.7]` |
| RF-21, RF-22 | Reservar una cancha; bloquear canchas para un evento | Flujos 05 y 13 | Abstract Factory | `FabricaSedeNorte.crear_servicios()`, `FabricaSedeSur.crear_servicios()` | `[1.3]`, `[1.6]`, `[2.2]`, `[6.6]` |
| RF-16, RF-18 | Reservar de forma recurrente | Flujo 08; diagrama de actividad | Builder | `ReservaRecurrenteBuilder.construir()` | `[3.1]`–`[3.11]` |
| RF-19, RF-20 | Bloquear canchas para un evento | Flujos 13 y 14 | Prototype | `Bloqueo.clonar_para()` | `[6.1]`–`[6.10]` |
| RNF-16, RF-10 | Reservar con prioridad; cancelar una reserva | Flujos 06 y 07 | Singleton | `ConfiguracionTecnologia.obtener_instancia()` | `[2.5]`–`[2.10]`, `[5.10]` |
| RF-04, RF-05, RF-08, RF-23 | Reservar con prioridad; cancelar una reserva | Flujos 06 y 07; máquina de estados | Strategy | `PrioridadAntes18.tiene_prioridad()`, `Reserva.cancelar()` | `[2.5]`–`[2.10]`, `[4.2]`–`[4.8]` |
| RF-02, RF-07, RF-16, RF-19, RF-24, RF-26, RF-27 | Reservar una cancha; reservar de forma recurrente; cancelar una reserva; bloquear canchas para un evento | Flujos 05, 07, 08 y 13; robustez | Facade | `ReservaFacade.reservar()`, `reservar_recurrente()`, `cancelar()`, `bloquear()`, `Administrador.registrar_accion()` | `[1]`–`[7]` |
| RF-17, RNF-05, RNF-09 | Reservar una cancha; reservar de forma recurrente | Flujos 05 y 08; diagrama de actividad | Locking pesimista | `ReservaFacade.reservar()`, `reservar_recurrente()`, `Cancha._lock`, `Estudiante.registrar_no_show()` | `[3.10]`–`[3.11]`, `[7]` |

Los números de flujo remiten a `DiagramasFlujo_PSet2.pdf`. Las etiquetas entre
corchetes remiten a la salida de `simulacion.py`.

**Prototype.** La Facade clona una plantilla `Bloqueo` por cada cancha y fecha.
Se usa `copy.deepcopy` porque `equipo_prestado` es una lista mutable: agregar
equipo a un clon no debe cambiar la plantilla ni otro clon. La simulación lo
muestra en el escenario 6.

**Singleton.** `ConfiguracionTecnologia` mantiene una instancia compartida con
la hora límite de prioridad, las ventanas de cancelación y los límites de
suspensión. Esto permite que prioridad, cancelación y suspensión lean los mismos
valores; el costo es aceptar estado global compartido y controlar quién lo
modifica.

La prioridad de RF-04 se aplica cuando la Facade recibe un lote explícito de
solicitudes para una misma cancha y franja mediante
`ReservaFacade.reservar_en_competencia()`: consulta la Strategy con la hora de
cada solicitud y prueba primero las solicitudes con prioridad antes de las 18:00.
Una reserva individual sin rival válido puede confirmarse a cualquier hora
dentro del horario de su sede.

Para RF-24, `ReservaFacade.reservar()` calcula el tiempo transcurrido desde
`seleccion_en` y rechaza una selección que supere 15 minutos, liberando una
retención temporal vencida. La salida `[2.11]`–`[2.12]` muestra ese rechazo.

### Si se quitara cada patrón

| Patrón o decisión | ¿Qué volvería a aparecer? | Escenario visible |
|---|---|---|
| Factory Method | Un `if` por tipo de solicitante, repetido en reserva única y recurrente, para escoger clase y política de cancelación. | 1, 3 y 4 |
| Abstract Factory | La selección manual de validador y notificador, con riesgo de mezclar sedes. | 1 y 2 |
| Builder | Un constructor largo y comprobaciones de campos obligatorios dispersas para cada serie. | 3 |
| Prototype | La reconstrucción manual del bloqueo por cancha y fecha y la copia manual de su lista de equipo. | 6 |
| Singleton | Copias separadas de los valores de prioridad, cancelación y suspensión que podrían diferir. | 2, 4 y 5 |
| Strategy | Condicionales de prioridad y de plazo o tipo de cancelación dentro de las entidades o la Facade. | 2 y 4 |
| Facade | La coordinación repetida de validación, disponibilidad, calendario, registros y avisos en el cliente. | 1 a 7 |
| Locking pesimista | La carrera entre comprobar una franja y confirmarla, que permitiría dos reservas o una serie parcial. | 3 y 7 |

### Recorrido de los tres no-shows

1. **Requerimiento:** RF-09 lleva el conteo por mes calendario, RF-10 ordena
   suspender durante siete días al tercer no-show y RF-11 impide reservar durante
   la suspensión. La cancelación tardía que genera el no-show se define en
   RF-08 para estudiantes y RF-23 para capitanes; RNF-16 reúne los umbrales.
2. **Caso de uso y diagramas:** *Cancelar una reserva* sigue el flujo 07 de
   `DiagramasFlujo_PSet2.pdf` y el diagrama de robustez de cancelación. La
   máquina de estados muestra el paso de reserva activa a `NO_SHOW`. El intento
   posterior de reservar vuelve al caso *Reservar una cancha* (flujo 05).
3. **Patrón y métodos:** Factory Method asigna la Strategy de cancelación al
   crear la reserva. `ReservaFacade.cancelar()` delega en
   `Reserva.cancelar()`; `CancelacionEstudiante.cancelar()` aplica las dos horas
   y marca el estado `NO_SHOW`. Después, `RegistroNoShows.registrar()` llama a
   `Estudiante.registrar_no_show()`, que cuenta los registros del mismo mes y
   crea una `Suspension`. `ReservaFacade.reservar()` consulta
   `Estudiante.esta_suspendido()` para rechazar la nueva solicitud.
4. **Configuración:** `ConfiguracionTecnologia.obtener_instancia()` proporciona
   `no_shows_para_suspension = 3` y `dias_suspension = 7`; la política de
   cancelación lee `horas_cancelacion_estudiante = 2`.
5. **Salida:** las líneas etiquetadas `[5.8]`, `[5.9]` y `[5.10]` muestran los
   conteos 1, 2 y 3; `[5.10]` informa la suspensión de siete días y `[5.11]`
   muestra el rechazo de una reserva posterior.

## Concurrencia

Se usa locking pesimista por cancha (`threading.RLock`) y por disponibilidad
(`threading.Lock`). La verificación de reservas o bloqueos superpuestos y el
registro de la reserva ocurren bajo el lock de la cancha; la disponibilidad
también protege su propio cambio de estado. Cada solicitante tiene un `RLock`
para que el conteo del tercer no-show y la suspensión sean una sola operación.
Así, dos solicitudes simultáneas por la misma cancha y franja no pueden
confirmar ambas. ReservaU tiene muchas
consultas y menos reservas; cada consulta mantiene el lock solo durante una
lectura breve, y las escrituras esperan durante la sección crítica. Se acepta
esa espera acotada en los picos de inicio de semestre a cambio de una solución
directa sin reintentos ni control de versiones.

## Correcciones de PSet 1 aplicadas en esta copia

La condición horaria se movió a `EstrategiaPrioridad`; `Estudiante` ya no
incluye un `if` que consulte directamente la hora. El plazo de dos horas dejó
de vivir en `Estudiante.cancelar_reserva`: `Reserva` delega en la estrategia de
cancelación correspondiente.
