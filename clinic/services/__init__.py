"""
Camada de Serviços - Business Logic Layer

Este módulo centraliza toda a lógica de negócio da aplicação,
seguindo o princípio de Responsabilidade Única (SRP).

Os serviços são responsáveis por:
- Orquestração de operações complexas
- Validações de regras de negócio
- Coordenação entre múltiplos models
- Cálculos e algoritmos de domínio

As Views devem ser finas e apenas delegar para os serviços.
"""

from .consulta_service import ConsultaService
from .diagnostico_service import DiagnosticoService
from .tutor_service import TutorService

# Importar função deprecated para backward compatibility
import sys
sys.path.insert(0, '..')
try:
    from ..services import sugerir_diagnosticos
except ImportError:
    # Se falhar, criar wrapper
    def sugerir_diagnosticos(sintomas):
        """DEPRECATED: Use DiagnosticoService.sugerir_diagnosticos()"""
        import warnings
        warnings.warn(
            "sugerir_diagnosticos() está obsoleto. Use DiagnosticoService.sugerir_diagnosticos()",
            DeprecationWarning,
            stacklevel=2
        )
        service = DiagnosticoService()
        return service.sugerir_diagnosticos(sintomas)

__all__ = [
    "ConsultaService",
    "DiagnosticoService",
    "TutorService",
    "sugerir_diagnosticos",  # Backward compatibility
]
