document.addEventListener('DOMContentLoaded', () => {
    const apiBaseUrl = 'http://localhost:8000/api/v1';
    const apiTokenUrl = 'http://localhost:8000/api/v1/token/';
    const apiRegisterUrl = 'http://localhost:8000/api/v1/auth/register/';
    const apiUserUrl = 'http://localhost:8000/api/v1/auth/user/';

    // ===============================================
    //  SEÇÃO 1: LÓGICA DE AUTENTICAÇÃO E ROTEAMENTO
    // ===============================================

    function getAuthToken() {
        return localStorage.getItem('accessToken');
    }

    function setUserType(type) {
        localStorage.setItem('userType', type);
    }

    function getUserType() {
        return localStorage.getItem('userType');
    }

    function logout() {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userType');
        localStorage.removeItem('userName');
        window.location.href = '/';
    }

    // Roteamento baseado no caminho da URL (funciona com Django)
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').filter(Boolean).pop() || 'home';

    // Páginas públicas que não precisam de autenticação
    const publicPages = [
        '', 'home',
        'login', 'registro',
        'login-cliente', 'login-funcionario', 'login-gerente',
        'registro-cliente', 'registro-funcionario', 'registro-gerente',
        // Mantém compatibilidade com .html (caso necessário)
        'index.html', 'login.html', 'registro.html',
        'login-cliente.html', 'login-funcionario.html', 'login-gerente.html',
        'registro-cliente.html', 'registro-funcionario.html', 'registro-gerente.html'
    ];

    // Guarda de autenticação: se não estiver em página pública e não tiver token, redireciona para o login
    if (!publicPages.includes(currentPage) && !getAuthToken()) {
        window.location.href = '/';
    }

    // ===============================================
    //  SEÇÃO 2: LÓGICA ESPECÍFICA DAS PÁGINAS DE LOGIN
    // ===============================================
    if (
        currentPage === 'login' ||
        currentPage === 'login-cliente' ||
        currentPage === 'login-funcionario' ||
        currentPage === 'login-gerente' ||
        // Compatibilidade com .html
        currentPage === 'login.html' ||
        currentPage === 'login-cliente.html' ||
        currentPage === 'login-funcionario.html' ||
        currentPage === 'login-gerente.html'
    ) {
        const loginForm = document.getElementById('loginForm');

        if (getAuthToken()) {
            // Redireciona baseado no tipo de usuário salvo
            const userType = getUserType();
            if (userType === 'gerente') {
                window.location.href = '/dashboard/';
            } else {
                window.location.href = '/dashboard/';
            }
            return;
        }

        if (loginForm) {
            // Detecta o tipo de usuário baseado no atributo data ou página
            const userType = loginForm.getAttribute('data-user-type') || 'funcionario';

            loginForm.addEventListener('submit', async event => {
                event.preventDefault();
                const loginButton = document.getElementById('loginButton');
                const errorMessageP = document.getElementById('loginErrorMessage');

                loginButton.disabled = true;
                loginButton.textContent = 'Entrando...';
                errorMessageP.classList.add('hidden');

                const formData = new FormData(loginForm);
                const username = formData.get('username');
                const password = formData.get('password');

                try {
                    const response = await fetch(apiTokenUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    const data = await response.json();
                    if (!response.ok) {
                        throw new Error(data.detail || 'Usuário ou senha inválidos.');
                    }
                    localStorage.setItem('accessToken', data.access);
                    localStorage.setItem('refreshToken', data.refresh);
                    setUserType(userType);

                    // Busca informações do usuário
                    try {
                        const userResponse = await fetch(apiUserUrl, {
                            headers: { Authorization: `Bearer ${data.access}` }
                        });
                        if (userResponse.ok) {
                            const userData = await userResponse.json();
                            const displayName =
                                userData.first_name || userData.username || 'Usuário';
                            localStorage.setItem('userName', displayName);
                        }
                    } catch (e) {
                        // Se falhar ao buscar dados do usuário, continua mesmo assim
                    }

                    // Redireciona baseado no tipo de usuário
                    if (userType === 'gerente') {
                        window.location.href = '/dashboard/';
                    } else {
                        window.location.href = '/dashboard/';
                    }
                } catch (error) {
                    errorMessageP.textContent = error.message;
                    errorMessageP.classList.remove('hidden');
                } finally {
                    loginButton.disabled = false;
                    loginButton.textContent = 'Entrar';
                }
            });
        }
    }

    // ===============================================
    //  SEÇÃO 2.5: LÓGICA DAS PÁGINAS DE REGISTRO
    // ===============================================
    if (
        currentPage === 'registro' ||
        currentPage === 'registro-cliente' ||
        currentPage === 'registro-funcionario' ||
        currentPage === 'registro-gerente' ||
        // Compatibilidade com .html
        currentPage === 'registro.html' ||
        currentPage === 'registro-cliente.html' ||
        currentPage === 'registro-funcionario.html' ||
        currentPage === 'registro-gerente.html'
    ) {
        const registroForm = document.getElementById('registroForm');

        if (registroForm) {
            const userType = registroForm.getAttribute('data-user-type') || 'funcionario';

            registroForm.addEventListener('submit', async event => {
                event.preventDefault();
                const registroButton = document.getElementById('registroButton');
                const errorMessageP = document.getElementById('registroErrorMessage');
                const successMessageP = document.getElementById('registroSuccessMessage');

                // Limpa mensagens anteriores
                errorMessageP.classList.add('hidden');
                if (successMessageP) {
                    successMessageP.classList.add('hidden');
                }

                registroButton.disabled = true;
                registroButton.textContent = 'Criando conta...';

                const formData = new FormData(registroForm);
                const username = formData.get('username');
                const email = formData.get('email');
                const firstName = formData.get('first_name') || '';
                const lastName = formData.get('last_name') || '';
                const password = formData.get('password');
                const password2 = formData.get('password2');

                // Validação de senha
                if (password !== password2) {
                    errorMessageP.textContent = 'As senhas não coincidem.';
                    errorMessageP.classList.remove('hidden');
                    registroButton.disabled = false;
                    registroButton.textContent = 'Criar Conta';
                    return;
                }

                if (password.length < 8) {
                    errorMessageP.textContent = 'A senha deve ter pelo menos 8 caracteres.';
                    errorMessageP.classList.remove('hidden');
                    registroButton.disabled = false;
                    registroButton.textContent = 'Criar Conta';
                    return;
                }

                try {
                    const response = await fetch(apiRegisterUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username,
                            email,
                            first_name: firstName,
                            last_name: lastName,
                            password,
                            password2,
                            user_type: userType
                        })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        // Trata erros de validação do backend
                        let errorMsg = 'Erro ao criar conta. ';
                        if (data.username) {
                            errorMsg = `${errorMsg}Nome de usuário: ${data.username.join(' ')}`;
                        } else if (data.email) {
                            errorMsg = `${errorMsg}E-mail: ${data.email.join(' ')}`;
                        } else if (data.password) {
                            errorMsg = `${errorMsg}Senha: ${data.password.join(' ')}`;
                        } else if (data.detail) {
                            errorMsg = `${errorMsg}${data.detail}`;
                        } else {
                            errorMsg = `${errorMsg}${JSON.stringify(data)}`;
                        }
                        throw new Error(errorMsg);
                    }

                    // Sucesso!
                    if (successMessageP) {
                        successMessageP.textContent =
                            '✅ Conta criada com sucesso! Redirecionando para login...';
                        successMessageP.classList.remove('hidden');
                    }

                    // Redireciona para a página de login correspondente após 2 segundos
                    setTimeout(() => {
                        const loginPages = {
                            cliente: '/login-cliente/',
                            funcionario: '/login-funcionario/',
                            gerente: '/login-gerente/'
                        };
                        window.location.href = loginPages[userType] || '/login-funcionario/';
                    }, 2000);
                } catch (error) {
                    errorMessageP.textContent = error.message;
                    errorMessageP.classList.remove('hidden');
                    registroButton.disabled = false;
                    registroButton.textContent = 'Criar Conta';
                }
            });
        }
    }

    // ==================================================
    //  SEÇÃO 3: LÓGICA ESPECÍFICA DA PÁGINA DE DASHBOARD
    // ==================================================
    if (
        currentPage === 'dashboard' ||
        currentPage === 'dashboard-admin' ||
        // Compatibilidade com .html
        currentPage === 'dashboard.html' ||
        currentPage === 'dashboard-admin.html'
    ) {
        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', logout);
        }

        // Exibe o nome do usuário
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            const savedName = localStorage.getItem('userName');
            const token = getAuthToken();
            
            if (savedName) {
                userNameElement.textContent = savedName;
            } else if (token) {
                // Tenta buscar do servidor
                const fetchUserName = async () => {
                    try {
                        const response = await fetch(apiUserUrl, {
                            headers: { Authorization: `Bearer ${token}` }
                        });
                        if (response.ok) {
                            const userData = await response.json();
                            const displayName =
                                userData.first_name || userData.username || 'Veterinário';
                            localStorage.setItem('userName', displayName);
                            userNameElement.textContent = displayName;
                        } else {
                            userNameElement.textContent = 'Veterinário';
                        }
                    } catch (error) {
                        console.error('Erro ao buscar nome do usuário:', error);
                        userNameElement.textContent = 'Veterinário';
                    }
                };
                fetchUserName();
            } else {
                userNameElement.textContent = 'Veterinário';
            }
        }
    }

    // ===============================================
    //  SEÇÃO 3.5: LÓGICA DA PÁGINA DE PACIENTES
    // ===============================================
    if (currentPage === 'pacientes' || currentPage === 'pacientes.html') {
        const searchInput = document.getElementById('searchInput');
        const searchButton = document.getElementById('searchButton');
        const patientTableBody = document.getElementById('patientTableBody');

        // Função para renderizar os pacientes na tabela
        const renderPatients = patients => {
            patientTableBody.innerHTML = ''; // Limpa a tabela

            if (patients.length === 0) {
                patientTableBody.innerHTML =
                    '<tr><td colspan="5" class="empty-message">Nenhum paciente encontrado.</td></tr>';
                return;
            }

            patients.forEach(patient => {
                const row = document.createElement('tr');

                // Garante que os campos opcionais não quebrem o código e tenham um placeholder
                const especie = patient.especie || 'Não informado';
                const raca = patient.raca || 'Não informado';
                const tutorName = patient.tutor_nome_completo || 'Sem tutor';

                // Cria cada célula (<td>) separadamente e adiciona à linha (<tr>)
                row.innerHTML = `
                    <td>${patient.nome}</td>
                    <td class="col-especie">${especie}</td>
                    <td>${raca}</td>
                    <td>${tutorName}</td>
                    <td>
                        <a href="#" class="action-button" data-patient-id="${patient.id}">Detalhes</a>
                    </td>
                `;
                patientTableBody.appendChild(row);
            });
        };

        // Função para buscar e exibir os pacientes (lidando com paginação e busca)
        const fetchAndDisplayPatients = async (searchTerm = '') => {
            patientTableBody.innerHTML =
                '<tr><td colspan="5" style="text-align: center;">Buscando...</td></tr>';
            let url = `${apiBaseUrl}/pacientes/`;
            if (searchTerm) {
                url += `?search=${encodeURIComponent(searchTerm)}`;
            }

            try {
                const allPatients = [];
                let nextUrl = url;
                while (nextUrl) {
                    const response = await fetch(nextUrl, {
                        headers: { Authorization: `Bearer ${getAuthToken()}` }
                    });
                    if (!response.ok)
                        throw new Error(`Erro ao buscar pacientes: ${response.statusText}`);
                    const data = await response.json();
                    allPatients.push(...(data.results || data));
                    nextUrl = data.next;
                }
                renderPatients(allPatients);
            } catch (error) {
                // Erro ao buscar pacientes - considere usar um sistema de logging em produção
                patientTableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">${error.message}</td></tr>`;
            }
        };

        // Event Listeners para a busca
        searchButton.addEventListener('click', () => {
            fetchAndDisplayPatients(searchInput.value.trim());
        });

        searchInput.addEventListener('keyup', event => {
            if (event.key === 'Enter') {
                fetchAndDisplayPatients(searchInput.value.trim());
            }
        });

        // Carregar a lista inicial de pacientes ao carregar a página
        fetchAndDisplayPatients();
        
        // Event listener para botões de detalhes
        patientTableBody.addEventListener('click', (e) => {
            if (e.target.classList.contains('action-button')) {
                e.preventDefault();
                const patientId = e.target.dataset.patientId;
                if (patientId) {
                    alert(`Funcionalidade de detalhes do paciente ${patientId} será implementada em breve!`);
                    // Futuramente: window.location.href = `/pacientes/${patientId}/`;
                }
            }
        });
    }

    // ==================================================
    //  SEÇÃO 4: LÓGICA ESPECÍFICA DA PÁGINA DE CONSULTA
    // ==================================================
    if (currentPage === 'consulta' || currentPage === 'consulta.html') {
        // --- Referências aos elementos do DOM da consulta ---
        const pacienteSelect = document.getElementById('pacienteSelect');
        const veterinarioSelect = document.getElementById('veterinarioSelect');
        const sintomasContainer = document.getElementById('listaSintomasCheckboxes');
        const consultaForm = document.getElementById('novaConsultaForm');
        const resultadoDiv = document.getElementById('resultadoDiagnostico');
        const diagnosticosUl = document.getElementById('listaDiagnosticosSugeridos');
        const mensagemErroP = document.getElementById('mensagemErro');
        const submitButton = document.getElementById('submitButton');

        // --- Funções Helper para a página de consulta ---
        const carregarTodosDados = async endpoint => {
            const todosOsDados = [];
            let url = `${apiBaseUrl}/${endpoint}/`;

            while (url) {
                const response = await fetch(url, {
                    headers: { Authorization: `Bearer ${getAuthToken()}` }
                });
                if (!response.ok)
                    throw new Error(`Erro ao buscar dados de ${endpoint}: ${response.statusText}`);
                const data = await response.json();
                todosOsDados.push(...(data.results || data));
                url = data.next;
            }
            return todosOsDados;
        };

        const popularSelect = async (selectElement, endpoint, nomeCampo) => {
            try {
                const dados = await carregarTodosDados(endpoint);
                selectElement.innerHTML = `<option value="">Selecione um ${nomeCampo}</option>`;
                dados.sort((a, b) =>
                    (a.nome_completo || a.nome).localeCompare(b.nome_completo || b.nome)
                );
                dados.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.nome_completo || item.nome;
                    selectElement.appendChild(option);
                });
            } catch (error) {
                selectElement.innerHTML = '<option value="">Erro ao carregar</option>';
                // Erro ao popular select - considere usar um sistema de logging em produção
            }
        };

        const popularSintomas = async () => {
            try {
                const sintomas = await carregarTodosDados('sintomas');
                sintomasContainer.innerHTML = '';
                sintomas.sort((a, b) => a.nome.localeCompare(b.nome));
                sintomas.forEach(sintoma => {
                    const div = document.createElement('div');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `sintoma-${sintoma.id}`;
                    checkbox.name = 'sintomas_apresentados';
                    checkbox.value = sintoma.id;
                    const label = document.createElement('label');
                    label.htmlFor = `sintoma-${sintoma.id}`;
                    label.textContent = sintoma.nome;
                    div.appendChild(checkbox);
                    div.appendChild(label);
                    sintomasContainer.appendChild(div);
                });
            } catch (error) {
                sintomasContainer.innerHTML =
                    '<p class="error-message">Não foi possível carregar os sintomas.</p>';
                // Erro ao popular sintomas - considere usar um sistema de logging em produção
            }
        };

        // --- Event Listener do formulário da consulta ---
        consultaForm.addEventListener('submit', async event => {
            event.preventDefault();
            submitButton.disabled = true;
            submitButton.textContent = 'Salvando...';
            resultadoDiv.classList.add('hidden');
            diagnosticosUl.innerHTML = '';
            mensagemErroP.textContent = '';

            const formData = new FormData(consultaForm);
            const sintomasSelecionadosIds = Array.from(
                document.querySelectorAll('input[name="sintomas_apresentados"]:checked')
            ).map(cb => parseInt(cb.value));

            const payload = {
                paciente: parseInt(formData.get('paciente')),
                veterinario_responsavel: parseInt(formData.get('veterinario_responsavel')),
                queixa_principal_tutor: formData.get('queixa_principal_tutor'),
                historico_doenca_atual: formData.get('historico_doenca_atual'),
                sintomas_apresentados_ids: sintomasSelecionadosIds,
                tipo_consulta: 'ROTINA' // Adicione um valor padrão ou um select no HTML para isso
            };
            if (formData.get('temperatura_celsius')) {
                payload.temperatura_celsius = formData.get('temperatura_celsius');
            }

            try {
                const response = await fetch(`${apiBaseUrl}/consultas/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${getAuthToken()}`
                    },
                    body: JSON.stringify(payload)
                });
                const responseData = await response.json();
                if (!response.ok) {
                    let errorMsg = `Erro ${response.status}: `;
                    for (const key in responseData) {
                        errorMsg += `${key}: ${responseData[key].join ? responseData[key].join(', ') : responseData[key]} `;
                    }
                    throw new Error(errorMsg);
                }

                resultadoDiv.classList.remove('hidden');
                const diagnosticos = responseData.diagnosticos_suspeitos || [];
                if (diagnosticos.length > 0) {
                    diagnosticos.forEach(diag => {
                        const li = document.createElement('li');
                        if (diag.porcentagem) {
                            li.textContent = `${diag.nome} (${diag.porcentagem})`;
                        } else {
                            li.textContent = diag.nome;
                        }
                        diagnosticosUl.appendChild(li);
                    });
                } else {
                    diagnosticosUl.innerHTML = '<li>Nenhum diagnóstico suspeito foi sugerido.</li>';
                }
            } catch (error) {
                resultadoDiv.classList.remove('hidden');
                mensagemErroP.textContent = error.message;
                // Erro ao enviar consulta - considere usar um sistema de logging em produção
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Salvar Consulta e Sugerir Diagnósticos';
            }
        });

        // --- Inicialização da página de consulta ---
        const inicializarPaginaConsulta = () => {
            popularSelect(pacienteSelect, 'pacientes', 'paciente');
            popularSelect(veterinarioSelect, 'veterinarios', 'veterinário');
            popularSintomas();
        };

        inicializarPaginaConsulta();
    }

    // ==================================================
    //  SEÇÃO 5: LÓGICA DA PÁGINA DE REGISTRO
    // ==================================================
    if (currentPage === 'registro.html') {
        const registroForm = document.getElementById('registroForm');

        if (registroForm) {
            registroForm.addEventListener('submit', async event => {
                event.preventDefault();
                const registroButton = document.getElementById('registroButton');
                const errorMessageP = document.getElementById('registroErrorMessage');

                registroButton.disabled = true;
                registroButton.textContent = 'Criando conta...';
                errorMessageP.classList.add('hidden');

                const formData = new FormData(registroForm);
                const password = formData.get('password');
                const password2 = formData.get('password2');

                if (password !== password2) {
                    errorMessageP.textContent = 'As senhas não coincidem!';
                    errorMessageP.classList.remove('hidden');
                    registroButton.disabled = false;
                    registroButton.textContent = 'Criar Conta';
                    return;
                }

                const payload = {
                    username: formData.get('username'),
                    email: formData.get('email'),
                    password: password
                };

                try {
                    const response = await fetch(`${apiBaseUrl}/auth/register/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        let errorMsg = '';
                        for (const key in data) {
                            errorMsg += `${key}: ${Array.isArray(data[key]) ? data[key].join(', ') : data[key]} `;
                        }
                        throw new Error(errorMsg || 'Erro ao criar conta.');
                    }

                    alert('Conta criada com sucesso! Faça login para continuar.');
                    window.location.href = '/login/';
                } catch (error) {
                    errorMessageP.textContent = error.message;
                    errorMessageP.classList.remove('hidden');
                } finally {
                    registroButton.disabled = false;
                    registroButton.textContent = 'Criar Conta';
                }
            });
        }
    }

    // ==================================================
    //  SEÇÃO 6: LÓGICA DA PÁGINA NOVO TUTOR
    // ==================================================
    if (currentPage === 'novo-tutor' || currentPage === 'novo-tutor.html') {
        const tutorForm = document.getElementById('novoTutorForm');

        // Máscara para CPF
        const cpfInput = document.getElementById('cpf');
        if (cpfInput) {
            cpfInput.addEventListener('input', e => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 11) {
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
                    e.target.value = value;
                }
            });
        }

        // Máscara para telefone
        const telefoneInput = document.getElementById('telefone');
        if (telefoneInput) {
            telefoneInput.addEventListener('input', e => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 11) {
                    value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
                    value = value.replace(/(\d)(\d{4})$/, '$1-$2');
                    e.target.value = value;
                }
            });
        }

        if (tutorForm) {
            tutorForm.addEventListener('submit', async event => {
                event.preventDefault();
                const submitButton = document.getElementById('submitTutorButton');
                const errorMsg = document.getElementById('tutorErrorMessage');
                const successMsg = document.getElementById('tutorSuccessMessage');

                submitButton.disabled = true;
                submitButton.textContent = 'Cadastrando...';
                errorMsg.classList.add('hidden');
                successMsg.classList.add('hidden');

                const formData = new FormData(tutorForm);
                const payload = {
                    nome_completo: formData.get('nome_completo'),
                    cpf: formData.get('cpf').replace(/\D/g, ''),
                    email: formData.get('email'),
                    telefone: formData.get('telefone').replace(/\D/g, ''),
                    endereco: formData.get('endereco')
                };

                try {
                    const response = await fetch(`${apiBaseUrl}/tutores/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            Authorization: `Bearer ${getAuthToken()}`
                        },
                        body: JSON.stringify(payload)
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        let errorText = '';
                        for (const key in data) {
                            errorText += `${key}: ${Array.isArray(data[key]) ? data[key].join(', ') : data[key]} `;
                        }
                        throw new Error(errorText || 'Erro ao cadastrar tutor.');
                    }

                    successMsg.textContent = 'Tutor cadastrado com sucesso!';
                    successMsg.classList.remove('hidden');
                    tutorForm.reset();

                    setTimeout(() => {
                        window.location.href = '/novo-paciente/';
                    }, 1500);
                } catch (error) {
                    errorMsg.textContent = error.message;
                    errorMsg.classList.remove('hidden');
                } finally {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Cadastrar Tutor';
                }
            });
        }
    }

    // ==================================================
    //  SEÇÃO 7: LÓGICA DA PÁGINA NOVO PACIENTE
    // ==================================================
    if (
        currentPage === 'novo-paciente' ||
        // Compatibilidade com .html
        currentPage === 'novo-paciente.html'
    ) {
        const pacienteForm = document.getElementById('novoPacienteForm');
        const tutorSelect = document.getElementById('tutorSelect');

        // Carregar tutores
        const carregarTutores = async () => {
            try {
                const response = await fetch(`${apiBaseUrl}/tutores/`, {
                    headers: { Authorization: `Bearer ${getAuthToken()}` }
                });
                const data = await response.json();
                const tutores = data.results || data;

                tutorSelect.innerHTML = '<option value="">Selecione um tutor</option>';
                tutores.forEach(tutor => {
                    const option = document.createElement('option');
                    option.value = tutor.id;
                    option.textContent = `${tutor.nome_completo} - ${tutor.cpf}`;
                    tutorSelect.appendChild(option);
                });
            } catch (error) {
                tutorSelect.innerHTML = '<option value="">Erro ao carregar tutores</option>';
            }
        };

        carregarTutores();

        if (pacienteForm) {
            pacienteForm.addEventListener('submit', async event => {
                event.preventDefault();
                const submitButton = document.getElementById('submitPacienteButton');
                const errorMsg = document.getElementById('pacienteErrorMessage');
                const successMsg = document.getElementById('pacienteSuccessMessage');

                submitButton.disabled = true;
                submitButton.textContent = 'Cadastrando...';
                errorMsg.classList.add('hidden');
                successMsg.classList.add('hidden');

                const formData = new FormData(pacienteForm);
                const payload = {
                    nome: formData.get('nome'),
                    especie: formData.get('especie'),
                    sexo: formData.get('sexo'),
                    tutor: parseInt(formData.get('tutor')),
                    raca: formData.get('raca') || null,
                    data_nascimento: formData.get('data_nascimento') || null,
                    peso_kg: formData.get('peso_kg') || null,
                    microchip: formData.get('microchip') || null,
                    observacoes: formData.get('observacoes') || ''
                };

                try {
                    const response = await fetch(`${apiBaseUrl}/pacientes/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            Authorization: `Bearer ${getAuthToken()}`
                        },
                        body: JSON.stringify(payload)
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        let errorText = '';
                        for (const key in data) {
                            errorText += `${key}: ${Array.isArray(data[key]) ? data[key].join(', ') : data[key]} `;
                        }
                        throw new Error(errorText || 'Erro ao cadastrar paciente.');
                    }

                    successMsg.textContent = 'Paciente cadastrado com sucesso!';
                    successMsg.classList.remove('hidden');
                    pacienteForm.reset();

                    setTimeout(() => {
                        window.location.href = '/pacientes/';
                    }, 1500);
                } catch (error) {
                    errorMsg.textContent = error.message;
                    errorMsg.classList.remove('hidden');
                } finally {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Cadastrar Paciente';
                }
            });
        }
    }
});
