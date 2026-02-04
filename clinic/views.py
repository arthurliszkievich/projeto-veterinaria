import logging

from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .constants import (
    DEFAULT_PAGE_SIZE,
    ERROR_GENERIC,
    ERROR_INTEGRITY_ERROR,
    ERROR_TUTOR_PROTECTED_DELETE,
    MAX_PAGE_SIZE,
)
from .models import Consulta, Doenca, Paciente, Sintoma, Tutor, Veterinario
from .serializers import (
    ConsultaSerializer,
    DoencaSerializer,
    PacienteSerializer,
    SintomaSerializer,
    TutorSerializer,
    UserRegisterSerializer,
    UserSerializer,
    VeterinarioSerializer,
)
from .services import ConsultaService

# Configurar logger
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginação padrão para a API.

    Configurações:
    - Tamanho padrão: 20 itens por página
    - Tamanho máximo: 100 itens por página
    - Permite ao cliente definir o tamanho via query param 'page_size'
    """

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE


class TutorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Tutores.

    Endpoints:
    - GET /tutores/ - Lista todos os tutores (com paginação)
    - POST /tutores/ - Cria um novo tutor
    - GET /tutores/{id}/ - Detalha um tutor específico
    - PUT/PATCH /tutores/{id}/ - Atualiza um tutor
    - DELETE /tutores/{id}/ - Remove um tutor (se não houver pacientes)

    Filtros disponíveis:
    - cpf, email, endereco_cidade, endereco_uf, nome_completo

    Busca (search):
    - nome_completo, cpf, email, observacoes, endereco_rua, endereco_bairro

    Ordenação (ordering):
    - nome_completo, data_cadastro, endereco_cidade
    """

    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = [
        "cpf",
        "email",
        "endereco_cidade",
        "endereco_uf",
        "nome_completo",
    ]
    search_fields = [
        "nome_completo",
        "cpf",
        "email",
        "observacoes",
        "endereco_rua",
        "endereco_bairro",
    ]
    ordering_fields = [
        "nome_completo",
        "data_cadastro",
        "endereco_cidade",
    ]

    def destroy(self, request, *args, **kwargs):
        """
        Remove um tutor do sistema.

        Se o tutor tiver pacientes associados, a operação é bloqueada
        e uma mensagem informativa é retornada com a lista de pacientes.

        Returns:
            Response: Confirmação de exclusão ou erro com detalhes
        """
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            # Captura os pacientes que estão protegendo o tutor
            pacientes_protegidos = list(e.protected_objects)
            nomes_pacientes = [p.nome for p in pacientes_protegidos]  # type: ignore

            logger.warning(
                f"Tentativa de excluir tutor com pacientes associados: {nomes_pacientes}"
            )

            return Response(
                {"detail": ERROR_TUTOR_PROTECTED_DELETE, "pacientes": nomes_pacientes},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao excluir tutor: {str(e)}")
            return Response(
                {"detail": ERROR_INTEGRITY_ERROR}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao excluir tutor: {str(e)}")
            return Response(
                {"detail": ERROR_GENERIC}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Pacientes.

    Endpoints:
    - GET /pacientes/ - Lista todos os pacientes
    - POST /pacientes/ - Registra um novo paciente
    - GET /pacientes/{id}/ - Detalha um paciente específico
    - PUT/PATCH /pacientes/{id}/ - Atualiza informações do paciente
    - DELETE /pacientes/{id}/ - Remove um paciente

    Filtros disponíveis:
    - tutor, tutor__nome_completo, especie, raca, status, sexo, nome

    Ordenação padrão: nome (alfabética)
    """

    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "tutor": ["exact"],
        "tutor__nome_completo": ["icontains"],
        "especie": ["exact"],
        "raca": ["icontains"],
        "status": ["exact"],
        "sexo": ["exact"],
        "nome": ["icontains"],
    }
    search_fields = [
        "nome",
        "raca",
        "microchip",
        "observacoes_clinicas_relevantes",
        "alergias_conhecidas",
        "tutor__nome_completo",
    ]
    ordering_fields = [
        "nome",
        "data_nascimento",
        "especie",
        "tutor__nome_completo",
        "peso_kg",
    ]
    ordering = ["nome"]


class VeterinarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Veterinários.

    Endpoints:
    - GET /veterinarios/ - Lista todos os veterinários
    - POST /veterinarios/ - Cadastra um novo veterinário
    - GET /veterinarios/{id}/ - Detalha um veterinário específico
    - PUT/PATCH /veterinarios/{id}/ - Atualiza dados do veterinário
    - DELETE /veterinarios/{id}/ - Remove um veterinário
    """

    queryset = Veterinario.objects.all()
    serializer_class = VeterinarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["crmv", "nome_completo"]
    search_fields = ["nome_completo", "crmv"]
    ordering_fields = ["nome_completo"]
    ordering = ["nome_completo"]


class SintomaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Sintomas.

    Sintomas são utilizados para registrar manifestações clínicas
    e auxiliar no sistema de sugestão de diagnósticos.

    Endpoints:
    - GET /sintomas/ - Lista todos os sintomas
    - POST /sintomas/ - Cadastra um novo sintoma
    - GET /sintomas/{id}/ - Detalha um sintoma específico
    - PUT/PATCH /sintomas/{id}/ - Atualiza informações do sintoma
    - DELETE /sintomas/{id}/ - Remove um sintoma
    """

    queryset = Sintoma.objects.all()
    serializer_class = SintomaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {"nome": ["exact", "icontains"], "descricao": ["icontains"]}
    search_fields = ["nome", "descricao"]
    ordering_fields = ["nome", "id"]
    ordering = ["nome"]


class ConsultaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar as Consultas.

    Este é o endpoint principal para registro e acompanhamento de consultas veterinárias.
    Inclui sugestão automática de diagnósticos baseada nos sintomas apresentados.

    Endpoints:
    - GET /consultas/ - Lista todas as consultas
    - POST /consultas/ - Registra uma nova consulta
    - GET /consultas/{id}/ - Detalha uma consulta específica
    - PUT/PATCH /consultas/{id}/ - Atualiza informações da consulta
    - DELETE /consultas/{id}/ - Remove uma consulta

    Funcionalidades especiais:
    - Sugestão automática de diagnósticos com base em sintomas
    - Queries otimizadas com select_related e prefetch_related
    - Filtros avançados por paciente, veterinário, data e tipo
    """

    queryset = (
        Consulta.objects.all()
        .select_related("paciente__tutor", "veterinario_responsavel")
        .prefetch_related(
            "sintomas_apresentados",
            "diagnosticos_suspeitos",
            "diagnosticos_definitivos",
        )
    )
    serializer_class = ConsultaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "paciente": ["exact"],
        "paciente__nome": ["icontains"],
        "paciente__tutor__nome_completo": ["icontains"],
        "veterinario_responsavel__nome_completo": ["icontains"],
        "tipo_consulta": ["exact"],
        "data_hora_agendamento": [
            "date",
            "date__gte",
            "date__lte",
            "year",
            "month",
            "day",
        ],
    }
    search_fields = [
        "paciente__nome",
        "paciente__tutor__nome_completo",
        "veterinario_responsavel__nome_completo",
        "queixa_principal_tutor",
        "historico_doenca_atual",
        "sintomas_apresentados__nome",
        "diagnosticos_suspeitos__nome",
        "diagnosticos_definitivos__nome",
        "tratamento_prescrito",
    ]
    ordering_fields = ["data_hora_agendamento", "paciente__nome", "tipo_consulta"]
    ordering = ["-data_criacao_registro"]

    def __init__(self, *args, **kwargs):
        """
        Inicializa o ViewSet com injeção de dependência do serviço.

        Seguindo o princípio de Dependency Inversion (SOLID),
        a View depende de uma abstração (serviço) ao invés de
        implementação concreta de lógica de negócio.
        """
        super().__init__(*args, **kwargs)
        self.consulta_service = ConsultaService()

    def perform_create(self, serializer):
        """
        Cria uma nova consulta e delega o processamento para o serviço.

        A View agora é "fina" e apenas orquestra a chamada ao serviço,
        seguindo o princípio de Single Responsibility.

        Args:
            serializer: Serializer validado com os dados da consulta
        """
        logger.info(f"Dados recebidos: {serializer.validated_data.keys()}")
        if 'sintomas_apresentados' in serializer.validated_data:
            logger.info(f"Sintomas no payload: {len(serializer.validated_data['sintomas_apresentados'])}")
        
        consulta = serializer.save()
        logger.info(f"Nova consulta criada: ID {consulta.id}")
        logger.info(f"Sintomas após save: {consulta.sintomas_apresentados.count()}")
        self.consulta_service.processar_diagnosticos(consulta)
        logger.info(f"Processamento de diagnósticos concluído")

    def perform_update(self, serializer):
        """
        Atualiza uma consulta existente e delega o reprocessamento para o serviço.

        Args:
            serializer: Serializer validado com os dados atualizados
        """
        consulta = serializer.save()
        self.consulta_service.processar_diagnosticos(consulta)
        logger.info(f"Consulta atualizada: ID {consulta.id}")

    def retrieve(self, request, *args, **kwargs):
        """
        Recupera uma consulta específica com sugestões de diagnóstico recalculadas.

        Garante que a resposta sempre contenha as sugestões mais atualizadas,
        mesmo que os sintomas tenham sido alterados fora do fluxo da API.

        Returns:
            Response: Dados completos da consulta com diagnósticos sugeridos
        """
        instance = self.get_object()
        self.consulta_service.processar_diagnosticos(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DoencaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar as Doenças (Base de Conhecimento).

    As doenças são utilizadas como base de conhecimento para o sistema
    de sugestão de diagnósticos. Cada doença pode ter sintomas associados
    que são usados para calcular a probabilidade de diagnóstico.

    Endpoints:
    - GET /doencas/ - Lista todas as doenças cadastradas
    - POST /doencas/ - Cadastra uma nova doença
    - GET /doencas/{id}/ - Detalha uma doença específica
    - PUT/PATCH /doencas/{id}/ - Atualiza informações da doença
    - DELETE /doencas/{id}/ - Remove uma doença
    """

    queryset = Doenca.objects.all().prefetch_related("sintomas_associados")
    serializer_class = DoencaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination


# ==============================
# VIEWS DE AUTENTICAÇÃO
# ==============================


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """
    Endpoint para registro de novos usuários.

    Aceita:
    - username (obrigatório)
    - email (obrigatório)
    - password (obrigatório, mínimo 8 caracteres)
    - password2 (obrigatório, confirmação de senha)
    - first_name (opcional)
    - last_name (opcional)
    - user_type (opcional: cliente, funcionario, gerente)

    Retorna:
    - 201: Usuário criado com sucesso
    - 400: Erros de validação
    """
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user_data = UserSerializer(user).data
        return Response(
            {"message": "Usuário criado com sucesso!", "user": user_data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_user_info(request):
    """
    Endpoint para obter informações do usuário autenticado.

    Requer autenticação JWT.

    Retorna:
    - 200: Dados do usuário
    - 401: Não autenticado
    """
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Não autenticado."}, status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
