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
            'fields': ('especie', 'raca', 'data_nascimento', 'sexo', 'cor_pelagem', 'peso_kg', 'procedencia')
        }),
        ('Histórico Pregresso', {
            'fields': ('alimentacao_detalhes', 'contactantes_outros_animais', 'ambiente_onde_vive',
                       'historico_vacinacao', 'historico_vermifugacao', 'doencas_pregressas',
                       'cirurgias_anteriores', 'alergias_conhecidas')
        }),
        ('Status e Controle', {
            'fields': ('status', 'observacoes_clinicas_relevantes', 'data_cadastro')
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
    # Define as colunas exibidas na lista de consultas
    list_display = ('paciente', 'data_hora_agendamento', 'tipo_consulta',
                    'veterinario_responsavel', 'get_tutor_nome', 'data_criacao_registro')

    # Adiciona filtros na barra lateral da lista de consultas
    list_filter = ('tipo_consulta', 'data_hora_agendamento',
                   # Filtrar pela espécie do pacient
                   'veterinario_responsavel', 'paciente__especie')

    # Define os campos pelos quais a busca pode ser feita
    search_fields = ('paciente__nome', 'paciente__tutor__nome_completo',
                     'veterinario_responsavel__nome_completo', 'tipo_consulta', 'suspeitas_diagnosticas')

    # Melhora a seleção de ForeignKeys com muitos itens
    autocomplete_fields = ['paciente', 'veterinario_responsavel']

    # Adiciona uma hierarquia de navegação por data na lista de consultas
    date_hierarchy = 'data_hora_agendamento'

    # Define a ordenação padrão na lista de consultas (mais recentes primeiro)
    ordering = ['-data_hora_agendamento']

    # Organiza os campos no formulário de adição/edição de Consulta
    fieldsets = (
        ("Informações Gerais da Consulta", {
            'fields': ('paciente', 'veterinario_responsavel', 'data_hora_agendamento', 'tipo_consulta')
        }),
        ("Anamnese Geral", {
            'fields': ('queixa_principal_tutor', 'historico_doenca_atual')
        }),
        ("Anamnese Especial (Revisão por Sistema)", {
            # Descrição para a seção
            'description': "Detalhes da anamnese para cada sistema do animal.",
            # Faz a seção iniciar colapsada (opcional)
            'classes': ('collapse',),
            'fields': (
                'anamnese_sistema_respiratorio', 'anamnese_sistema_cardiovascular',
                'anamnese_sistema_digestorio', 'anamnese_sistema_urinario',
                'anamnese_sistema_reprodutor', 'anamnese_sistema_locomotor',
                'anamnese_sistema_neurologico', 'anamnese_pele_anexos',
                'anamnese_olhos',
            )
        }),
        ("Exame Físico Geral", {
            'description': "Sinais vitais e observações gerais do exame físico.",
            'fields': (
                # Agrupando campos relacionados na mesma linha para melhor layout
                ('temperatura_celsius', 'frequencia_cardiaca_bpm',
                 'frequencia_respiratoria_mpm'),
                ('tpc_segundos', 'hidratacao_status', 'escore_condicao_corporal'),
                'exame_postura', 'exame_nivel_consciencia',
                'exame_linfonodos_obs', 'exame_mucosas_obs', 'exame_pulso_ppm',
                'observacoes_exame_fisico_geral',
            )
        }),
        ("Exame Físico Específico (por Sistema)", {
            'description': "Achados detalhados do exame físico para cada sistema.",
            'classes': ('collapse',),
            'fields': (
                'examefisico_sistema_respiratorio', 'examefisico_sistema_cardiovascular',
                'examefisico_sistema_digestorio', 'examefisico_sistema_urinario',
                'examefisico_sistema_reprodutor', 'examefisico_sistema_locomotor',
                'examefisico_sistema_neurologico', 'examefisico_pele_anexos',
                'examefisico_olhos', 'examefisico_ouvidos',
            )
        }),
        ("Sintomas e Diagnóstico Inicial", {
            'fields': ('sintomas_apresentados', 'suspeitas_diagnosticas')
        }),
        ("Exames e Diagnóstico Definitivo", {
            'fields': ('exames_complementares_solicitados', 'diagnostico_definitivo')
        }),
        ("Tratamento e Prognóstico", {
            'fields': ('tratamento_prescrito', 'procedimentos_realizados', 'prognostico')
        }),
        ("Orientações e Pós-Consulta", {
            'fields': ('instrucoes_para_tutor', 'data_proximo_retorno')
        }),
        ("Datas de Controle", {  # Seção para campos de data gerenciados automaticamente
            'fields': ('data_criacao_registro', 'data_ultima_modificacao'),
            'classes': ('collapse',),  # Inicia colapsada
            'description': "Datas de criação e última modificação do registro."
        })
    )

    # Melhora a interface para campos ManyToManyField
    filter_horizontal = ('sintomas_apresentados',)

    # Define campos que serão apenas de leitura no formulário do admin
    readonly_fields = ('data_criacao_registro', 'data_ultima_modificacao')

    # Método para exibir o nome do tutor na lista de consultas
    def get_tutor_nome(self, obj):
        if obj.paciente and obj.paciente.tutor:
            return obj.paciente.tutor.nome_completo
        return "N/A"  # Valor padrão se não houver tutor ou paciente
    # Nome mais descritivo para a coluna
    get_tutor_nome.short_description = 'Tutor do Paciente'  # type: ignore
    # Permite ordenação por esta coluna
    get_tutor_nome.admin_order_field = 'paciente__tutor__nome_completo'  # type: ignore
