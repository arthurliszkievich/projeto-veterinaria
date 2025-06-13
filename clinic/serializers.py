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


class ConsultaSerializer(serializers.ModelSerializer):
    """
    Serializa os dados de Consulta para a API.
    - Usa campos `read_only` para exibir nomes relacionados (paciente, tutor, etc).
    - Lida com campos ManyToMany (sintomas, diagnósticos) de forma explícita.
    """

    # --- CAMPOS DE LEITURA (para enriquecer a resposta do GET) ---
    paciente_nome = serializers.CharField(
        source='paciente.nome', read_only=True)
    tutor_nome = serializers.CharField(
        source='paciente.tutor.nome_completo', read_only=True)
    veterinario_responsavel_nome = serializers.CharField(
        source='veterinario_responsavel.nome_completo', read_only=True)

    # --- TRATAMENTO PARA CAMPOS MANY-TO-MANY ---

    # 1. Sintomas:
    #    - Para GET, exibe os detalhes completos de cada sintoma.
    #    - Para POST/PUT, espera uma lista de IDs no campo `sintomas_apresentados`.
    sintomas_apresentados = serializers.PrimaryKeyRelatedField(
        queryset=Sintoma.objects.all(),
        many=True,
        required=False  # Torna o campo opcional
    )

    # 2. Diagnósticos Suspeitos:
    #    - Para GET, exibe os IDs. Para exibir detalhes, seria necessário aninhar o DoencaSerializer.
    #    - Para POST/PUT, espera uma lista de IDs no campo `diagnosticos_suspeitos`.
    diagnosticos_suspeitos = serializers.PrimaryKeyRelatedField(
        queryset=Doenca.objects.all(),
        many=True,
        required=False
    )

    # 3. Diagnósticos Definitivos:
    #    - Similar aos outros, lida com a relação M2M para diagnósticos confirmados.
    diagnosticos_definitivos = serializers.PrimaryKeyRelatedField(
        queryset=Doenca.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Consulta
        fields = [
            'id',
            'paciente',  # Usado para escrita (recebe o ID)
            'veterinario_responsavel',  # Usado para escrita (recebe o ID)

            # Campos de leitura para nomes
            'paciente_nome',
            'tutor_nome',
            'veterinario_responsavel_nome',

            # Campos diretos do modelo
            'data_hora_agendamento', 'tipo_consulta', 'queixa_principal_tutor',
            'historico_doenca_atual',

            # Anamnese
            'anamnese_sistema_respiratorio', 'anamnese_sistema_cardiovascular',
            'anamnese_sistema_digestorio', 'anamnese_sistema_urinario',
            'anamnese_sistema_reprodutor', 'anamnese_sistema_locomotor',
            'anamnese_sistema_neurologico', 'anamnese_pele_anexos', 'anamnese_olhos',

            # Exame Físico Geral
            'temperatura_celsius', 'frequencia_cardiaca_bpm', 'frequencia_respiratoria_mpm',
            'tpc_segundos', 'hidratacao_status', 'escore_condicao_corporal',
            'exame_postura', 'exame_nivel_consciencia', 'exame_linfonodos_obs',
            'exame_mucosas_obs', 'exame_pulso_ppm', 'observacoes_exame_fisico_geral',

            # Exame Físico Específico
            'examefisico_sistema_respiratorio', 'examefisico_sistema_cardiovascular',
            'examefisico_sistema_digestorio', 'examefisico_sistema_urinario',
            'examefisico_sistema_reprodutor', 'examefisico_sistema_locomotor',
            'examefisico_sistema_neurologico', 'examefisico_pele_anexos',
            'examefisico_olhos', 'examefisico_ouvidos',

            # Campos de Tratamento e Prognóstico
            'exames_complementares_solicitados', 'tratamento_prescrito',
            'procedimentos_realizados', 'prognostico', 'instrucoes_para_tutor',
            'data_proximo_retorno',

            # Campos ManyToMany
            'sintomas_apresentados',
            'diagnosticos_suspeitos',
            'diagnosticos_definitivos',

            # Datas de controle
            'data_criacao_registro', 'data_ultima_modificacao'
        ]

        # Campos que são apenas para leitura e não podem ser modificados via API.
        read_only_fields = [
            'id',
            'paciente_nome',
            'tutor_nome',
            'veterinario_responsavel_nome',
            'data_criacao_registro',
            'data_ultima_modificacao',
        ]

    def to_representation(self, instance):
        """
        Customiza a representação de saída (GET) para aninhar os detalhes
        dos campos ManyToMany.
        """
        # Pega a representação padrão do serializer
        representation = super().to_representation(instance)

        # Substitui os IDs dos sintomas pelos objetos completos serializados
        representation['sintomas_apresentados'] = SintomaSerializer(
            instance.sintomas_apresentados.all(), many=True).data
        representation['diagnosticos_suspeitos'] = DoencaSerializer(
            instance.diagnosticos_suspeitos.all(), many=True).data
        representation['diagnosticos_definitivos'] = DoencaSerializer(
            instance.diagnosticos_definitivos.all(), many=True).data

        return representation


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
