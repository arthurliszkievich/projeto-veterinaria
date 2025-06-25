from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from .models import Tutor, Paciente, Veterinario, Consulta, Sintoma, Doenca
from .serializers import (TutorSerializer, PacienteSerializer,
                          VeterinarioSerializer, ConsultaSerializer, SintomaSerializer, DoencaSerializer)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from .services import sugerir_diagnosticos


class TutorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Tutores.
    Permite listar, criar, atualizar e excluir Tutores.
    """

    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]  # Adiciona os novos backends
    filterset_fields = [
        "cpf", "email", "endereco_cidade", "endereco_uf", "nome_completo",]
    search_fields = ["nome_completo", "cpf", "email",
                     "observacoes", "endereco_rua", "endereco_bairro",]
    ordering_fields = ["nome_completo", "data_cadastro", "endereco_cidade",]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            # Captura os pacientes que estão protegendo o tutor
            pacientes_protegidos = list(e.protected_objects)
            nomes_pacientes = [p.nome for p in pacientes_protegidos]

            return Response(
                {
                    "detail": "Não é possível excluir o tutor porque existem pacientes associados.",
                    "pacientes": nomes_pacientes
                },
                status=status.HTTP_400_BAD_REQUEST
            )


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


class SintomaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os Sintomas.
    Permite listar, criar, atualizar e excluir Sintomas.
    """
    queryset = Sintoma.objects.all()
    serializer_class = SintomaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        # Permite nome exato e "contém" (case-insensitive)
        'nome': ['exact', 'icontains'],
        'descricao': ['icontains']
    }
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'id']
    ordering = ['nome']


class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all().select_related(
        'paciente__tutor', 'veterinario_responsavel'
    ).prefetch_related(  # Otimiza queries para M2M na listagem/detalhe
        'sintomas_apresentados', 'diagnosticos_suspeitos', 'diagnosticos_definitivos'
    )
    serializer_class = ConsultaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'paciente': ['exact'],
        'paciente__nome': ['icontains'],
        'paciente__tutor__nome_completo': ['icontains'],
        'veterinario_responsavel__nome_completo': ['icontains'],
        'tipo_consulta': ['exact'],
        'data_hora_agendamento': ['date', 'date__gte', 'date__lte', 'year', 'month', 'day'],
    }
    search_fields = [
        'paciente__nome', 'paciente__tutor__nome_completo', 'veterinario_responsavel__nome_completo',
        'queixa_principal_tutor', 'historico_doenca_atual',
        'sintomas_apresentados__nome',
        'diagnosticos_suspeitos__nome',  # Busca nos diagnósticos que foram salvos
        'diagnosticos_definitivos__nome',
        'tratamento_prescrito'
    ]
    # Campos para ordenação na API (ex: ?ordering=data_hora_agendamento)
    ordering_fields = ['data_hora_agendamento',
                       'paciente__nome', 'tipo_consulta']
    ordering = ['-data_criacao_registro']  # Ordenação padrão da listagem

    def _processar_sugestoes_diagnostico(self, consulta_instance):
        """Método auxiliar para calcular e anexar sugestões de diagnóstico."""
        sintomas_apresentados_objs = list(
            consulta_instance.sintomas_apresentados.all())

        doencas_sugeridas_ordenadas = []
        if sintomas_apresentados_objs:
            doencas_sugeridas_ordenadas = sugerir_diagnosticos(
                sintomas_apresentados_objs)
            if doencas_sugeridas_ordenadas:
                # Salva a relação no banco
                consulta_instance.diagnosticos_suspeitos.set(
                    doencas_sugeridas_ordenadas)
            else:
                consulta_instance.diagnosticos_suspeitos.clear()
        else:
            consulta_instance.diagnosticos_suspeitos.clear()

        # Anexa a lista ORDENADA à instância para o SerializerMethodField usar na RESPOSTA
        setattr(consulta_instance, '_diagnosticos_sugeridos_ordenados',
                doencas_sugeridas_ordenadas)

    def perform_create(self, serializer):
        # Salva a consulta e os campos M2M enviados via _ids (sintomas_apresentados_ids, etc.)
        consulta = serializer.save()
        # Processa e anexa as sugestões de diagnóstico
        self._processar_sugestoes_diagnostico(consulta)

    def perform_update(self, serializer):
        consulta = serializer.save()
        self._processar_sugestoes_diagnostico(consulta)

    # Para garantir que a lista ordenada seja anexada também na resposta de retrieve (GET de um item)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Recalcula e anexa as sugestões para garantir que a resposta tenha a ordem correta,
        # mesmo que os sintomas da consulta tenham sido alterados fora do fluxo de create/update da API.
        self._processar_sugestoes_diagnostico(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DoencaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite que doenças sejam visualizadas ou editadas.
    """
    queryset = Doenca.objects.all().prefetch_related('sintomas_associados')
    serializer_class = DoencaSerializer
    # Exemplo: todos podem ver, apenas autenticados podem editar
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
