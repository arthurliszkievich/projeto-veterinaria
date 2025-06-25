# Certifique-se que Sintoma está importado
from .models import Consulta, Doenca, Sintoma
from rest_framework import serializers
from .models import Tutor, Paciente, Veterinario, Consulta, Sintoma, Doenca
from validate_docbr import CPF


class TutorSerializer(serializers.ModelSerializer):
    pacientes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Tutor
        fields = [
            "id", "nome_completo", "cpf", "telefone_principal", "telefone_secundario",
            "email", "endereco_rua", "endereco_numero", "endereco_complemento", "endereco_bairro",
            "endereco_cidade", "endereco_uf", "endereco_cep", "data_cadastro", "observacoes", "pacientes",
        ]
        read_only_fields = ["id", "data_cadastro"]

    def validate_cpf(self, value):
        """Valida se o CPF é válido usando a biblioteca validate_docbr"""
        cpf = CPF()

        # Remove formatação para validar apenas os números
        cpf_value = value.replace('.', '').replace('-', '')

        if not cpf.validate(cpf_value):
            raise serializers.ValidationError("CPF inválido")

        # Formata o CPF para o padrão XXX.XXX.XXX-XX antes de retornar
        return cpf.mask(cpf_value)


class PacienteSerializer(serializers.ModelSerializer):
    tutor_nome_completo = serializers.CharField(
        source='tutor.nome_completo', read_only=True)
    idade_atual = serializers.CharField(source='idade', read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ['id', 'data_cadastro']


class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinario
        fields = ['id', 'nome_completo', 'crmv']
        read_only_fields = ['id']


class SintomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sintoma
        fields = ['id', 'nome', 'descricao']


class DoencaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Doenca."""

    # Para LEITURA (GET): Mostra os objetos de sintomas completos.
    sintomas_associados = SintomaSerializer(many=True, read_only=True)

    # Para ESCRITA (POST/PUT): Aceita uma lista de IDs de sintomas.
    sintomas_ids = serializers.PrimaryKeyRelatedField(
        queryset=Sintoma.objects.all(),
        many=True,
        write_only=True,
        source='sintomas_associados',  # Mapeia este campo para o campo do modelo
        help_text="Lista de IDs dos sintomas a serem associados a esta doença."
    )

    class Meta:
        model = Doenca
        fields = [
            'id',
            'nome',
            'descricao',
            'sintomas_associados',  # Usado na resposta (GET)
            'sintomas_ids'          # Usado na requisição (POST/PUT)
        ]


class ConsultaSerializer(serializers.ModelSerializer):
    # Campos de leitura para nomes (melhoram a resposta do GET)
    paciente_nome = serializers.CharField(
        source='paciente.nome', read_only=True)
    tutor_nome = serializers.CharField(
        source='paciente.tutor.nome_completo', read_only=True)
    veterinario_responsavel_nome = serializers.CharField(
        source='veterinario_responsavel.nome_completo', read_only=True)

    # Campos ManyToMany para LEITURA (GET) - com detalhes e ordem correta para suspeitos
    sintomas_apresentados = SintomaSerializer(many=True, read_only=True)
    diagnosticos_suspeitos = serializers.SerializerMethodField(
        read_only=True)  # Garante ordem por score
    diagnosticos_definitivos = DoencaSerializer(many=True, read_only=True)

    # Campos ManyToMany para ESCRITA (POST/PUT) - espera lista de IDs
    sintomas_apresentados_ids = serializers.PrimaryKeyRelatedField(
        queryset=Sintoma.objects.all(), many=True, required=False,
        source='sintomas_apresentados', write_only=True
    )
    # Não vamos permitir escrita direta de diagnósticos suspeitos via API, será calculado
    diagnosticos_definitivos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Doenca.objects.all(), many=True, required=False,
        source='diagnosticos_definitivos', write_only=True
    )

    class Meta:
        model = Consulta
        fields = [
            'id',
            'paciente',  # FK para escrita
            'veterinario_responsavel',  # FK para escrita
            'paciente_nome',
            'tutor_nome',
            'veterinario_responsavel_nome',
            'data_hora_agendamento',
            'tipo_consulta',
            'queixa_principal_tutor',
            'historico_doenca_atual',
            # Anamnese Especial
            'anamnese_sistema_respiratorio', 'anamnese_sistema_cardiovascular',
            'anamnese_sistema_digestorio', 'anamnese_sistema_urinario',
            'anamnese_sistema_reprodutor', 'anamnese_sistema_locomotor',
            'anamnese_sistema_neurologico', 'anamnese_pele_anexos', 'anamnese_olhos',
            # Exame Físico Geral
            'temperatura_celsius', 'frequencia_cardiaca_bpm',
            'frequencia_respiratoria_mpm', 'tpc_segundos', 'hidratacao_status',
            'escore_condicao_corporal', 'exame_postura', 'exame_nivel_consciencia',
            'exame_linfonodos_obs', 'exame_mucosas_obs', 'exame_pulso_ppm',
            'observacoes_exame_fisico_geral',
            # Exame Físico Específico
            'examefisico_sistema_respiratorio', 'examefisico_sistema_cardiovascular',
            'examefisico_sistema_digestorio', 'examefisico_sistema_urinario',
            'examefisico_sistema_reprodutor', 'examefisico_sistema_locomotor',
            'examefisico_sistema_neurologico', 'examefisico_pele_anexos',
            'examefisico_olhos', 'examefisico_ouvidos',
            # Diagnósticos, Tratamento e Prognóstico
            'exames_complementares_solicitados',
            'tratamento_prescrito', 'procedimentos_realizados', 'prognostico',
            'instrucoes_para_tutor', 'data_proximo_retorno',
            # M2M para leitura (detalhes)
            'sintomas_apresentados',
            'diagnosticos_suspeitos',  # Virá do SerializerMethodField
            'diagnosticos_definitivos',
            # M2M para escrita (IDs)
            'sintomas_apresentados_ids',
            'diagnosticos_definitivos_ids',
            # Controle
            'data_criacao_registro',
            'data_ultima_modificacao'
        ]
        read_only_fields = (
            'id',
            'paciente_nome',
            'tutor_nome',
            'veterinario_responsavel_nome',
            'data_criacao_registro',
            'data_ultima_modificacao',
        )

    def get_diagnosticos_suspeitos(self, instance):
        # Retorna os diagnósticos suspeitos ordenados por score (anexados pelo ViewSet)
        if hasattr(instance, '_diagnosticos_sugeridos_ordenados'):
            return DoencaSerializer(instance._diagnosticos_sugeridos_ordenados, many=True, context=self.context).data
        # Fallback: se não foram calculados (ex: listagem geral), retorna do banco (ordem padrão)
        return DoencaSerializer(instance.diagnosticos_suspeitos.all(), many=True, context=self.context).data
