# language: es
Característica: Job programado que aplica retención y purga de logs de acceso
  Como sistema
  Quiero aplicar una política de retención y purgar los logs de acceso vencidos
  Para cumplir con la normativa de minimización y retención de datos

  @REQ-RET-001
  Escenario: Ejecución del job de purga de logs vencidos
    Dado que existen logs de acceso con fechas de retención vencidas
    Cuando el job programado se ejecuta
    Entonces el sistema purga los registros de logs vencidos

  @REQ-EXP-001
  Escenario: Exportación del historial de accesos por el titular
    Dado que el titular solicita exportar su historial de accesos desde su perfil
    Cuando el sistema procesa la solicitud de exportación
    Entonces el sistema entrega los datos de acceso en un formato estructurado
