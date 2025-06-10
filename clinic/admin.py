# clinic/admin.py
from django.contrib import admin
from .models import Tutor, Paciente, Veterinario, Consulta, Sintoma


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'email',
                    'telefone_principal', 'data_cadastro')
    search_fields = ('nome_completo', 'cpf', 'email')
    list_filter = ('data_cadastro', 'endereco_cidade', 'endereco_uf')
    fieldsets = (
        (None, {
            'fields': ('nome_completo', 'cpf', 'email')
        }),
        ('Contato', {
            'fields': ('telefone_principal', 'telefone_secundario')
        }),
        ('Endereço', {
            'fields': ('endereco_rua', 'endereco_numero', 'endereco_complemento', 'endereco_bairro', 'endereco_cidade', 'endereco_uf', 'endereco_cep')
        }),
        ('Outras Informações', {
            'fields': ('observacoes', 'data_cadastro')
        }),
    )
    # Torna o campo data_cadastro apenas leitura no admin
    readonly_fields = ('data_cadastro',)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tutor', 'especie', 'raca',
                    'sexo', 'status', 'idade', 'data_cadastro')
    search_fields = ('nome', 'tutor__nome_completo', 'microchip', 'raca')
    list_filter = ('especie', 'sexo', 'status',
                   'tutor__endereco_cidade', 'data_cadastro')
    autocomplete_fields = ['tutor']  # Facilita a busca e seleção do tutor
    # Idade é uma property, não pode ser editada diretamente
    readonly_fields = ('data_cadastro', 'idade')
    fieldsets = (
        ('Identificação do Paciente', {
            'fields': ('nome', 'tutor', 'foto', 'microchip')
        }),
        ('Características', {
            'fields': ('especie', 'raca', 'data_nascimento', 'sexo', 'cor_pelagem', 'peso_kg')
        }),
        ('Histórico e Status', {
            'fields': ('status', 'alergias_conhecidas', 'observacoes_clinicas')
        }),
        (None, {
            'fields': ('data_cadastro',)
        })
    )

    def get_idade(self, obj):  # Para exibir a property 'idade' corretamente se necessário
        return obj.idade
    get_idade.short_description = 'Idade Atual'  # type: ignore


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'crmv',)
    search_fields = ('nome_completo', 'crmv')


@admin.register(Sintoma)
class SintomaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'data_hora_agendamento',
                    'tipo_consulta', 'veterinario_responsavel', 'get_tutor_nome')
    list_filter = ('tipo_consulta', 'data_hora_agendamento',
                   'veterinario_responsavel', 'paciente__tutor')
    search_fields = ('paciente__nome', 'paciente__tutor__nome_completo',
                     'veterinario_responsavel__nome_completo', 'tipo_consulta')
    autocomplete_fields = ['paciente', 'veterinario_responsavel']
    date_hierarchy = 'data_hora_agendamento'  # Permite navegação por data

    fieldsets = (
        ("Informações Gerais", {
            'fields': ('paciente', 'veterinario_responsavel', 'data_hora_agendamento', 'tipo_consulta')
        }),
        ("Anamnese e Exame Físico", {
            'fields': ('queixa_principal_tutor', 'historico_doenca_atual', ('temperatura_celsius', 'frequencia_cardiaca_bpm', 'frequencia_respiratoria_mpm'),
                       ('tpc_segundos', 'hidratacao_status', 'escore_condicao_corporal'), 'observacoes_exame_fisico', 'sintomas_apresentados')
        }),
        ("Diagnóstico e Tratamento", {
            'fields': ('suspeitas_diagnosticas', 'exames_complementares_solicitados', 'diagnostico_definitivo',
                       'tratamento_prescrito', 'procedimentos_realizados')
        }),
        ("Pós-Consulta", {
            'fields': ('prognostico', 'instrucoes_para_tutor', 'data_proximo_retorno')
        }),

    )
    filter_horizontal = ('sintomas_apresentados',)

    def get_tutor_nome(self, obj):
        return obj.paciente.tutor.nome_completo
    # Nome da coluna no admin
    get_tutor_nome.short_description = 'Tutor'  # type: ignore
    # Permite ordenar por esta coluna
    get_tutor_nome.admin_order_field = 'paciente__tutor__nome_completo'  # type: ignore
