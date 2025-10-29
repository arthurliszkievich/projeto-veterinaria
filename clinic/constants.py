"""
Constantes e mensagens centralizadas para a aplicação clinic.
"""

# ==================== MENSAGENS DE ERRO ====================

# Tutor
ERROR_TUTOR_CPF_INVALIDO = "CPF inválido"
ERROR_TUTOR_PROTECTED_DELETE = (
    "Não é possível excluir o tutor porque existem pacientes associados."
)
ERROR_TUTOR_CPF_DUPLICADO = "Já existe um tutor cadastrado com este CPF."
ERROR_TUTOR_EMAIL_DUPLICADO = "Já existe um tutor cadastrado com este e-mail."

# Paciente
ERROR_PACIENTE_MICROCHIP_DUPLICADO = (
    "Já existe um paciente cadastrado com este microchip."
)

# Veterinário
ERROR_VETERINARIO_CRMV_DUPLICADO = "Já existe um veterinário cadastrado com este CRMV."

# Sintoma
ERROR_SINTOMA_NOME_DUPLICADO = "Já existe um sintoma cadastrado com este nome."

# Doença
ERROR_DOENCA_NOME_DUPLICADO = "Já existe uma doença cadastrada com este nome."

# Consulta
ERROR_CONSULTA_PACIENTE_OBRIGATORIO = "O campo paciente é obrigatório."
ERROR_CONSULTA_DATA_FUTURA = "A data de nascimento não pode ser no futuro."

# Gerais
ERROR_FIELD_REQUIRED = "Este campo é obrigatório."
ERROR_UNIQUE_CONSTRAINT = "Este valor já está cadastrado no sistema."
ERROR_INTEGRITY_ERROR = "Erro de integridade no banco de dados."
ERROR_GENERIC = "Ocorreu um erro ao processar a requisição."


# ==================== MENSAGENS DE SUCESSO ====================

SUCCESS_CREATED = "Registro criado com sucesso."
SUCCESS_UPDATED = "Registro atualizado com sucesso."
SUCCESS_DELETED = "Registro excluído com sucesso."


# ==================== LABELS E VERBOSE NAMES ====================

# Tutor
LABEL_TUTOR_NOME_COMPLETO = "Nome Completo"
LABEL_TUTOR_CPF = "CPF"
LABEL_TUTOR_EMAIL = "E-mail"
LABEL_TUTOR_TELEFONE_PRINCIPAL = "Telefone Principal"
LABEL_TUTOR_TELEFONE_SECUNDARIO = "Telefone Secundário"
LABEL_TUTOR_DATA_CADASTRO = "Data de Cadastro"

# Paciente
LABEL_PACIENTE_NOME = "Nome do Paciente"
LABEL_PACIENTE_ESPECIE = "Espécie"
LABEL_PACIENTE_RACA = "Raça"
LABEL_PACIENTE_DATA_NASCIMENTO = "Data de Nascimento"
LABEL_PACIENTE_SEXO = "Sexo"
LABEL_PACIENTE_PESO = "Peso (kg)"

# Veterinário
LABEL_VETERINARIO_NOME = "Nome do Veterinário"
LABEL_VETERINARIO_CRMV = "CRMV"

# Sintoma
LABEL_SINTOMA_NOME = "Nome do Sintoma"
LABEL_SINTOMA_DESCRICAO = "Descrição do Sintoma"

# Doença
LABEL_DOENCA_NOME = "Nome da Doença"
LABEL_DOENCA_DESCRICAO = "Descrição"
LABEL_DOENCA_SINTOMAS_ASSOCIADOS = "Sintomas Típicos Associados"

# Consulta
LABEL_CONSULTA_PACIENTE = "Paciente"
LABEL_CONSULTA_VETERINARIO = "Veterinário Responsável"
LABEL_CONSULTA_DATA = "Data e Hora do Atendimento"
LABEL_CONSULTA_TIPO = "Tipo de Consulta"


