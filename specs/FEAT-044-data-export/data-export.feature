# language: es
# Cada Scenario etiquetado con su REQ. El gate de cobertura exige 100%.

Característica: Exportación de datos personales (portabilidad)

  @REQ-EXP-001
  Escenario: Generar la exportación estructurada
    Dado un usuario con datos personales registrados
    Cuando solicita exportar sus datos
    Entonces el sistema genera un archivo JSON con sus datos personales

  @REQ-EXP-002
  Escenario: Responder dentro del plazo legal
    Dada una solicitud de exportación registrada hoy
    Cuando se calcula la fecha límite de respuesta
    Entonces la fecha límite no supera los 10 días
