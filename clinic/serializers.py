from django.contrib.auth.models import User
from rest_framework import serializers

from .constants import (
    ERROR_TUTOR_CPF_INVALIDO,
    HELP_TEXT_DOENCA_SINTOMAS,
)
from .models import Consulta, Doenca, Paciente, Sintoma, Tutor, Veterinario
from .services import TutorService


class UserSerializer(serializers.ModelSerializer):
    """Serializer para retornar dados do usuário autenticado"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de novos usuários"""

    password2 = serializers.CharField(write_only=True, required=True)
    user_type = serializers.ChoiceField(
        choices=["cliente", "funcionario", "gerente"],
        default="funcionario",
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "user_type",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user_type = validated_data.pop("user_type", "funcionario")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
        )

        # Define permissões baseadas no tipo de usuário
        if user_type == "gerente":
            user.is_staff = True
            user.save()

        return user


class TutorSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Tutor.

    Delega validação de CPF para TutorService, seguindo o princípio
    de Single Responsibility (SRP). O Serializer apenas serializa/deserializa,
    sem lógica de negócio.
    """

    pacientes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Tutor
        fields = [
            "id",
            "nome_completo",
            "cpf",
            "telefone_principal",
            "telefone_secundario",
            "email",
            "endereco_rua",
            "endereco_numero",
            "endereco_complemento",
            "endereco_bairro",
            "endereco_cidade",
            "endereco_uf",
            "endereco_cep",
            "data_cadastro",
            "observacoes",
            "pacientes",
        ]
        read_only_fields = ["id", "data_cadastro"]

    def __init__(self, *args, **kwargs):
        """
        Inicializa o serializer com injeção de dependência do serviço.

        Seguindo o princípio de Dependency Inversion (SOLID).
        """
        super().__init__(*args, **kwargs)
        self.tutor_service = TutorService()

    def validate_cpf(self, value):
        """
        Valida e formata o CPF delegando para o serviço de negócio.

        O Serializer mantém apenas a interface de validação do DRF,
        mas delega toda a lógica para TutorService.

        Args:
            value (str): CPF a ser validado

        Returns:
            str: CPF formatado no padrão XXX.XXX.XXX-XX

        Raises:
            ValidationError: Se o CPF for inválido
        """
        is_valid, cpf_formatado = self.tutor_service.validar_e_formatar_cpf(
            value
        )

        if not is_valid:
            raise serializers.ValidationError(ERROR_TUTOR_CPF_INVALIDO)

        return cpf_formatado


class PacienteSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Paciente.

    Inclui campos calculados como nome do tutor e idade atual do paciente.
    """

    tutor_nome_completo = serializers.CharField(
        source="tutor.nome_completo", read_only=True
    )
    idade_atual = serializers.CharField(source="idade", read_only=True)

    class Meta:
        model = Paciente
        fields = "__all__"
        read_only_fields = ["id", "data_cadastro"]


class VeterinarioSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Veterinário."""

    class Meta:
        model = Veterinario
        fields = ["id", "nome_completo", "crmv"]
        read_only_fields = ["id"]


class SintomaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Sintoma."""

    class Meta:
        model = Sintoma
        fields = ["id", "nome", "descricao"]


class DoencaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Doença.

    Suporta dois modos de operação:
    - GET: Retorna sintomas associados completos (objetos)
    - POST/PUT: Aceita lista de IDs de sintomas para associação
    """

    # Para LEITURA (GET): Mostra os objetos de sintomas completos.
    sintomas_associados = SintomaSerializer(many=True, read_only=True)

    # Para ESCRITA (POST/PUT): Aceita uma lista de IDs de sintomas.
    sintomas_ids = serializers.PrimaryKeyRelatedField(
        queryset=Sintoma.objects.all(),
        many=True,
        write_only=True,
        source="sintomas_associados",
        help_text=HELP_TEXT_DOENCA_SINTOMAS,
    )

    class Meta:
        model = Doenca
        fields = [
            "id",
            "nome",
            "descricao",
            "sintomas_associados",  # Usado na resposta (GET)
            "sintomas_ids",  # Usado na requisição (POST/PUT)
        ]


class ConsultaSerializer(serializers.ModelSerializer):
    # Campos de leitura para nomes (melhoram a resposta do GET)
    paciente_nome = serializers.CharField(source="paciente.nome", read_only=True)
    tutor_nome = serializers.CharField(
        source="paciente.tutor.nome_completo", read_only=True
    )
    veterinario_responsavel_nome = serializers.CharField(
        source="veterinario_responsavel.nome_completo", read_only=True
    )

    # Campos ManyToMany para LEITURA (GET) - com detalhes e ordem correta para suspeitos
    sintomas_apresentados = SintomaSerializer(many=True, read_only=True)
    diagnosticos_suspeitos = serializers.SerializerMethodField(
        read_only=True
    )  # Garante ordem por score
    diagnosticos_definitivos = DoencaSerializer(many=True, read_only=True)

    # Campos ManyToMany para ESCRITA (POST/PUT) - espera lista de IDs
    sintomas_apresentados_ids = serializers.PrimaryKeyRelatedField(
        queryset=Sintoma.objects.all(),
        many=True,
        required=False,
        source="sintomas_apresentados",
        write_only=True,
    )
    # Não vamos permitir escrita direta de diagnósticos suspeitos via API, será calculado
    diagnosticos_definitivos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Doenca.objects.all(),
        many=True,
        required=False,
        source="diagnosticos_definitivos",
        write_only=True,
    )

    class Meta:
        model = Consulta
        fields = [
            "id",
            "paciente",  # FK para escrita
            "veterinario_responsavel",  # FK para escrita
            "paciente_nome",
            "tutor_nome",
            "veterinario_responsavel_nome",
            "data_hora_agendamento",
            "tipo_consulta",
            "queixa_principal_tutor",
            "historico_doenca_atual",
            # Anamnese Especial
            "anamnese_sistema_respiratorio",
            "anamnese_sistema_cardiovascular",
            "anamnese_sistema_digestorio",
            "anamnese_sistema_urinario",
            "anamnese_sistema_reprodutor",
            "anamnese_sistema_locomotor",
            "anamnese_sistema_neurologico",
            "anamnese_pele_anexos",
            "anamnese_olhos",
            # Exame Físico Geral
            "temperatura_celsius",
            "frequencia_cardiaca_bpm",
            "frequencia_respiratoria_mpm",
            "tpc_segundos",
            "hidratacao_status",
            "escore_condicao_corporal",
            "exame_postura",
            "exame_nivel_consciencia",
            "exame_linfonodos_obs",
            "exame_mucosas_obs",
            "exame_pulso_ppm",
            "observacoes_exame_fisico_geral",
            # Exame Físico Específico
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
            # Diagnósticos, Tratamento e Prognóstico
            "exames_complementares_solicitados",
            "tratamento_prescrito",
            "procedimentos_realizados",
            "prognostico",
            "instrucoes_para_tutor",
            "data_proximo_retorno",
            # M2M para leitura (detalhes)
            "sintomas_apresentados",
            "diagnosticos_suspeitos",  # Virá do SerializerMethodField
            "diagnosticos_definitivos",
            # M2M para escrita (IDs)
            "sintomas_apresentados_ids",
            "diagnosticos_definitivos_ids",
            # Controle
            "data_criacao_registro",
            "data_ultima_modificacao",
        ]
        read_only_fields = (
            "id",
            "paciente_nome",
            "tutor_nome",
            "veterinario_responsavel_nome",
            "data_criacao_registro",
            "data_ultima_modificacao",
        )

    def get_diagnosticos_suspeitos(self, instance):
        # Retorna os diagnósticos suspeitos ordenados por score (anexados pelo ViewSet)
        if hasattr(instance, "_diagnosticos_sugeridos_ordenados"):
            doencas = instance._diagnosticos_sugeridos_ordenados
            resultado = []
            for doenca in doencas:
                doenca_data = DoencaSerializer(doenca, context=self.context).data
                # Adiciona o score se estiver disponível
                if hasattr(doenca, "_score"):
                    doenca_data["score"] = round(doenca._score, 2)
                    doenca_data["porcentagem"] = f"{round(doenca._score, 1)}%"
                resultado.append(doenca_data)
            return resultado
        # Fallback: se não foram calculados (ex: listagem geral), retorna do banco (ordem padrão)
        return DoencaSerializer(
            instance.diagnosticos_suspeitos.all(), many=True, context=self.context
        ).data
