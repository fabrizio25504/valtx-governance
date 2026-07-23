# language: es
# Escenarios Gherkin — cada Scenario se etiqueta con el/los REQ que valida.
# El gate de cobertura falla si algún REQ del spec no aparece aquí.

Característica: Check-in por geolocalización

  @REQ-GEO-001
  Escenario: Se pide consentimiento antes de capturar ubicación
    Dado que el usuario nunca aceptó la política de ubicación
    Cuando intenta hacer check-in
    Entonces el sistema solicita consentimiento explícito
    Y no captura coordenadas hasta que el usuario acepta

  @REQ-GEO-002
  Escenario: La ubicación tiene retención con purga automática
    Dado un check-in registrado hace más del plazo de retención
    Cuando corre el proceso de purga
    Entonces las coordenadas asociadas se eliminan

  @REQ-GEO-003
  Escenario: Revocar consentimiento detiene y purga
    Dado un usuario con consentimiento activo
    Cuando revoca el consentimiento
    Entonces el sistema deja de capturar y purga sus coordenadas
