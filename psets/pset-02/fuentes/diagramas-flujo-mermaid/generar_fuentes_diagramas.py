from pathlib import Path
from textwrap import dedent

OUT = Path(__file__).parent

DIAGRAMAS = {
"01_registrarse": '''flowchart TD
A([Actor principal: Estudiante]) --> P[/Precondiciones:<br/>Email y contraseña disponibles.<br/>No existe cuenta con ese email./] --> S1[1. El estudiante selecciona Registrarse] --> S2[2. El sistema solicita datos] --> S3[3. El estudiante ingresa nombre, email y contraseña] --> D4{4. ¿Datos válidos y email no registrado?}
D4 -->|No| A4a[4a. El sistema informa datos inválidos o email duplicado] --> F1([Fin])
D4 -->|Sí| S5[5. El sistema crea la cuenta] --> S6[6. El sistema confirma el registro] --> F2([Fin: estudiante registrado])
''',
"02_iniciar_sesion": '''flowchart TD
A([Actor principal: Usuario<br/>Estudiante, Capitán o Administrador]) --> P[/Precondiciones:<br/>El usuario tiene una cuenta registrada./] --> S1[1. El usuario selecciona Iniciar sesión] --> S2[2. El sistema solicita email y contraseña] --> S3[3. El usuario ingresa credenciales] --> D4{4. ¿Credenciales correctas?}
D4 -->|No| A4a[4a. El sistema informa credenciales inválidas] --> F1([Fin])
D4 -->|Sí| S5[5. El sistema autentica al usuario] --> S6[6. El sistema muestra opciones según el rol] --> F2([Fin: sesión iniciada])
''',
"03_consultar_disponibilidad": '''flowchart TD
A([Actor principal: Estudiante<br/>El Capitán participa por herencia]) --> P[/Precondiciones:<br/>El estudiante está autenticado./] --> S1[1. El estudiante selecciona Consultar disponibilidad] --> S2[2. El estudiante ingresa sede, cancha o fecha] --> S3[3. El sistema consulta horarios, reservas y bloqueos] --> D4{4. ¿Existen franjas disponibles?}
D4 -->|No| A4a[4a. El sistema informa que no existen franjas disponibles] --> F1([Fin])
D4 -->|Sí| S5[5. El sistema muestra franjas disponibles] --> F2([Fin: disponibilidad consultada])
''',
"04_consultar_mis_reservas": '''flowchart TD
A([Actor principal: Estudiante<br/>El Capitán participa por herencia]) --> P[/Precondiciones:<br/>El estudiante está autenticado./] --> S1[1. El estudiante selecciona Consultar mis reservas] --> S2[2. El sistema busca sus reservas] --> D3{3. ¿Existen reservas registradas?}
D3 -->|No| A3a[3a. El sistema informa que no existen reservas] --> F1([Fin])
D3 -->|Sí| S4[4. El sistema muestra fecha, cancha, franja y estado] --> F2([Fin: reservas consultadas])
''',
"05_reservar_una_cancha": '''flowchart TD
A([Actor principal: Estudiante<br/>El Capitán participa por herencia]) --> P[/Precondiciones:<br/>Autenticado; cancha, fecha y franja seleccionadas./] --> S1[1. El solicitante pide reservar cancha, fecha y franja] --> D2{2. ¿Han pasado 15 minutos o menos desde la selección?}
D2 -->|No| A2a[2a. El sistema cancela el proceso y deja libre la franja] --> F1([Fin: tiempo agotado])
D2 -->|Sí| S3[3. El sistema valida suspensión] --> D4{4. ¿El solicitante está suspendido?}
D4 -->|Sí| A4a[4a. El sistema rechaza e informa la suspensión] --> F2([Fin])
D4 -->|No| S5[5. El sistema valida el horario de la sede] --> D6{6. ¿Horario permitido?}
D6 -->|No| A6a[6a. El sistema rechaza e informa el horario permitido] --> F3([Fin])
D6 -->|Sí| S7[7. El sistema aplica la estrategia de prioridad si hay solicitudes concurrentes] --> D8{8. ¿La solicitud conserva la prioridad?}
D8 -->|No| A8a[8a. El sistema rechaza e informa la prioridad] --> F4([Fin])
D8 -->|Sí| S9[9. El creador prepara la reserva con su política de cancelación] --> S10[10. El sistema verifica disponibilidad y registra de forma atómica] --> D11{11. ¿La franja estaba disponible?}
D11 -->|No| A11a[11a. El sistema rechaza la reserva sin ocupar la franja] --> F5([Fin])
D11 -->|Sí| S12[12. El sistema notifica por el canal de la sede] --> F6([Fin: reserva confirmada])
''',
"06_reservar_con_prioridad": '''flowchart TD
A([Actor principal: Capitán]) --> P[/Precondiciones:<br/>Autenticado, no suspendido y con solicitudes concurrentes; se considera la hora de la solicitud./] --> S1[1. El capitán selecciona cancha, fecha y franja] --> S2[2. El sistema identifica solicitudes concurrentes] --> D3{3. ¿El momento de la solicitud está antes de la hora límite configurada?}
D3 -->|No| A3a[3a. El sistema procesa con política regular] --> S7
D3 -->|Sí| S4[4. El sistema verifica prioridad vigente] --> D5{5. ¿El capitán tiene prioridad?}
D5 -->|No| A5a[5a. El sistema procesa con política regular] --> S7
D5 -->|Sí| S6[6. El sistema selecciona la solicitud prioritaria] --> S7[7. El sistema valida disponibilidad] --> D8{8. ¿Puede confirmarse?}
D8 -->|No| A8a[8a. El sistema rechaza e informa el motivo] --> F1([Fin])
D8 -->|Sí| S9[9. El sistema confirma la reserva y notifica resultados] --> F2([Fin: prioridad procesada])
''',
"07_cancelar_una_reserva": '''flowchart TD
A([Actor principal: Estudiante<br/>El Capitán participa por herencia]) --> P[/Precondiciones:<br/>Autenticado; reserva propia ACTIVA, identificada y aún no iniciada./] --> S1[1. El solicitante pide cancelar su reserva] --> S2[2. El sistema verifica propiedad y estado] --> D3{3. ¿La reserva puede cancelarse?}
D3 -->|No| A3a[3a. El sistema rechaza e informa el motivo] --> F1([Fin])
D3 -->|Sí| S4[4. La estrategia obtiene de la configuración el plazo de 2 h o 24 h] --> D5{5. ¿Se cumple el plazo antes del inicio?}
D5 -->|Sí| S6[6. La reserva pasa a CANCELADA, registra fecha y libera la franja] --> S7[7. El sistema registra la cancelación y notifica] --> F2([Fin: cancelación regular])
D5 -->|No| A5a[5a. La reserva pasa a NO_SHOW, registra fecha y libera la franja] --> A6a[6a. El estudiante registra y cuenta los no-shows del mes] --> D7a{7a. ¿Alcanzó el límite de 3 no-shows configurado?}
D7a -->|Sí| A8a[8a. El estudiante crea una suspensión de 7 días] --> A9a[9a. El sistema notifica no-show y suspensión] --> F3([Fin: no-show registrado])
D7a -->|No| A8b[8b. El sistema notifica el no-show] --> F3
''',
"08_reservar_recurrente": '''flowchart TD
A([Actor principal: Capitán]) --> P[/Precondiciones:<br/>Cancha, fecha inicial y franja seleccionadas; número de semanas opcional./] --> S1[1. El capitán ingresa los datos obligatorios y, si desea, semanas, equipo y notas] --> D2{2. ¿La serie comprende de 2 a 8 semanas?}
D2 -->|No| A2a[2a. El sistema rechaza e informa el rango permitido] --> F1([Fin])
D2 -->|Sí| S3[3. El sistema valida rol, autenticación, suspensión, cancha y sede] --> D4{4. ¿Cumple las condiciones iniciales?}
D4 -->|No| A4a[4a. El sistema rechaza sin registrar reservas] --> F2([Fin])
D4 -->|Sí| S5[5. El sistema genera las fechas semanales tentativas] --> S6[6. Por cada semana valida horario de sede, disponibilidad y prioridad] --> D7{7. ¿Todas las semanas son válidas?}
D7 -->|No| A7a[7a. El sistema informa la primera semana en conflicto y descarta toda la serie] --> F3([Fin])
D7 -->|Sí| S8[8. El sistema confirma de forma atómica todas las semanas] --> S9[9. El sistema guarda equipo y notas y notifica] --> F4([Fin: serie confirmada])
''',
"09_validar_disponibilidad_semanal": '''flowchart TD
A([Actor principal: Capitán<br/>Invoca este flujo desde Reservar de forma recurrente]) --> P[/Precondiciones:<br/>Existe una serie tentativa de 2 a 8 fechas, con cancha y franja identificadas./] --> S1[1. El capitán envía la solicitud recurrente] --> S2[2. El sistema toma la primera semana pendiente] --> S3[3. El sistema consulta reservas y bloqueos] --> D4{4. ¿La cancha está disponible?}
D4 -->|No| A4a[4a. El sistema registra la primera semana en conflicto y detiene la validación] --> F1([Fin: serie no disponible])
D4 -->|Sí| S5[5. El sistema avanza a la siguiente semana] --> D6{6. ¿Quedan semanas por validar?}
D6 -->|Sí| S3
D6 -->|No| S7[7. El sistema devuelve disponibilidad completa] --> F2([Fin: disponibilidad validada])
''',
"10_gestionar_horarios": '''flowchart TD
A([Actor principal: Administrador]) --> P[/Precondiciones:<br/>Administrador autenticado y cancha identificada./] --> S1[1. El administrador selecciona una cancha] --> S2[2. El sistema muestra horarios y estado actuales] --> S3[3. El administrador ingresa el nuevo horario o habilitación] --> D4{4. ¿El horario es válido?}
D4 -->|No| A4a[4a. El sistema informa hora de inicio o fin inválida] --> F1([Fin])
D4 -->|Sí| S5[5. El sistema actualiza horarios o habilitación] --> S6[6. El sistema registra la modificación] --> S7[7. El sistema confirma la actualización] --> F2([Fin: horario gestionado])
''',
"11_asignar_prioridad": '''flowchart TD
A([Actor principal: Administrador]) --> P[/Precondiciones:<br/>Administrador autenticado y estudiante registrado identificado./] --> S1[1. El administrador selecciona al estudiante] --> S2[2. El sistema verifica que exista y esté activo] --> D3{3. ¿Puede recibir prioridad de capitán?}
D3 -->|No| A3a[3a. El sistema rechaza e informa el motivo] --> F1([Fin])
D3 -->|Sí| S4[4. El administrador ingresa el equipo oficial] --> S5[5. El sistema asigna rol de Capitán y prioridad] --> S6[6. El sistema registra la modificación] --> S7[7. El sistema confirma la asignación] --> F2([Fin: prioridad asignada])
''',
"12_anular_una_reserva": '''flowchart TD
A([Actor principal: Administrador]) --> P[/Precondiciones:<br/>Administrador autenticado, reserva activa identificada y motivo disponible./] --> S1[1. El administrador selecciona la reserva e ingresa el motivo] --> S2[2. El sistema verifica que exista y esté CONFIRMADA] --> D3{3. ¿La reserva puede anularse?}
D3 -->|No| A3a[3a. El sistema rechaza e informa el motivo] --> F1([Fin])
D3 -->|Sí| S4[4. El sistema cambia el estado a ANULADA] --> S5[5. El sistema registra fecha, hora, administrador y motivo] --> D6{6. ¿Existe bloqueo vigente para la franja?}
D6 -->|Sí| A6a[6a. El sistema conserva la franja BLOQUEADA] --> S8
D6 -->|No| S7[7. El sistema libera la disponibilidad] --> S8[8. El sistema notifica al solicitante] --> S9[9. El sistema registra la acción administrativa] --> F2([Fin: reserva anulada sin penalización])
''',
"13_bloquear_canchas_evento": '''flowchart TD
A([Actor principal: Administrador]) --> P[/Precondiciones:<br/>Administrador autenticado; canchas, fechas, franja y motivo identificados.<br/>Equipo de montaje opcional./] --> S1[1. El administrador ingresa datos del evento] --> S2[2. El sistema valida los datos] --> D3{3. ¿Los datos son válidos?}
D3 -->|No| A3a[3a. El sistema rechaza e informa datos inválidos] --> F1([Fin])
D3 -->|Sí| S4[4. El sistema crea una plantilla de bloqueo] --> S5[5. El sistema replica el bloqueo por cancha y fecha] --> S6[6. El sistema busca reservas CONFIRMADAS en conflicto] --> D7{7. ¿Existen reservas en conflicto?}
D7 -->|Sí| A7a[7a. El sistema anula cada reserva y registra cada anulación, sin no-show] --> A8a[8a. El sistema mantiene las franjas BLOQUEADAS] --> A9a[9a. El sistema registra la creación del bloqueo] --> A10a[10a. El sistema notifica a solicitantes afectados] --> S11
D7 -->|No| S8[8. El sistema marca las franjas BLOQUEADAS] --> S9[9. El sistema registra la creación del bloqueo] --> S11[11. El sistema confirma los bloqueos] --> F2([Fin: bloqueos registrados])
''',
"14_anular_reservas_conflicto": '''flowchart TD
A([Actor principal: Administrador<br/>El flujo se activa desde Bloquear canchas para un evento]) --> P[/Precondiciones:<br/>Existe un bloqueo válido y al menos una reserva CONFIRMADA en conflicto./] --> S1[1. El administrador confirma la creación del bloqueo] --> S2[2. El sistema identifica una reserva en conflicto] --> D3{3. ¿La reserva continúa CONFIRMADA?}
D3 -->|No| A3a[3a. El sistema omite la reserva] --> S7
D3 -->|Sí| S4[4. El sistema cambia el estado a ANULADA] --> S5[5. El sistema registra el bloqueo como causa] --> S6[6. El sistema mantiene la franja BLOQUEADA] --> S7[7. El sistema revisa si existen más reservas en conflicto] --> D8{8. ¿Existen más reservas?}
D8 -->|Sí| S2
D8 -->|No| S9[9. El sistema notifica a los solicitantes afectados] --> F1([Fin: conflictos anulados])
''',
"15_notificar_solicitante": '''flowchart TD
A([Actor principal: Sistema ReservaU<br/>Proceso automático]) --> P[/Precondiciones:<br/>Existe una reserva confirmada, cancelada, anulada o con no-show.<br/>Sede y solicitante identificados./] --> S1[1. El sistema obtiene la sede de la cancha] --> S2[2. El sistema identifica el canal de notificación] --> D3{3. ¿La sede es Campus Norte?}
D3 -->|Sí| S4[4. El sistema envía correo institucional] --> S6
D3 -->|No| A3a[3a. El sistema envía mensaje de texto para Campus Sur] --> S6[6. El sistema registra el envío] --> F1([Fin: solicitante notificado])
''',
}

OUT.mkdir(parents=True, exist_ok=True)
for nombre, contenido in DIAGRAMAS.items():
    (OUT / f"{nombre}.mmd").write_text(dedent(contenido).strip() + "\n", encoding="utf-8")
print(f"Se escribieron {len(DIAGRAMAS)} fuentes Mermaid en {OUT}")
