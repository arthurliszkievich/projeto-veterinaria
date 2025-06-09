from rest_framework import serializers
from .models import Tutor, Paciente, Veterinario, Consulta


class TutorSerializer(serializers.ModelSerializer):
    pacientes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Tutor
        fields = ['id', 'nome_completo', 'cpf', 'telefone_principal',
                  'telefone_secundario', 'email', 'endereco_rua', 'endereco_numero',
                  'endereco_complemento', 'endereco_bairro', 'endereco_cidade',
                  'endereco_uf', 'endereco_cep', 'data_cadastro', 'observacoes', 'pacientes'
                  ]
        read_only_fields = ['id', 'data_cadastro']


class PacienteSerializer(serializers.ModelSerializer):
    tutor_nome_completo = serializers.CharField(
        source='tutor.nome_completo', read_only=True)
    idade_atual = serializers.CharField(source='idade', read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'nome', 'tutor', 'tutor_nome_completo', 'especie', 'raca',
            'data_nascimento', 'idade_atual', 'sexo', 'microchip', 'cor_pelagem',
            'peso_kg', 'data_cadastro', 'status', 'foto',
            'observacoes_clinicas', 'alergias_conhecidas'
        ]
        read_only_fields = ['id', 'data_cadastro',
                            'tutor_nome_completo', 'idade_atual']


class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinario
        fields = ['id', 'nome_completo', 'crmv']
        read_only_fields = ['id']


class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'
        read_only_fields = ['id', 'data_criacao_registro', 'data_ultima_modificacao',
                            'paciente_nome', 'tutor_nome', 'veterinario_nome']
