"""
Serviço de Tutor

Responsável pela lógica de negócio relacionada a tutores.
Encapsula validações, formatações e regras de negócio.

Princípios aplicados:
- SRP: Apenas responsável pela lógica de tutores
- DRY: Validação de CPF centralizada e reutilizável
"""

import logging
from typing import Tuple

from validate_docbr import CPF

from ..constants import ERROR_TUTOR_CPF_INVALIDO

logger = logging.getLogger(__name__)


class TutorService:
    """
    Serviço para gerenciar operações relacionadas a tutores.

    Este serviço encapsula toda a lógica de negócio para tutores,
    incluindo validação e formatação de CPF.

    Example:
        >>> service = TutorService()
        >>> cpf_valido, cpf_formatado = service.validar_e_formatar_cpf("12345678900")
        >>> if cpf_valido:
        ...     tutor.cpf = cpf_formatado
    """

    def __init__(self):
        """Inicializa o serviço com validador de CPF."""
        self.cpf_validator = CPF()

    def validar_e_formatar_cpf(self, cpf_raw: str) -> Tuple[bool, str]:
        """
        Valida e formata um CPF.

        Args:
            cpf_raw: CPF em qualquer formato (com ou sem pontuação)

        Returns:
            Tupla (is_valid, cpf_formatado):
            - is_valid: True se o CPF é válido, False caso contrário
            - cpf_formatado: CPF no formato XXX.XXX.XXX-XX (ou string vazia se inválido)

        Example:
            >>> service = TutorService()
            >>> is_valid, formatted = service.validar_e_formatar_cpf("12345678900")
            >>> if is_valid:
            ...     print(formatted)  # "123.456.789-00"
        """
        # Remove formatação para validar apenas os números
        cpf_limpo = self._limpar_cpf(cpf_raw)

        # Valida o CPF
        if not self._validar_cpf(cpf_limpo):
            logger.warning(f"CPF inválido recebido: {cpf_raw}")
            return False, ""

        # Formata o CPF
        cpf_formatado = self._formatar_cpf(cpf_limpo)

        logger.debug(f"CPF validado e formatado: {cpf_formatado}")
        return True, cpf_formatado

    def validar_cpf(self, cpf_raw: str) -> bool:
        """
        Valida um CPF sem formatar.

        Método de conveniência quando apenas a validação é necessária.

        Args:
            cpf_raw: CPF em qualquer formato

        Returns:
            True se válido, False caso contrário

        Example:
            >>> service = TutorService()
            >>> service.validar_cpf("123.456.789-00")
            True
        """
        cpf_limpo = self._limpar_cpf(cpf_raw)
        return self._validar_cpf(cpf_limpo)

    def formatar_cpf(self, cpf_raw: str) -> str:
        """
        Formata um CPF (assume que já foi validado).

        Args:
            cpf_raw: CPF em qualquer formato

        Returns:
            CPF formatado como XXX.XXX.XXX-XX

        Example:
            >>> service = TutorService()
            >>> service.formatar_cpf("12345678900")
            "123.456.789-00"
        """
        cpf_limpo = self._limpar_cpf(cpf_raw)
        return self._formatar_cpf(cpf_limpo)

    def _limpar_cpf(self, cpf: str) -> str:
        """
        Remove toda formatação do CPF.

        Args:
            cpf: CPF com ou sem formatação

        Returns:
            CPF apenas com dígitos
        """
        return cpf.replace(".", "").replace("-", "").strip()

    def _validar_cpf(self, cpf_limpo: str) -> bool:
        """
        Valida CPF usando biblioteca validate_docbr.

        Args:
            cpf_limpo: CPF apenas com dígitos

        Returns:
            True se válido, False caso contrário
        """
        return self.cpf_validator.validate(cpf_limpo)

    def _formatar_cpf(self, cpf_limpo: str) -> str:
        """
        Formata CPF para o padrão XXX.XXX.XXX-XX.

        Args:
            cpf_limpo: CPF apenas com dígitos

        Returns:
            CPF formatado
        """
        return self.cpf_validator.mask(cpf_limpo)
