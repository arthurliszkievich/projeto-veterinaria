from rest_framework import viewsets, permissions
from .models import Tutor, Paciente
from .serializers import TutorSerializer, PacienteSerializer


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
