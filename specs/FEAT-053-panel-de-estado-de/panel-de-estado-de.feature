# language: es
Característica: Panel de estado de consentimiento del titular
  Como titular de datos
  Quiero consultar y revocar mi consentimiento desde un panel
  Para tener control sobre mis datos personales y su tratamiento

  @REQ-PAN-001
  Escenario: Consulta del estado de consentimiento vigente
    Dado un empleado con cuenta "user123" que tiene un consentimiento vigente
    Cuando solicita el resumen de su consentimiento
    Entonces el sistema devuelve un resumen con el estado "vigente"
    Y la fecha de otorgamiento "2023-01-15"
    Y los canales aceptados ["email", "sms"]

  @REQ-PAN-002
  Escenario: Revocación del consentimiento de marketing
    Dado un empleado con cuenta "user123" que tiene un consentimiento vigente para marketing
    Cuando revoca el consentimiento de marketing desde su perfil
    Entonces el sistema actualiza el estado del consentimiento a "revocado"
    Y registra la acción de revocación con cifrado en el almacenamiento

  @REQ-PAN-003
  Escenario: Cifrado de registros de consentimiento en almacenamiento
    Dado un sistema que almacena registros de consentimiento
    Cuando se guarda un nuevo registro de consentimiento o revocación
    Entonces el sistema persiste el registro aplicando cifrado en reposo

  @REQ-PAN-004
  Escenario: Minimización de datos capturados en el panel
    Dado un empleado que accede al panel de consentimiento
    Cuando el sistema procesa la solicitud de visualización
    Entonces el sistema captura unicamente la cuenta y el estado del canal de marketing
