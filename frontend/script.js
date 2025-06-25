document.addEventListener('DOMContentLoaded', function() {
    const apiBaseUrl = 'http://localhost:8000/api/clinic';
    const sintomasCheckboxesContainer = document.getElementById('listaSintomasCheckboxes');
    const novaConsultaForm = document.getElementById('novaConsultaForm');
    const listaDiagnosticosSugeridosEl = document.getElementById('listaDiagnosticosSugeridos');
    const mensagemErroEl = document.getElementById('mensagemErro');

    // --- FUNÇÃO PARA PEGAR O TOKEN DE AUTENTICAÇÃO ---
    function getAuthToken() {
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUxNDYzMzM1LCJpYXQiOjE3NTA4NTg1MzUsImp0aSI6ImE5Njc4NjM5ZmZhNDQ5N2Y4YWE1ZDBjMThiOTRhNWEyIiwidXNlcl9pZCI6Mn0.1YC5O5Jg784ZlB-B0ilrnSIXo2LYb7jQD9BWpDorFhE"; // !!! SUBSTITUA ESTE VALOR !!!
    }

    // --- FUNÇÃO RECURSIVA PARA CARREGAR TODAS AS PÁGINAS DE SINTOMAS ---
    async function carregarTodasPaginasSintomas(url, acumuladorSintomas = []) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // Se sua API de sintomas for protegida (improvável para GET de lista pública):
                    // 'Authorization': `Bearer ${getAuthToken()}` 
                }
            });

            if (!response.ok) {
                throw new Error(`Erro ao buscar página de sintomas: ${response.status} ${response.statusText} (URL: ${url})`);
            }

            const data = await response.json();
            const sintomasDaPagina = data.results || data; // Lida com DRF paginado ou não
            
            if (Array.isArray(sintomasDaPagina)) {
                acumuladorSintomas.push(...sintomasDaPagina);
            } else {
                console.warn("Resposta da API de sintomas (ou de uma página) não continha um array em 'results' ou como raiz:", data);
            }


            if (data.next) { // Se existe uma próxima página
                console.log(`Carregando próxima página de sintomas: ${data.next}`);
                return await carregarTodasPaginasSintomas(data.next, acumuladorSintomas);
            } else {
                return acumuladorSintomas; // Retorna todos os sintomas acumulados
            }

        } catch (error) {
            console.error('Falha ao carregar uma página de sintomas:', error);
            throw error; 
        }
    }

    // --- CARREGAR SINTOMAS DA API E CRIAR CHECKBOXES ---
    async function carregarSintomas() {
        const urlInicialSintomas = `${apiBaseUrl}/sintomas/`;

        try {
            sintomasCheckboxesContainer.innerHTML = '<p>Carregando todos os sintomas...</p>';
            const todosOsSintomas = await carregarTodasPaginasSintomas(urlInicialSintomas);

            sintomasCheckboxesContainer.innerHTML = ''; 
            if (todosOsSintomas.length === 0) {
                sintomasCheckboxesContainer.innerHTML = '<p>Nenhum sintoma cadastrado ou encontrado.</p>';
                return;
            }

            todosOsSintomas.sort((a, b) => a.nome.localeCompare(b.nome));

            todosOsSintomas.forEach(sintoma => {
                const div = document.createElement('div');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `sintoma-${sintoma.id}`;
                checkbox.name = 'sintomas_apresentados_checkboxes'; // Nome para os inputs no HTML
                checkbox.value = sintoma.id;

                const label = document.createElement('label');
                label.htmlFor = `sintoma-${sintoma.id}`;
                label.textContent = sintoma.nome; 

                div.appendChild(checkbox);
                div.appendChild(label);
                sintomasCheckboxesContainer.appendChild(div);
            });

        } catch (error) {
            console.error('Falha ao carregar e processar todos os sintomas:', error);
            sintomasCheckboxesContainer.innerHTML = `<p class="error-message">Não foi possível carregar os sintomas: ${error.message}</p>`;
        }
    }

    // --- LIDAR COM O ENVIO DO FORMULÁRIO ---
    novaConsultaForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        mensagemErroEl.textContent = '';
        listaDiagnosticosSugeridosEl.innerHTML = '';

        const formData = new FormData(novaConsultaForm);
        
        // --- Coleta dos dados do formulário ---
        const pacienteId = formData.get('pacienteId');
        const veterinarioId = formData.get('veterinarioId');
        const queixaPrincipal = formData.get('queixaPrincipal');
        const historicoDoencaAtual = formData.get('historicoDoencaAtual');
        const temperaturaCelsius = formData.get('temperaturaCelsius');

        const sintomasSelecionadosIds = [];
        document.querySelectorAll('input[name="sintomas_apresentados_checkboxes"]:checked').forEach(checkbox => {
            sintomasSelecionadosIds.push(parseInt(checkbox.value));
        });

        // --- Montagem do Payload para a API ---
        const payload = {
            paciente: parseInt(pacienteId), // O serializer espera o ID (FK)
            veterinario_responsavel: parseInt(veterinarioId), // O serializer espera o ID (FK)
            queixa_principal_tutor: queixaPrincipal,
            historico_doenca_atual: historicoDoencaAtual,
            sintomas_apresentados_ids: sintomasSelecionadosIds 
        };

        if (temperaturaCelsius && temperaturaCelsius.trim() !== '') {
            payload.temperatura_celsius = temperaturaCelsius;
        }
        
        // Serão adicionados outros campos do seu modelo Consulta aqui)


        console.log('Enviando payload para /consultas/:', JSON.stringify(payload));

        try {
            const authToken = getAuthToken();
            if (!authToken || authToken === "COLE_SEU_NOVO_TOKEN_JWT_AQUI") {
                alert('Token de autenticação não configurado ou inválido em script.js. Por favor, gere um novo token e atualize.');
                return; 
            }

            const response = await fetch(`${apiBaseUrl}/consultas/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(payload)
            });

            const responseData = await response.json();

            if (!response.ok) {
                console.error('Erro da API ao criar consulta:', responseData);
                let errorMsg = `Erro ao salvar consulta: ${response.status} - ${response.statusText}. `;
                if (responseData && typeof responseData === 'object') {
                    for (const key in responseData) {
                        // Formata melhor os erros de validação do DRF
                        if (Array.isArray(responseData[key])) {
                            errorMsg += `\n${key}: ${responseData[key].join('; ')}`;
                        } else {
                            errorMsg += `\n${key}: ${responseData[key]}`;
                        }
                    }
                }
                throw new Error(errorMsg.trim());
            }

            console.log('Consulta criada com sucesso:', responseData);
            // O nome do campo na resposta para os diagnósticos suspeitos ordenados
            const diagnosticosSuspeitos = responseData.diagnosticos_suspeitos || [];

            if (diagnosticosSuspeitos.length > 0) {
                diagnosticosSuspeitos.forEach(diag => {
                    const li = document.createElement('li');
                    li.textContent = diag.nome; 
                    listaDiagnosticosSugeridosEl.appendChild(li);
                });
            } else {
                listaDiagnosticosSugeridosEl.innerHTML = '<li>Nenhum diagnóstico suspeito foi sugerido com base nos sintomas fornecidos.</li>';
            }

        } catch (error) {
            console.error('Falha ao enviar consulta ou processar resposta:', error);
            mensagemErroEl.textContent = error.message;
        }
    });

    // --- INICIALIZAÇÃO ---
    carregarSintomas();
});