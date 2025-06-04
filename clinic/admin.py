# clinic/admin.py
from django.contrib import admin
from .models import Tutor, Paciente


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
    get_idade.short_description = 'Idade Atual'
