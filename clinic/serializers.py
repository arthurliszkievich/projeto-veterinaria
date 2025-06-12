from rest_framework import serializers
from .models import Tutor, Paciente, Veterinario, Consulta, Sintoma
from validate_docbr import CPF  # Importe a classe CPF para validação


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
    # --- Campos Adicionais para Leitura (Facilitar a visualização na API GET) ---

    # Mostra o nome do paciente associado a esta consulta.
    # 'source' aponta para o atributo 'nome' do objeto 'paciente' relacionado.
    # 'read_only=True' significa que este campo é apenas para visualização, não para escrita.
    paciente_nome = serializers.CharField(
        source='paciente.nome', read_only=True)

    # Mostra o nome completo do tutor do paciente associado a esta consulta.
    # Navega através de 'paciente' para 'tutor' e depois para 'nome_completo'.
    tutor_nome = serializers.CharField(
        source='paciente.tutor.nome_completo', read_only=True)

    # Mostra o nome completo do veterinário responsável.
    # 'allow_null=True' é importante se 'veterinario_responsavel' pode ser nulo no modelo.
    veterinario_nome = serializers.CharField(
        source='veterinario_responsavel.nome_completo',
        read_only=True,
        allow_null=True
    )

    # --- Campos para Relacionamento ManyToMany com Sintomas ---

    # Para LEITURA (GET): Exibe os detalhes completos de cada sintoma associado.
    # Usa o SintomaSerializer para formatar cada objeto Sintoma.
    # 'many=True' porque uma consulta pode ter vários sintomas.
    # 'read_only=True' porque este campo é apenas para exibir os sintomas; a escrita será feita por outro campo.
    # O nome 'sintomas_apresentados' aqui corresponde ao nome do campo ManyToMany no modelo Consulta.
    sintomas_apresentados = SintomaSerializer(many=True, read_only=True)

    # Para ESCRITA (POST/PUT/PATCH): Permite enviar uma lista de IDs de Sintomas.
    # Este campo não aparecerá na resposta GET por causa do 'write_only=True'.
    # 'queryset' é necessário para que o PrimaryKeyRelatedField valide os IDs enviados.
    # 'source' mapeia este campo de escrita para o campo 'sintomas_apresentados' do modelo Consulta.
    # Assim, quando você envia IDs para 'sintoma_ids_para_escrita', o DRF atualiza o
    # relacionamento 'sintomas_apresentados' no modelo.
    # 'required=False' torna o campo opcional ao criar/atualizar uma consulta.
    sintoma_ids_para_escrita = serializers.PrimaryKeyRelatedField(
        queryset=Sintoma.objects.all(),
        source='sintomas_apresentados',  # Mapeia para o campo ManyToMany do modelo
        many=True,
        required=False,
        write_only=True,  # Só usado para criar/atualizar, não aparece na resposta GET
        # Label para a API Navegável
        label="IDs dos Sintomas Apresentados (para escrita)"
    )

    class Meta:
        model = Consulta
        # Lista explícita de TODOS os campos que você quer na sua API.
        # Inclui:
        #   1. Campos diretos do modelo Consulta.
        #   2. Nomes dos campos customizados de leitura definidos acima (paciente_nome, etc.).
        #   3. O campo 'sintomas_apresentados' (que usará o SintomaSerializer para leitura).
        #   4. O campo 'sintoma_ids_para_escrita' (que será usado para entrada de dados).
        fields = [
            'id',
            # ForeignKey para Paciente (envia/recebe ID do paciente)
            'paciente',
            'paciente_nome',  # Campo de leitura
            'tutor_nome',    # Campo de leitura
            # ForeignKey para Veterinario (envia/recebe ID do veterinário)
            'veterinario_responsavel',
            'veterinario_nome',        # Campo de leitura
            'data_hora_agendamento',
            'tipo_consulta',

            'queixa_principal_tutor',
            'historico_doenca_atual',

            # Anamnese Especial
            'anamnese_sistema_respiratorio',
            'anamnese_sistema_cardiovascular',
            'anamnese_sistema_digestorio',
            'anamnese_sistema_urinario',
            'anamnese_sistema_reprodutor',
            'anamnese_sistema_locomotor',
            'anamnese_sistema_neurologico',
            'anamnese_pele_anexos',
            'anamnese_olhos',

            # Exame Físico Geral
            'temperatura_celsius',
            'frequencia_cardiaca_bpm',
            'frequencia_respiratoria_mpm',
            'tpc_segundos',
            'hidratacao_status',
            'escore_condicao_corporal',
            'exame_postura',
            'exame_nivel_consciencia',
            'exame_linfonodos_obs',
            'exame_mucosas_obs',
            'exame_pulso_ppm',
            'observacoes_exame_fisico_geral',

            # Exame Físico Específico
            'examefisico_sistema_respiratorio',
            'examefisico_sistema_cardiovascular',
            'examefisico_sistema_digestorio',
            'examefisico_sistema_urinario',
            'examefisico_sistema_reprodutor',
            'examefisico_sistema_locomotor',
            'examefisico_sistema_neurologico',
            'examefisico_pele_anexos',
            'examefisico_olhos',
            'examefisico_ouvidos',

            # Para LEITURA (mostrará os detalhes via SintomaSerializer)
            'sintomas_apresentados',
            # Para ESCRITA (receberá a lista de IDs dos sintomas)
            'sintoma_ids_para_escrita',

            'suspeitas_diagnosticas',
            'exames_complementares_solicitados',
            'diagnostico_definitivo',
            'tratamento_prescrito',
            'procedimentos_realizados',

            'prognostico',
            'instrucoes_para_tutor',
            'data_proximo_retorno',

            'data_criacao_registro',
            'data_ultima_modificacao'
        ]

        # Lista de campos que são apenas para leitura e não podem ser modificados via API.
        # Inclui o 'id', campos de data automáticos, e os campos de nome/detalhe que são derivados.
        read_only_fields = [
            'id',
            'data_criacao_registro',
            'data_ultima_modificacao',
            'paciente_nome',
            'tutor_nome',
            'veterinario_nome',
            # 'sintomas_apresentados' já é read_only por causa da definição do campo
            # SintomaSerializer(..., read_only=True) acima.
        ]
