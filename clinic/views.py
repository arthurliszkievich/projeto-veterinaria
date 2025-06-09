from rest_framework import viewsets, permissions
from .models import Tutor, Paciente, Veterinario, Consulta
from .serializers import TutorSerializer, PacienteSerializer, VeterinarioSerializer, ConsultaSerializer


class TutorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Tutores.
    Permite listar, criar, atualizar e excluir Tutores.
    """
    queryset = Tutor.objects.all().order_by('nome_completo')
    serializer_class = TutorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filterset_fields = ['cpf', 'email',
                        'endereco_cidade', 'endereco_uf', 'nome_completo']


class PacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Pacientes.
    Permite listar, criar, atualizar e excluir Pacientes.
    """
    # queryset = Onde pega os dados
    queryset = Paciente.objects.all().order_by('nome')
    # serializer_class = serializar e deserializar os dados
    serializer_class = PacienteSerializer
    # Permissões de acesso
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filterset_fields = {
        'tutor': ['exact'],  # Filtra por ID exato do tutor
        # Filtra se nome do tutor contém (case-insensitive)
        'tutor__nome_completo': ['icontains'],
        'especie': ['exact'],  # Filtra por espécie exata
        'raca': ['icontains'],  # Filtra se raça contém (case-insensitive)
        'status': ['exact'],
        'sexo': ['exact'],
        # Filtra se nome do paciente contém (case-insensitive)
        'nome': ['icontains']
    }


class VeterinarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Veterinários.
    Permite listar, criar, atualizar e excluir Veterinários.
    """
    queryset = Veterinario.objects.all().order_by('nome_completo')
    serializer_class = VeterinarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filterset_fields = ['crmv', 'nome_completo']


class ConsultaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar as Consultas.
    Permite listar, criar, atualizar e excluir Consultas.
    """
    queryset = Consulta.objects.all().order_by(
        '-data_criacao_registro')
    serializer_class = ConsultaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filterset_fields = {

        'paciente': ['exact'],
        # Para filtrar pelo Tutor, você precisa ir através do Paciente:
        # Filtra pelo ID exato do Tutor do Paciente
        'paciente__tutor': ['exact'],
        # Exemplo: Filtra se o nome do Tutor contém (case-insensitive)
        'paciente__tutor__nome_completo': ['icontains'],

        # Filtra pelo ID exato do Veterinário Responsável
        'veterinario_responsavel': ['exact'],
        # Exemplo: Filtra se o nome do Veterinário contém
        'veterinario_responsavel__nome_completo': ['icontains'],

        # 'data_criacao_registro': ['exact', 'gte', 'lte'], # 'gte' = maior ou igual, 'lte' = menor ou igual
        # Ajustado para usar o lookup de data correto para ranges:
        'data_criacao_registro': ['exact', 'date__gte', 'date__lte', 'year', 'month', 'day'],

        # 'data_ultima_modificacao': ['exact', 'gte', 'lte'],
        # Ajustado para usar o lookup de data correto para ranges:
        'data_ultima_modificacao': ['exact', 'date__gte', 'date__lte', 'year', 'month', 'day'],

        # Outros filtros que você tinha e que são campos diretos de Consulta:
        'tipo_consulta': ['exact'],
    }

    search_fields = [
        'paciente__nome',
        'paciente__tutor__nome_completo',
        'veterinario_responsavel__nome_completo',
        'suspeitas_diagnosticas',
        'diagnostico_definitivo'
    ]
    ordering_fields = ['data_hora_agendamento', 'paciente__nome',
                       'veterinario_responsavel__nome_completo']

    ordering = ['-data_criacao_registro']  # Mantém sua ordenação padrão
