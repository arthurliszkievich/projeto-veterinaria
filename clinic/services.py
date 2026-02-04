"""
DEPRECADO: Este módulo está obsoleto.

A função sugerir_diagnosticos() foi movida para a classe DiagnosticoService
em clinic.services.diagnostico_service seguindo princípios SOLID.

Este módulo é mantido apenas para backward compatibility.
Use a nova estrutura:

    from clinic.services import DiagnosticoService
    
    service = DiagnosticoService()
    diagnosticos = service.sugerir_diagnosticos(sintomas)

Será removido em versões futuras.
"""

import logging
import warnings

from .models import Doenca

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def sugerir_diagnosticos(sintomas_apresentados_objs):
    """
    DEPRECADO: Use DiagnosticoService.sugerir_diagnosticos() ao invés desta função.

    Esta função é mantida apenas para backward compatibility.
    
    Args:
        sintomas_apresentados_objs (list): Lista de objetos Sintoma apresentados pelo paciente.

    Returns:
        list: Lista ordenada de objetos Doenca (da maior para menor probabilidade).
    """
    warnings.warn(
        "sugerir_diagnosticos() está obsoleto. "
        "Use DiagnosticoService.sugerir_diagnosticos() ao invés.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Importação lazy para evitar circular imports
    from .services import DiagnosticoService

    service = DiagnosticoService()
    return service.sugerir_diagnosticos(sintomas_apresentados_objs)
