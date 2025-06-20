# clinic/admin.py
from django.contrib import admin
from .models import Tutor, Paciente, Veterinario, Consulta, Sintoma, Doenca


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = (
        "nome_completo",
        "cpf",
        "email",
        "telefone_principal",
        "data_cadastro",
    )
    search_fields = ("nome_completo", "cpf", "email")
    list_filter = ("data_cadastro", "endereco_cidade", "endereco_uf")
    fieldsets = (
        (None, {"fields": ("nome_completo", "cpf", "email")}),
        ("Contato", {"fields": ("telefone_principal", "telefone_secundario")}),
        (
            "Endereço",
            {
                "fields": (
                    "endereco_rua",
                    "endereco_numero",
                    "endereco_complemento",
                    "endereco_bairro",
                    "endereco_cidade",
                    "endereco_uf",
                    "endereco_cep",
                )
            },
        ),
        ("Outras Informações", {"fields": ("observacoes", "data_cadastro")}),
    )
    # Torna o campo data_cadastro apenas leitura no admin
    readonly_fields = ("data_cadastro",)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tutor",
        "especie",
        "raca",
        "sexo",
        "status",
        "idade",
        "data_cadastro",
    )
    search_fields = ("nome", "tutor__nome_completo", "microchip", "raca")
    list_filter = (
        "especie",
        "sexo",
        "status",
        "tutor__endereco_cidade",
        "data_cadastro",
    )
    autocomplete_fields = ["tutor"]  # Facilita a busca e seleção do tutor
    # Idade é uma property, não pode ser editada diretamente
    readonly_fields = ("data_cadastro", "idade")
    fieldsets = (
        (
            "Identificação do Paciente",
            {"fields": ("nome", "tutor", "foto", "microchip")},
        ),
        (
            "Características",
            {
                "fields": (
                    "especie",
                    "raca",
                    "data_nascimento",
                    "sexo",
                    "cor_pelagem",
                    "peso_kg",
                    "procedencia",
                )
            },
        ),
        (
            "Histórico Pregresso",
            {
                "fields": (
                    "alimentacao_detalhes",
                    "contactantes_outros_animais",
                    "ambiente_onde_vive",
                    "historico_vacinacao",
                    "historico_vermifugacao",
                    "doencas_pregressas",
                    "cirurgias_anteriores",
                    "alergias_conhecidas",
                )
            },
        ),
        (
            "Status e Controle",
            {"fields": ("status", "observacoes_clinicas_relevantes",
                        "data_cadastro")},
        ),
    )

    def get_idade(
        self, obj
    ):  # Para exibir a property 'idade' corretamente se necessário
        return obj.idade

    get_idade.short_description = "Idade Atual"  # type: ignore


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = (
        "nome_completo",
        "crmv",
    )
    search_fields = ("nome_completo", "crmv")