# ==================== HELP TEXTS ====================

HELP_TEXT_CPF_FORMAT = "formato: XXX.XXX.XXX-XX"
HELP_TEXT_CEP_FORMAT = "formato: XXXXX-XXX"
HELP_TEXT_TUTOR_OBSERVACOES = "Informações adicionais sobre o tutor"
HELP_TEXT_PACIENTE_FOTO = "Foto do paciente"
HELP_TEXT_DOENCA_SINTOMAS = (
    "Lista de IDs dos sintomas a serem associados a esta doença."
)


# ==================== CHOICES ====================

# Paciente - Espécie
ESPECIE_CANINO = "CANINO"
ESPECIE_FELINO = "FELINO"
ESPECIE_AVE = "AVE"
ESPECIE_REPTIL = "REPTIL"
ESPECIE_ROEDOR = "ROEDOR"
ESPECIE_LAGOMORFO = "LAGOMORFO"
ESPECIE_OUTRO = "OUTRO"

ESPECIE_CHOICES = [
    (ESPECIE_CANINO, "Canino"),
    (ESPECIE_FELINO, "Felino"),
    (ESPECIE_AVE, "Ave"),
    (ESPECIE_REPTIL, "Réptil"),
    (ESPECIE_ROEDOR, "Roedor"),
    (ESPECIE_LAGOMORFO, "Lagomorfo (Coelho)"),
    (ESPECIE_OUTRO, "Outro"),
]

# Paciente - Sexo
SEXO_MACHO = "M"
SEXO_FEMEA = "F"
SEXO_MACHO_CASTRADO = "MC"
SEXO_FEMEA_CASTRADA = "FC"
SEXO_INDEFINIDO = "IND"

SEXO_CHOICES = [
    (SEXO_MACHO, "Macho"),
    (SEXO_FEMEA, "Fêmea"),
    (SEXO_MACHO_CASTRADO, "Macho Castrado"),
    (SEXO_FEMEA_CASTRADA, "Fêmea Castrada"),
    (SEXO_INDEFINIDO, "Indefinido"),
]

# Paciente - Status
STATUS_ATIVO = "ATIVO"
STATUS_OBITO = "OBITO"
STATUS_TRANSFERIDO = "TRANSFERIDO"
STATUS_PERDIDO = "PERDIDO"

STATUS_CHOICES = [
    (STATUS_ATIVO, "Ativo"),
    (STATUS_OBITO, "Óbito"),
    (STATUS_TRANSFERIDO, "Transferido"),
    (STATUS_PERDIDO, "Perdido"),
]

# Consulta - Tipo
TIPO_ROTINA = "ROTINA"
TIPO_EMERGENCIA = "EMERGENCIA"
TIPO_VACINACAO = "VACINACAO"
TIPO_CIRURGIA = "CIRURGIA"
TIPO_POS_CIRURGICO = "POS_CIRURGICO"
TIPO_RETORNO = "RETORNO"
TIPO_OUTRO = "OUTRO"

TIPO_CONSULTA_CHOICES = [
    (TIPO_ROTINA, "Rotina/Check-up"),
    (TIPO_EMERGENCIA, "Emergência"),
    (TIPO_VACINACAO, "Vacinação"),
    (TIPO_CIRURGIA, "Cirurgia/Procedimento"),
    (TIPO_POS_CIRURGICO, "Pós-Cirúrgico"),
    (TIPO_RETORNO, "Retorno"),
    (TIPO_OUTRO, "Outro"),
]


# ==================== CONFIGURAÇÕES ====================

# Paginação
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Validação
CPF_REGEX = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
CEP_REGEX = r"^\d{5}-\d{3}$"
TELEFONE_REGEX = r"^\(\d{2}\)\s?\d{4,5}-\d{4}$"

# Score de diagnóstico
DIAGNOSTICO_SCORE_MINIMO = 0.0
DIAGNOSTICO_SCORE_MAXIMO = 1.0
