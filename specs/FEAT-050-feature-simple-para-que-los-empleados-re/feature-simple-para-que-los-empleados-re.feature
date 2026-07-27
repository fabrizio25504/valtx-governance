# language: es
Característica: Registro y consulta de solicitudes de vacaciones
  Como un empleado
  Quiero registrar y consultar mis solicitudes de vacaciones
  Para gestionar mis tiempos de descanso de manera simple

  @REQ-VAC-001
  Escenario: Registro de nueva solicitud de vacaciones con consentimiento
    Dado que el usuario "empleado01" ha brindado su consentimiento previo y expreso
    Cuando el usuario "empleado01" envía una solicitud de vacaciones con fecha de inicio "2023-12-01", fecha de fin "2023-12-15" y motivo "Vacaciones anuales"
    Entonces el sistema registra la solicitud con estado "pendiente"
    Y el sistema almacena el consentimiento demostrable con timestamp y versión de política

  @REQ-VAC-002
  Escenario: Bloqueo de acceso a solicitud de vacaciones por usuario no autorizado
    Dado que existe una solicitud de vacaciones registrada por el usuario "empleado01"
    Y el usuario "otro_empleado" no es el solicitante ni el jefe directo
    Cuando el usuario "otro_empleado" intenta visualizar la solicitud
    Entonces el sistema bloquea el acceso al registro de la solicitud

  @REQ-VAC-003
  Escenario: Consulta de historial de solicitudes del empleado
    Dado que el usuario "empleado01" tiene solicitudes de vacaciones registradas con consentimiento previo
    Cuando el usuario "empleado01" consulta el listado de sus solicitudes
    Entonces el sistema muestra el historial de solicitudes con su estado actual (pendiente, aprobado, rechazado)
