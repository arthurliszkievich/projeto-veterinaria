from rest_framework import viewsets, permissions
from .models import Tutor, Paciente, Veterinario, Consulta
from .serializers import TutorSerializer, PacienteSerializer, VeterinarioSerializer, ConsultaSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore


class TutorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Tutores.
    Permite listar, criar, atualizar e excluir Tutores.
    """
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter,
                       OrderingFilter]  # Adiciona os novos backends
    filterset_fields = ['cpf', 'email',
                        'endereco_cidade', 'endereco_uf', 'nome_completo']
    search_fields = ['nome_completo', 'cpf', 'email',
                     'observacoes', 'endereco_rua', 'endereco_bairro']  # Campos para busca textual
    ordering_fields = ['nome_completo', 'data_cadastro',
                       'endereco_cidade']  # Campos pelos quais se pode ordenar


class PacienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Pacientes.
    Permite listar, criar, atualizar e excluir Pacientes.
    """
    # queryset = Onde pega os dados
    queryset = Paciente.objects.all()
    # serializer_class = serializar e deserializar os dados
    serializer_class = PacienteSerializer
    # Permissões de acesso
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter,
                       OrderingFilter]  # Adiciona os novos backends
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
    search_fields = ['nome', 'raca', 'microchip', 'observacoes_clinicas',
                     'alergias_conhecidas', 'tutor__nome_completo']
    ordering_fields = ['nome', 'data_nascimento',
                       'especie', 'tutor__nome_completo', 'peso_kg']
    ordering = ['nome']


class VeterinarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Veterinários.
    Permite listar, criar, atualizar e excluir Veterinários.
    """
    queryset = Veterinario.objects.all()
    serializer_class = VeterinarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['crmv', 'nome_completo']
    search_fields = ['nome_completo', 'crmv']
    ordering_fields = ['nome_completo']
    ordering = ['nome_completo']


class ConsultaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar as Consultas.
    Permite listar, criar, atualizar e excluir Consultas.
    """
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'paciente': ['exact'],
        'paciente__nome': ['icontains'],
        'paciente__tutor': ['exact'],
        'paciente__tutor__nome_completo': ['icontains'],
        'veterinario_responsavel': ['exact'],
        'veterinario_responsavel__nome_completo': ['icontains'],
        'tipo_consulta': ['exact'],
        # ['exact', 'gte', 'lte'], # 'gte' = maior ou igual, 'lte' = menor ou igual
        'data_hora_agendamento': ['date', 'date__gte', 'date__lte', 'year', 'month', 'day'],
    }
    search_fields = [
        'paciente__nome',
        'paciente__tutor__nome_completo',
        'veterinario_responsavel__nome_completo',
        'queixa_principal_tutor',
        'suspeitas_diagnosticas',
        'diagnostico_definitivo',
        'tratamento_prescrito'
    ]
    ordering_fields = ['data_hora_agendamento', 'paciente__nome',
                       'veterinario_responsavel__nome_completo']

    ordering = ['-data_criacao_registro']  # Mantém sua ordenação padrão