@admin.register(Sintoma)
class SintomaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = (
        "paciente",
        "data_hora_agendamento",
        "tipo_consulta",
        "veterinario_responsavel",
        "get_tutor_nome",
        "data_criacao_registro",
    )
    list_filter = (
        "tipo_consulta",
        "data_hora_agendamento",
        "veterinario_responsavel",
        "paciente__especie",
    )
    search_fields = (
        "paciente__nome",
        "paciente__tutor__nome_completo",
        "veterinario_responsavel__nome_completo",
        "tipo_consulta",
        "diagnosticos_suspeitos__nome",
        "diagnosticos_definitivos__nome",
    )
    autocomplete_fields = ["paciente", "veterinario_responsavel"]
    date_hierarchy = "data_hora_agendamento"
    ordering = ["-data_hora_agendamento"]

    fieldsets = (
        (
            "Informações Gerais da Consulta",
            {
                "fields": (
                    "paciente",
                    "veterinario_responsavel",
                    "data_hora_agendamento",
                    "tipo_consulta",
                )
            },
        ),
        (
            "Anamnese Geral",
            {"fields": ("queixa_principal_tutor", "historico_doenca_atual")},
        ),
        (
            "Anamnese Especial (Revisão por Sistema)",
            {
                "description": "Detalhes da anamnese para cada sistema do animal.",
                "classes": ("collapse",),
                "fields": (
                    "anamnese_sistema_respiratorio",
                    "anamnese_sistema_cardiovascular",
                    "anamnese_sistema_digestorio",
                    "anamnese_sistema_urinario",
                    "anamnese_sistema_reprodutor",
                    "anamnese_sistema_locomotor",
                    "anamnese_sistema_neurologico",
                    "anamnese_pele_anexos",
                    "anamnese_olhos",
                    # "anamnese_ouvidos" - Adicionei este aqui, pois você tem o exame físico de ouvidos
                ),
            },
        ),
        (
            "Exame Físico Geral",
            {
                "description": "Sinais vitais e observações gerais do exame físico.",
                "fields": (
                    (
                        "temperatura_celsius",
                        "frequencia_cardiaca_bpm",
                        "frequencia_respiratoria_mpm",
                    ),
                    ("tpc_segundos", "hidratacao_status",
                     "escore_condicao_corporal"),
                    "exame_postura",
                    "exame_nivel_consciencia",
                    "exame_linfonodos_obs",
                    "exame_mucosas_obs",
                    "exame_pulso_ppm",
                    "observacoes_exame_fisico_geral",
                ),
            },
        ),
        (
            "Exame Físico Específico (por Sistema)",
            {
                "description": "Achados detalhados do exame físico para cada sistema.",
                "classes": ("collapse",),
                "fields": (
                    "examefisico_sistema_respiratorio",
                    "examefisico_sistema_cardiovascular",
                    "examefisico_sistema_digestorio",
                    "examefisico_sistema_urinario",
                    "examefisico_sistema_reprodutor",
                    "examefisico_sistema_locomotor",
                    "examefisico_sistema_neurologico",
                    "examefisico_pele_anexos",
                    "examefisico_olhos",
                    "examefisico_ouvidos",
                ),
            },
        ),
        (
            # Nome da seção pode ser "Sintomas Apresentados e Diagnósticos Suspeitos"
            "Sintomas e Diagnóstico Inicial",
            {"fields": ("sintomas_apresentados", "diagnosticos_suspeitos")},
        ),
        (
            "Exames e Diagnóstico Definitivo",
            {"fields": ("exames_complementares_solicitados",
                        "diagnosticos_definitivos")},
        ),
        (
            "Tratamento e Prognóstico",
            {
                "fields": (
                    "tratamento_prescrito",
                    "procedimentos_realizados",
                    "prognostico",
                )
            },
        ),
        (
            "Orientações e Pós-Consulta",
            {"fields": ("instrucoes_para_tutor", "data_proximo_retorno")},
        ),
        (
            "Datas de Controle",
            {
                "fields": ("data_criacao_registro", "data_ultima_modificacao"),
                "classes": ("collapse",),
                "description": "Datas de criação e última modificação do registro.",
            },
        ),
    )

    filter_horizontal = (
        "sintomas_apresentados",
        "diagnosticos_suspeitos",
    )
    readonly_fields = ("data_criacao_registro", "data_ultima_modificacao")

    def get_tutor_nome(self, obj):
        if obj.paciente and obj.paciente.tutor:
            return obj.paciente.tutor.nome_completo
        return "N/A"

    get_tutor_nome.short_description = "Tutor do Paciente"  # type: ignore
    get_tutor_nome.admin_order_field = "paciente__tutor__nome_completo"  # type: ignore


@admin.register(Doenca)
class DoencaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_sintomas_count')
    search_fields = ('nome', 'descricao', 'sintomas_associados__nome')
    filter_horizontal = ('sintomas_associados',)

    @admin.display(description='Nº de Sintomas Associados')
    def get_sintomas_count(self, obj):
        """Retorna a contagem de sintomas associados."""
        return obj.sintomas_associados.count()
