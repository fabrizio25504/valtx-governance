#!/usr/bin/env python3
"""
Genera las Policy Cards de la Ley N° 29733 (Perú) + Reglamento DS 016-2024-JUS.

Fuente de verdad auditable de la normativa peruana destilada a tarjetas.
Artículos de la LEY 29733: verificados en múltiples fuentes (alta confianza).
Artículos del REGLAMENTO DS 016-2024-JUS: de fuentes secundarias (IAPP) —
marcados con `nota: POR CONFIRMAR` donde no hubo doble verificación.

Ejecuta:  python .specify/memory/policies/build_policies_peru.py
"""
import os, yaml

HERE = os.path.dirname(__file__)
REV = "2025-03-30"        # vigencia del reglamento DS 016-2024-JUS
VIG = "2027-03-30"        # próxima revisión (cadencia bianual)
OWNER = "legal@valtx.pe"

URLS = {
    "ley": "https://diariooficial.elperuano.pe/Normas/obtenerDocumento?idNorma=23",
    "reg": "https://busquedas.elperuano.pe/dispositivo/SE/2349653-1",
}

CARDS = [
    dict(
        id="POL-PE-CONSENT-001",
        titulo="Consentimiento para tratamiento de datos personales",
        enforcement="MUST",
        triggers=["registro", "formulario", "cuenta", "cookies", "tracking",
                  "marketing", "pii", "datos_personales", "opt-in"],
        requisito=("Obtener consentimiento previo, libre, expreso, informado e "
                   "inequívoco ANTES de tratar datos personales, y que sea DEMOSTRABLE "
                   "(registrar timestamp, versión de política y texto mostrado). "
                   "Prohibidos checkboxes premarcados o consentimiento por inacción."),
        fuente="Ley 29733 Art. 5 (principio de consentimiento); Art. 13-14 (alcances/límites); "
               "DS 016-2024-JUS Arts. 22, 25, 26 (menores, identidad en Internet, publicidad)",
        source_url=URLS["ley"],
        nota="Características del consentimiento (inequívoco/demostrable) del reglamento: "
             "artículo general POR CONFIRMAR en el texto oficial.",
        patron_ears=("WHEN el usuario inicia una acción que recolecta datos personales "
                     "THE SYSTEM SHALL registrar consentimiento previo, expreso y demostrable "
                     "(timestamp + versión de política) antes de tratar el dato."),
        mapea_principio="PRIN-PRIV-001",
    ),
    dict(
        id="POL-PE-SENSIBLE-002",
        titulo="Datos sensibles — tratamiento reforzado",
        enforcement="MUST",
        triggers=["salud", "biometria", "huella", "rostro", "genetico", "etnia",
                  "religion", "politica", "sindical", "orientacion_sexual", "sensible"],
        requisito=("Los datos sensibles exigen consentimiento expreso y POR ESCRITO "
                   "(firma manuscrita/digital/electrónica). Aplicar cifrado y control de "
                   "acceso estricto; minimizar o evitar el almacenamiento cuando sea posible."),
        fuente="Ley 29733 Art. 2.5 (definición de datos sensibles); "
               "DS 016-2024-JUS Título Preliminar Art. III (definiciones ampliadas: biométricos/neuronales)",
        source_url=URLS["ley"],
        nota="El reglamento amplía la definición (biométricos que identifican, datos neuronales/emocionales).",
        patron_ears=("WHERE el feature trata datos sensibles THE SYSTEM SHALL exigir "
                     "consentimiento por escrito y cifrar el dato en reposo y tránsito."),
        mapea_principio="PRIN-PRIV-001",
    ),
    dict(
        id="POL-PE-UBIC-003",
        titulo="Datos de ubicación e identificadores en línea",
        enforcement="MUST",
        triggers=["ubicacion", "geolocalizacion", "gps", "geofencing", "ip",
                  "cookies", "device_id", "tracking", "location"],
        requisito=("Tratar la geolocalización, IP, cookies y device-ID como datos "
                   "personales. Recabar consentimiento ESPECÍFICO y separado del general "
                   "para capturar ubicación; permitir revocación y no capturar en background sin aviso."),
        fuente="Ley 29733 (ubicación como dato personal); DS 016-2024-JUS Título Preliminar Art. III "
               "(identificadores en línea/ubicación dentro de datos personales)",
        source_url=URLS["reg"],
        nota="No existe artículo dedicado exclusivamente a geolocalización; se clasifica vía definiciones.",
        patron_ears=("WHEN el usuario activa una función que requiere ubicación "
                     "THE SYSTEM SHALL solicitar consentimiento específico y separado "
                     "antes de capturar coordenadas, con opción de revocación."),
        mapea_principio="PRIN-PRIV-001",
    ),
    dict(
        id="POL-PE-MINIM-004",
        titulo="Finalidad, proporcionalidad, calidad y retención",
        enforcement="MUST",
        triggers=["esquema_bd", "formulario", "retencion", "purga", "logs",
                  "data_warehouse", "pii", "perfil"],
        requisito=("Recolectar solo datos necesarios y pertinentes para una finalidad "
                   "determinada y explícita (minimización). Definir política de retención "
                   "con borrado/anonimización automático al expirar. Mantener datos exactos y actualizados."),
        fuente="Ley 29733 Art. 6 (finalidad), Art. 7 (proporcionalidad), Art. 8 (calidad), Art. 20 (supresión)",
        source_url=URLS["ley"],
        nota="Plazo fijo de retención (p.ej. 2 años marketing) citado por fuentes secundarias — NO confirmado; "
             "definir plazo por finalidad.",
        patron_ears=("THE SYSTEM SHALL capturar el mínimo de campos necesarios y aplicar "
                     "un plazo de retención con purga automática por finalidad declarada."),
        mapea_principio="PRIN-PRIV-001",
    ),
    dict(
        id="POL-PE-ARCO-005",
        titulo="Derechos ARCO + portabilidad",
        enforcement="MUST",
        triggers=["cuenta", "perfil", "eliminar_cuenta", "exportar_datos", "dsar",
                  "baja", "pii"],
        requisito=("Implementar flujos para acceso, rectificación, cancelación (supresión) "
                   "y oposición del titular, con respuesta en el plazo legal de 10 días. "
                   "Ofrecer exportación en formato estructurado (portabilidad)."),
        fuente="Ley 29733 Art. 19 (acceso), Art. 20 (rectificación/supresión), Art. 22 (oposición), "
               "Arts. 18,21,23,24 (conexos); DS 016-2024-JUS Art. 76 (portabilidad)",
        source_url=URLS["ley"],
        nota="Art. 76 (portabilidad) del reglamento: POR CONFIRMAR (fuente IAPP).",
        patron_ears=("WHEN el titular solicita acceso/rectificación/cancelación/oposición "
                     "THE SYSTEM SHALL atender la solicitud en un máximo de 10 días."),
        mapea_principio="PRIN-PRIV-001",
    ),
    dict(
        id="POL-PE-SEG-006",
        titulo="Medidas de seguridad del tratamiento",
        enforcement="MUST",
        triggers=["almacenamiento", "autenticacion", "logging", "backup", "cifrado",
                  "pii", "transmision"],
        requisito=("Implementar medidas técnicas y organizativas: cifrado, control de "
                   "acceso, logs conservados (mín. 2 años) y un Documento de Seguridad con "
                   "inventario de bancos de datos y medidas."),
        fuente="Ley 29733 Art. 9 (principio de seguridad), Art. 16 (seguridad del tratamiento); "
               "DS 016-2024-JUS Art. 47 (Documento de Seguridad), Arts. 49-50 (accesos/equipos)",
        source_url=URLS["ley"],
        nota="Arts. 47/49/50 del reglamento: confianza media (IAPP).",
        patron_ears=("THE SYSTEM SHALL cifrar los datos personales en reposo y tránsito "
                     "y registrar accesos en logs conservados al menos 2 años."),
        mapea_principio="PRIN-SEC-002",
    ),
    dict(
        id="POL-PE-TRANSF-007",
        titulo="Flujo transfronterizo de datos",
        enforcement="MUST",
        triggers=["cloud", "hosting_extranjero", "saas", "cdn", "subprocesador",
                  "transferencia_internacional"],
        requisito=("Antes de enviar datos fuera de Perú, verificar nivel de protección "
                   "adecuado del país destino o usar cláusulas contractuales tipo/consentimiento. "
                   "Entidades extranjeras que sirven a residentes peruanos deben designar representante local."),
        fuente="Ley 29733 Art. 15 (flujo transfronterizo); DS 016-2024-JUS Arts. 18-20 (transferencia internacional)",
        source_url=URLS["ley"],
        nota="Arts. 18-20 del reglamento: confianza media (IAPP).",
        patron_ears=("WHERE el dato personal se procesa o almacena fuera de Perú "
                     "THE SYSTEM SHALL garantizar base de transferencia válida (adecuación o cláusulas)."),
        mapea_principio="PRIN-ARCH-001",
    ),
    dict(
        id="POL-PE-REGISTRO-008",
        titulo="Inscripción de banco de datos (RNPDP)",
        enforcement="MUST",
        triggers=["nueva_bd", "nuevo_producto", "nuevo_sistema", "pii"],
        requisito=("Inscribir cada banco de datos personales en el Registro Nacional de "
                   "Protección de Datos Personales (RNPDP/SIPDP) ANTES de iniciar el tratamiento. "
                   "La inscripción es gratuita."),
        fuente="Ley 29733 Art. 34 (Registro Nacional; no inscribir = infracción grave)",
        source_url=URLS["ley"],
        nota="",
        patron_ears=("WHEN se crea un nuevo banco de datos con datos personales "
                     "THE SYSTEM SHALL bloquear el go-live hasta registrar su inscripción en el RNPDP."),
        mapea_principio="PRIN-PRIV-001",
    ),
    dict(
        id="POL-PE-BRECHA-009",
        titulo="Notificación de brechas de seguridad",
        enforcement="MUST",
        triggers=["incidente", "brecha", "acceso_no_autorizado", "filtracion",
                  "ransomware", "perdida_datos"],
        requisito=("Ante un incidente de seguridad que afecte datos personales, notificar a "
                   "la ANPD (y a los titulares cuando corresponda) en un máximo de 48 horas "
                   "desde su conocimiento. Mantener un procedimiento documentado de respuesta a brechas."),
        fuente="DS 016-2024-JUS Art. 34 (notificación de brechas, 48h)",
        source_url=URLS["reg"],
        nota="Art. 34 del reglamento y plazo 48h: confianza media-alta (IAPP/guías). CONFIRMAR número.",
        patron_ears=("WHEN se detecta una brecha de seguridad de datos personales "
                     "THE SYSTEM SHALL disparar el flujo de notificación a la ANPD dentro de 48h."),
        mapea_principio="PRIN-SEC-002",
    ),
]


def main():
    for c in CARDS:
        c = dict(c)
        c["fecha_revision"] = REV
        c["vigencia_hasta"] = VIG
        c["owner"] = OWNER
        c["jurisdiccion"] = "PE"
        if not c.get("nota"):
            c.pop("nota", None)
        path = os.path.join(HERE, f"{c['id']}.yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(c, f, allow_unicode=True, sort_keys=False, width=100)
        print("escrita", os.path.basename(path))
    print(f"\n{len(CARDS)} Policy Cards de Ley 29733 + DS 016-2024-JUS generadas.")


if __name__ == "__main__":
    main()
