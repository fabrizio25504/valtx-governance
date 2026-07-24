# language: es
# Cada Scenario etiquetado con su REQ. El gate de cobertura exige 100%.

Característica: Expiración y renovación de consentimiento de ubicación

  @REQ-CONS-001
  Escenario: Avisar antes de que expire el consentimiento
    Dado un consentimiento que expira en 3 días
    Y una ventana de aviso de 7 días
    Cuando corre el chequeo diario
    Entonces el sistema notifica al usuario para renovar

  @REQ-CONS-002
  Escenario: Expirar sin renovación purga los datos
    Dado un consentimiento cuya fecha de expiración ya pasó
    Cuando corre el proceso de expiración
    Entonces el sistema detiene la captura y purga los datos de ubicación

  @REQ-CONS-003
  Escenario: Renovar registra la renovación demostrable
    Dado un usuario con consentimiento vigente
    Cuando renueva aceptando la política v2
    Entonces el sistema registra la renovación con timestamp y versión de política
