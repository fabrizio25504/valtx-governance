# language: es
Característica: Calendario interno de eventos
  Como un organizador o empleado
  Quiero gestionar e inscribirme en eventos internos
  Para participar en actividades de la empresa

  @REQ-EVT-001
  Escenario: Crear un evento interno
    Dado que un organizador accede al formulario de creación de eventos
    Cuando ingresa el titulo, descripcion, fecha, hora y lugar del evento
    Entonces el sistema registra el nuevo evento en el calendario

  @REQ-EVT-002
  Escenario: Registro de consentimiento al inscribirse
    Dado que un empleado desea inscribirse en un evento abierto
    Cuando completa el formulario de inscripcion y acepta el consentimiento
    Entonces el sistema registra el consentimiento previo, expreso y demostrable con timestamp y version de politica

  @REQ-EVT-003
  Escenario: Captura minimizada de datos en el formulario
    Dado que un empleado esta completando el formulario de inscripcion
    Cuando envia sus datos para inscribirse
    Entonces el sistema captura unicamente los campos necesarios: nombre, area y correo corporativo

  @REQ-EVT-004
  Escenario: Cancelacion de inscripcion
    Dado que un empleado tiene una inscripcion activa en un evento
    Cuando cancela su inscripcion
    Entonces el sistema actualiza el estado del registro manteniendo la trazabilidad de quien se inscribio y cuando

  @REQ-EVT-005
  Escenario: Visualizacion de inscritos por el organizador
    Dado que un organizador tiene eventos creados con inscripciones
    Cuando solicita ver la lista de inscritos
    Entonces el sistema muestra los registros de los eventos propios para el control de aforo

  @REQ-EVT-006
  Escenario: Purga automatica de datos de inscripcion
    Dado que un evento ha finalizado hace 90 dias
    Cuando se ejecuta la purga automatica de datos
    Entonces el sistema elimina los datos de inscripcion asociados al evento
