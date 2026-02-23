// ==================== STATE MANAGEMENT ====================
const state = {
    user: null,
    token: null,
    currentView: 'home',
    posts: [],
    sports: [],
    users: [],
    currentAdminTab: 'users'
};

// ==================== API HELPER ====================
const API_BASE = '';

async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (state.token) {
        defaultOptions.headers['Authorization'] = `Bearer ${state.token}`;
    }

    if (options.body instanceof FormData) {
        delete defaultOptions.headers['Content-Type'];
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'Erro na requisição');
    }

    return data;
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ==================== MODAL ====================
function showModal(title, content, actions = []) {
    const modalContainer = document.getElementById('modalContainer');

    const actionsHTML = actions.map(action =>
        `<button class="btn ${action.class || 'btn-secondary'}" onclick="${action.onclick}">${action.label}</button>`
    ).join('');

    modalContainer.innerHTML = `
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2 class="modal-title">${title}</h2>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${actions.length > 0 ? `<div class="modal-footer">${actionsHTML}</div>` : ''}
            </div>
        </div>
    `;
}

function closeModal(event) {
    if (!event || event.target.classList.contains('modal-overlay')) {
        document.getElementById('modalContainer').innerHTML = '';
    }
}

// ==================== AUTHENTICATION ====================
function saveAuth(token, user) {
    state.token = token;
    state.user = user;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

function loadAuth() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');

    if (token && user) {
        state.token = token;
        state.user = JSON.parse(user);
        return true;
    }
    return false;
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigateTo('home');
}

async function login(ra, senha) {
    try {
        const data = await apiCall('/api/login', {
            method: 'POST',
            body: JSON.stringify({ ra, senha })
        });

        saveAuth(data.access_token, data.user);
        showToast('Login realizado com sucesso!', 'success');
        navigateTo('dashboard');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function register(formData) {
    try {
        await apiCall('/api/register', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        showToast('Cadastro realizado com sucesso! Faça login para continuar.', 'success');
        navigateTo('home');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==================== NAVIGATION ====================
function updateNavbar() {
    const navMenu = document.getElementById('navMenu');

    if (state.user) {
        navMenu.innerHTML = `
            <a href="#" class="nav-link" onclick="navigateTo('dashboard')">Dashboard</a>
            <a href="#" class="nav-link" onclick="navigateTo('shirt')">Nova Camisa</a>
            <a href="#" class="nav-link" onclick="navigateTo('sports')">Esportes</a>
            <a href="#" class="nav-link" onclick="navigateTo('posts')">Postagens</a>
            ${state.user.is_admin ? '<a href="#" class="nav-link" onclick="navigateTo(\'admin\')">Painel de Controle</a>' : ''}
            <span class="nav-link">👤 ${state.user.nome}</span>
            <button class="btn btn-small btn-secondary" onclick="logout()">Sair</button>
        `;
    } else {
        navMenu.innerHTML = `
            <a href="#" class="nav-link" onclick="navigateTo('home')">Início</a>
            <button class="btn btn-small btn-primary" onclick="navigateTo('login')">Entrar</button>
            <button class="btn btn-small btn-secondary" onclick="navigateTo('register')">Cadastrar</button>
        `;
    }
}

function navigateTo(view) {
    state.currentView = view;
    updateNavbar();
    renderView(view);
}

// ==================== VIEW RENDERING ====================
function renderView(view) {
    const mainContent = document.getElementById('mainContent');

    const views = {
        home: renderHome,
        login: renderLogin,
        register: renderRegister,
        dashboard: renderDashboard,
        shirt: renderShirtOrder,
        sports: renderSports,
        posts: renderPosts,
        admin: renderAdmin
    };

    if (views[view]) {
        views[view](mainContent);
    } else {
        mainContent.innerHTML = '<h1>Página não encontrada</h1>';
    }
}

// ==================== HOME VIEW ====================
function renderHome(container) {
    container.innerHTML = `
        <div class="hero animate-slide-in">
            <h1 class="hero-title">Sistema de Gerenciamento UNIP</h1>
            <p class="hero-subtitle">Ciência da Computação - Gestão completa da sua turma</p>
            <div class="hero-actions">
                <button class="btn btn-primary" onclick="navigateTo('login')">Fazer Login</button>
                <button class="btn btn-secondary" onclick="navigateTo('register')">Criar Conta</button>
            </div>
        </div>
        <div class="grid grid-3 animate-slide-in">
            <div class="card">
                <div class="card-header">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📚</div>
                    <h3 class="card-title">Gestão de Alunos</h3>
                </div>
                <p class="card-subtitle">Cadastro completo com RA, número de camisa e controle de duplicatas</p>
            </div>
            <div class="card">
                <div class="card-header">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">⚽</div>
                    <h3 class="card-title">Esportes</h3>
                </div>
                <p class="card-subtitle">Participe de futebol, vôlei, basquete e muito mais</p>
            </div>
            <div class="card">
                <div class="card-header">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📢</div>
                    <h3 class="card-title">Comunicação</h3>
                </div>
                <p class="card-subtitle">Avisos, fotos e atualizações sobre jogos e eventos</p>
            </div>
        </div>
    `;
    // Apenas mostrar postagens recentes se o usuário estiver logado
    if (state.user) {
        loadRecentPosts(container);
    }
}

async function loadRecentPosts(container) {
    try {
        const data = await apiCall('/api/posts');
        const recentPosts = data.slice(0, 3);
        if (recentPosts.length > 0) {
            const postsHTML = `
                <div class="mt-xl">
                    <h2 class="text-center mb-lg" style="font-size: 2rem; font-weight: 700;">Últimas Postagens</h2>
                    <div class="grid grid-3">
                        ${recentPosts.map(post => createPostCard(post)).join('')}
                    </div>
                </div>
            `;
            container.innerHTML += postsHTML;
        }
    } catch (error) {
        console.error('Error loading posts:', error);
    }
}

// ==================== LOGIN VIEW ====================
function renderLogin(container) {
    container.innerHTML = `
        <div class="flex flex-center" style="min-height: 60vh;">
            <div class="card" style="max-width: 500px; width: 100%;">
                <div class="card-header text-center">
                    <h2 class="card-title">Entrar no Sistema</h2>
                    <p class="card-subtitle">Acesse sua conta com RA e senha</p>
                </div>
                <form id="loginForm" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label class="form-label">RA</label>
                        <input type="text" class="form-input" name="ra" required placeholder="Digite seu RA">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Senha</label>
                        <input type="password" class="form-input" name="senha" required placeholder="Digite sua senha">
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Entrar</button>
                </form>
                <p class="text-center mt-md" style="color: var(--text-secondary);">
                    Não tem conta? <a href="#" onclick="navigateTo('register')" style="color: var(--primary-400);">Cadastre-se</a>
                </p>
            </div>
        </div>
    `;
}

function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    login(formData.get('ra'), formData.get('senha'));
}

// ==================== REGISTER VIEW ====================
function renderRegister(container) {
    container.innerHTML = `
        <div class="flex flex-center" style="min-height: 60vh;">
            <div class="card" style="max-width: 600px; width: 100%;">
                <div class="card-header text-center">
                    <h2 class="card-title">Criar Conta</h2>
                    <p class="card-subtitle">Preencha seus dados para se cadastrar</p>
                </div>
                <form id="registerForm" onsubmit="handleRegister(event)">
                    <div class="grid grid-2">
                        <div class="form-group">
                            <label class="form-label">RA *</label>
                            <input type="text" class="form-input" name="ra" required placeholder="Ex: 12345678">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Nome Completo *</label>
                            <input type="text" class="form-input" name="nome" required placeholder="Seu nome completo">
                        </div>
                    </div>
                    <div class="grid grid-2">
                        <div class="form-group">
                             <label class="form-label">Curso *</label>
                             <input type="text" class="form-input" name="curso" required value="Ciência da Computação">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Semestre *</label>
                            <select class="form-select" name="semestre" required>
                                <option value="">Selecione</option>
                                ${[1, 2, 3, 4, 5, 6, 7, 8].map(s => `<option value="${s}">${s}º Semestre</option>`).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Turma *</label>
                        <input type="text" class="form-input" name="turma" required placeholder="Ex: CC1P14, CC2P14, CC3P15">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Apelido (Opcional)</label>
                        <input type="text" class="form-input" name="apelido" placeholder="Apelido para a camisa">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Senha *</label>
                        <input type="password" class="form-input" name="senha" required placeholder="Mínimo 6 caracteres" minlength="6">
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Cadastrar</button>
                </form>
                <p class="text-center mt-md" style="color: var(--text-secondary);">
                    Já tem conta? <a href="#" onclick="navigateTo('login')" style="color: var(--primary-400);">Faça login</a>
                </p>
            </div>
        </div>
    `;
}

function handleRegister(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        ra: formData.get('ra'),
        nome: formData.get('nome'),
        curso: formData.get('curso'),
        semestre: formData.get('semestre'),
        turma: formData.get('turma'),
        apelido: formData.get('apelido'),
        senha: formData.get('senha')
    };
    register(data);
}

// ==================== DASHBOARD VIEW ====================
async function renderDashboard(container) {
    if (!state.user) {
        navigateTo('login');
        return;
    }
    // Busca dados frescos do servidor para o status estar sempre atualizado
    try {
        const freshUser = await apiCall('/api/me');
        state.user = { ...state.user, ...freshUser };
        localStorage.setItem('user', JSON.stringify(state.user));
    } catch (e) {
        console.warn('Não foi possível atualizar dados do usuário:', e);
    }

    const cargo = state.user.cargo || 'Aluno';
    const isAdmin = state.user.is_admin;
    const badgeClass = isAdmin ? 'badge-warning' : (cargo === 'Professor' ? 'badge-success' : 'badge-info');

    container.innerHTML = `
        <div class="animate-slide-in">
            <div class="hero">
                <h1 class="hero-title">Bem-vindo, ${state.user.nome}! <span class="text-icon">👋</span></h1>
                <p class="hero-subtitle">RA: ${state.user.ra} | Turma: ${state.user.turma} | ${state.user.semestre}º Semestre</p>
            </div>
            <div class="grid grid-3">
                <div class="card">
                    <div class="card-header">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">👕</div>
                        <h3 class="card-title">Número da Camisa</h3>
                    </div>
                    <p style="font-size: 3rem; font-weight: 800; color: var(--primary-400);">
                        ${state.user.numero_camisa || 'Não definido'}
                    </p>
                    <button class="btn btn-primary btn-small mt-md" onclick="navigateTo('shirt')">Gerenciar Pedido</button>
                </div>
                <div class="card">
                    <div class="card-header">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">⚽</div>
                        <h3 class="card-title">Meus Esportes</h3>
                    </div>
                    <p style="font-size: 2rem; font-weight: 700; color: var(--success);">
                        ${state.user.sports ? state.user.sports.length : 0}
                    </p>
                    <button class="btn btn-primary btn-small mt-md" onclick="navigateTo('sports')">Ver Esportes</button>
                </div>
                <div class="card">
                    <div class="card-header">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                        <h3 class="card-title">Status</h3>
                    </div>
                    <div class="mt-md">
                        <span class="badge ${badgeClass}">${isAdmin ? 'Administrador' : cargo}</span>
                    </div>
                    <div class="mt-sm" style="font-size:0.85em; color: var(--text-secondary);">
                        ${state.user.tamanho_camisa ? `Camisa: <strong>${state.user.tamanho_camisa}</strong> | Qtd: <strong>${state.user.quantidade_camisa || 1}</strong>` : 'Pedido de camisa não realizado'}
                    </div>
                </div>
            </div>
            ${state.user.sports && state.user.sports.length > 0 ? `
                <div class="mt-xl">
                    <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 1.5rem;">Esportes que Participo</h2>
                    <div class="grid grid-4">
                        ${state.user.sports.map(sport => `
                            <div class="card" style="position: relative; overflow: hidden;">
                                <h3 style="font-weight: 600; margin-bottom: 0.5rem;">${sport.nome}</h3>
                                <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1rem;">${sport.descricao || ''}</p>
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="badge ${state.user.status_esporte === 'Titular' ? 'badge-success' : 'badge-info'}" style="font-size: 0.75rem;">
                                        ${state.user.status_esporte || 'Inscrito'}
                                    </span>
                                </div>
                                ${state.user.status_esporte === 'Titular' ? '<div style="position: absolute; top: 10px; right: 10px; font-size: 1.5rem;" title="Titular!">⭐</div>' : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// ==================== SPORTS VIEW ====================
async function renderSports(container) {
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div></div>';
    try {
        const data = await apiCall('/api/sports?include_participants=true');
        state.sports = data;
        const userSportIds = state.user ? state.user.sports.map(s => s.id) : [];

        container.innerHTML = `
            <div class="animate-slide-in">
                <div class="hero">
                    <h1 class="hero-title">Esportes Disponíveis <span class="text-icon">⚽🏀🏐</span></h1>
                    <p class="hero-subtitle">Escolha os esportes que você quer participar</p>
                </div>
                <div class="grid grid-3">
                    ${data.map(sport => {
            const isJoined = userSportIds.includes(sport.id);
            const sportIcons = { 'Futebol': '⚽', 'Vôlei': '🏐', 'Basquete': '🏀', 'Futsal': '⚽', 'Handebol': '🤾' };
            const icon = sportIcons[sport.nome] || '🏅';
            return `
                            <div class="sport-card ${isJoined ? 'joined' : ''}" onclick="${state.user ? `toggleSport(${sport.id})` : 'showToast(\'Faça login para participar\', \'warning\')'}">
                                <div class="sport-icon">${icon}</div>
                                <h3 class="sport-name">${sport.nome}</h3>
                                <p class="sport-description">${sport.descricao || ''}</p>
                                <p class="sport-participants">${sport.total_participants || 0} participante(s)</p>
                                ${isJoined ? '<span class="badge badge-success mt-md">Participando</span>' : ''}
                            </div>
                        `;
        }).join('')}
                </div>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<p class="text-center text-error">Erro ao carregar esportes: ${error.message}</p>`;
    }
}

async function toggleSport(sportId) {
    if (!state.user) {
        showToast('Faça login para participar', 'warning');
        return;
    }
    const sport = state.sports.find(s => s.id === sportId);
    const isJoined = state.user.sports.some(s => s.id === sportId);
    try {
        if (isJoined) {
            await apiCall(`/api/sports/${sportId}/leave`, { method: 'POST' });
            state.user.sports = state.user.sports.filter(s => s.id !== sportId);
            showToast(`Você saiu de ${sport.nome}`, 'info');
        } else {
            await apiCall(`/api/sports/${sportId}/join`, { method: 'POST' });
            // User can only have 1 sport, so replace the list
            state.user.sports = [sport];
            showToast(`Você agora participa de ${sport.nome}!`, 'success');
        }
        localStorage.setItem('user', JSON.stringify(state.user));
        navigateTo('sports');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==================== POSTS VIEW ====================
async function renderPosts(container) {
    // Bloquear acesso às postagens sem login
    if (!state.user) {
        container.innerHTML = `
            <div class="flex flex-center" style="min-height: 60vh;">
                <div class="card text-center" style="max-width: 450px; width: 100%;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">🔒</div>
                    <h2 class="card-title">Acesso Restrito</h2>
                    <p class="card-subtitle">Faça login para visualizar as postagens da turma.</p>
                    <div class="mt-lg" style="display: flex; gap: 1rem; justify-content: center;">
                        <button class="btn btn-primary" onclick="navigateTo('login')">Fazer Login</button>
                        <button class="btn btn-secondary" onclick="navigateTo('register')">Cadastrar</button>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div></div>';
    try {
        const data = await apiCall('/api/posts');
        state.posts = data;
        container.innerHTML = `
            <div class="animate-slide-in">
                <div class="hero">
                    <h1 class="hero-title">Postagens <span class="text-icon">📢</span></h1>
                    <p class="hero-subtitle">Avisos, fotos e atualizações sobre jogos</p>
                </div>
                ${data.length === 0 ? '<p class="text-center">Nenhuma postagem ainda</p>' : `
                    <div class="grid grid-2">
                        ${data.map(post => createPostCard(post)).join('')}
                    </div>
                `}
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<p class="text-center text-error">Erro ao carregar postagens: ${error.message}</p>`;
    }
}

function createPostCard(post) {
    const typeIcons = { 'aviso': '📢', 'foto': '📸', 'jogo': '⚽' };
    const icon = typeIcons[post.tipo] || '📝';
    const date = new Date(post.created_at).toLocaleDateString('pt-BR');
    return `
        <div class="post-card">
            ${post.imagem_url ? `<img src="${post.imagem_url}" alt="${post.titulo}" class="post-image">` : ''}
            <div class="post-content">
                <div class="post-header">
                    <div>
                        <h3 class="post-title">${icon} ${post.titulo}</h3>
                        <p class="post-meta">Por ${post.admin_nome || 'Admin'} • ${date}</p>
                    </div>
                    <span class="badge badge-${post.tipo === 'aviso' ? 'warning' : post.tipo === 'jogo' ? 'success' : 'info'}">${post.tipo}</span>
                </div>
                <p class="post-text">${post.conteudo}</p>
            </div>
        </div>
    `;
}

// ==================== ADMIN VIEW (FIXED) ====================
window.renderAdmin = async function (container) {
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div></div>';

    try {
        // Fetch fresh data
        const [users, sports, posts] = await Promise.all([
            apiCall('/api/users'),
            apiCall('/api/sports?include_participants=true'),
            apiCall('/api/posts')
        ]);

        // Update state
        state.users = users;
        state.sports = sports;
        state.posts = posts;

        container.innerHTML = `
            <div class="animate-slide-in">
                <div class="hero">
                    <h1 class="hero-title">Painel de Controle <span class="text-icon">🔧</span></h1>
                    <p class="hero-subtitle">Gerencie alunos, esportes e postagens</p>
                </div>

                <div class="grid grid-3 mb-xl">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h3 class="h1 mb-sm">${state.users.length}</h3>
                            <p>Alunos Cadastrados</p>
                        </div>
                    </div>
                    <div class="card bg-secondary text-white">
                        <div class="card-body text-center">
                            <h3 class="h1 mb-sm">${state.sports.length}</h3>
                            <p>Esportes Ativos</p>
                        </div>
                    </div>
                    <div class="card text-center" style="background: var(--surface-color); border: 1px solid var(--border-color);">
                        <div class="card-body">
                            <h3 class="h1 mb-sm" style="color: var(--primary-500);">${state.posts.length}</h3>
                            <p style="color: var(--text-secondary);">Postagens</p>
                        </div>
                    </div>
                </div>

                <div class="tabs mb-lg">
                    <button id="tab-users" class="tab active" onclick="switchTab(event, 'users')">Alunos</button>
                    <button id="tab-shirts" class="tab" onclick="switchTab(event, 'shirts')">Lista de Camisas</button>
                    <button id="tab-sports" class="tab" onclick="switchTab(event, 'sports')">Esportes</button>
                    <button id="tab-posts" class="tab" onclick="switchTab(event, 'posts')">Postagens</button>
                </div>

                <div id="tab-content" class="card"></div>
            </div>
        `;

        loadAdminTab(state.currentAdminTab);
    } catch (error) {
        container.innerHTML = `<p class="text-center text-error">Erro ao carregar painel: ${error.message}</p>`;
    }
}

window.switchTab = function (event, tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    state.currentAdminTab = tabName;
    loadAdminTab(tabName);
}

window.loadAdminTab = function (tabName) {
    state.currentAdminTab = tabName;
    // Update active tab button if not already active
    document.querySelectorAll('.tab').forEach(t => {
        if (t.id === `tab-${tabName}`) {
            t.classList.add('active');
        } else {
            t.classList.remove('active');
        }
    });

    const container = document.getElementById('tab-content');
    if (tabName === 'users') {
        renderUsersTable(container);
    } else if (tabName === 'sports') {
        renderSportsTable(container);
    } else if (tabName === 'posts') {
        renderPostsTable(container);
    } else if (tabName === 'shirts') {
        renderShirtListTable(container);
    }
}

function renderUsersTable(container) {
    container.innerHTML = `
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>RA</th>
                        <th>Nome</th>
                        <th>Turma</th>
                        <th>Semestre</th>
                        <th>Camisa</th>
                        <th>Cargo</th>
                        <th>Esportes</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${state.users.map(user => `
                        <tr>
                            <td>${user.ra}</td>
                            <td>${user.nome} ${user.is_admin ? '<span class="badge badge-warning">Admin</span>' : ''}</td>
                            <td>${user.turma}</td>
                            <td>${user.semestre}º</td>
                            <td>${user.numero_camisa || '-'}</td>
                            <td><span class="badge badge-info">${user.cargo || 'Aluno'}</span></td>
                            <td>${user.sports ? user.sports.length : 0}</td>
                            <td>
                                <div class="table-actions">
                                    <button class="btn btn-small btn-primary" onclick="window.showEditUserModal(${user.id})" title="Editar">✏️</button>
                                    <button class="btn btn-small btn-danger" onclick="window.deleteUser(${user.id})" title="Deletar">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderSportsTable(container) {
    container.innerHTML = `
        <div class="flex flex-between mb-lg">
            <h3>Gerenciar Esportes</h3>
            <button class="btn btn-primary" onclick="window.showCreateSportModal()">Novo Esporte</button>
        </div>
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Descrição</th>
                        <th>Participantes</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${state.sports.map(sport => `
                        <tr>
                            <td>${sport.nome}</td>
                            <td>${sport.descricao || '-'}</td>
                            <td>${sport.participants ? sport.participants.length : 0}</td>
                            <td>
                                <div class="table-actions">
                                    <button class="btn btn-small btn-info" onclick="window.showSportParticipants(${sport.id})" title="Ver Inscritos">👥</button>
                                    <button class="btn btn-small btn-primary" onclick="window.showEditSportModal(${sport.id})" title="Editar">✏️</button>
                                    <button class="btn btn-small btn-danger" onclick="window.deleteSport(${sport.id})" title="Deletar">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderPostsTable(container) {
    container.innerHTML = `
        <div class="flex flex-between mb-lg">
            <h3>Gerenciar Postagens</h3>
            <button class="btn btn-primary" onclick="window.showCreatePostModal()">Nova Postagem</button>
        </div>
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Título</th>
                        <th>Autor</th>
                        <th>Tipo</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${state.posts.map(post => `
                        <tr>
                            <td>${new Date(post.created_at).toLocaleDateString()}</td>
                            <td>${post.titulo}</td>
                            <td>${post.admin_nome || 'Admin'}</td>
                            <td><span class="badge badge-secondary">${post.tipo}</span></td>
                            <td>
                                <div class="table-actions">
                                    <button class="btn btn-small btn-danger" onclick="window.deletePost(${post.id})" title="Deletar">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderShirtListTable(container) {
    // Agora mostra todos os usuários que podem ter pedido camisa (incluindo Admins e Professores)
    const allStudents = state.users;
    const paidCount = allStudents.filter(u => u.camisa_paga).length;
    const pendingCount = allStudents.length - paidCount;

    container.innerHTML = `
        <div class="flex flex-between mb-lg" style="flex-wrap: wrap; gap: 0.75rem;">
            <div>
                <h3 style="margin-bottom: 0.35rem;">Lista de Camisas</h3>
                <div style="display: flex; gap: 0.75rem;">
                    <span style="font-size: 0.82em; color: var(--success); font-weight: 600;">&#10003; ${paidCount} pagos</span>
                    <span style="font-size: 0.82em; color: var(--warning); font-weight: 600;">&#9650; ${pendingCount} pendentes</span>
                </div>
            </div>
            <button class="btn btn-secondary" onclick="window.printShirtList()">&#128424;&#65039; Imprimir PDF</button>
        </div>
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>Nome Completo</th>
                        <th>Turma</th>
                        <th>N&#186; Camisa</th>
                        <th>Nome na Camisa</th>
                        <th>Tamanho</th>
                        <th>Qtd</th>
                        <th>Semestre</th>
                        <th>Pagamento</th>
                    </tr>
                </thead>
                <tbody>
                    ${allStudents.map(user => `
                        <tr>
                            <td>${user.nome}</td>
                            <td><span class="badge badge-info">${user.turma || '-'}</span></td>
                            <td><span class="badge badge-primary" style="font-size: 1.1em;">${user.numero_camisa || '-'}</span></td>
                            <td>${user.apelido || '-'}</td>
                            <td><strong>${user.tamanho_camisa || '-'}</strong></td>
                            <td>${user.quantidade_camisa || 1}</td>
                            <td>${user.semestre}&#186;</td>
                            <td>
                                ${user.tamanho_camisa ? `
                                    <button
                                        class="btn btn-small ${user.camisa_paga ? 'btn-success' : 'btn-danger'}"
                                        onclick="window.toggleCamisaPaga(${user.id})"
                                        title="${user.camisa_paga ? 'Clique para marcar como N&#195;O PAGO' : 'Clique para marcar como PAGO'}"
                                        style="min-width: 90px; font-weight: 700; letter-spacing: 0.5px;"
                                    >
                                        ${user.camisa_paga ? '&#10003; PAGO' : '&#10006; N&#195;O PAGO'}
                                    </button>
                                ` : '<span style="color: var(--text-muted); font-size: 0.8em;">Sem pedido</span>'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

window.toggleCamisaPaga = async function (userId) {
    try {
        const result = await apiCall(`/api/users/${userId}/pagar-camisa`, { method: 'POST' });
        // Atualiza o usuário no state local
        const idx = state.users.findIndex(u => u.id === userId);
        if (idx !== -1) {
            state.users[idx].camisa_paga = result.camisa_paga;
        }
        showToast(result.camisa_paga ? '&#10003; Camisa marcada como PAGO!' : 'Camisa marcada como NÃO PAGO', result.camisa_paga ? 'success' : 'warning');
        // Re-renderiza a aba
        const container = document.getElementById('tab-content');
        if (container) renderShirtListTable(container);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

window.printShirtList = function () {
    // Filtrar apenas quem tem pedido E já pagou
    const users = state.users.filter(u => u.tamanho_camisa && u.camisa_paga);
    if (users.length === 0) {
        showToast('Nenhum pedido PAGO encontrado para imprimir.', 'warning');
        return;
    }

    const printWindow = window.open('', '_blank');

    let rows = users.map(user => `
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">${user.nome}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${user.turma || '-'}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${user.apelido || '-'}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold;">${user.numero_camisa || '-'}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${user.tamanho_camisa || '-'}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${user.quantidade_camisa || 1}</td>
        </tr>
    `).join('');

    printWindow.document.write(`
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Pedidos Pagos - CC UNIP</title>
            <style>
                body { font-family: 'Inter', sans-serif; padding: 40px; color: #333; }
                .header { text-align: center; margin-bottom: 40px; border-bottom: 2px solid #16a34a; padding-bottom: 20px; }
                h1 { margin: 0; color: #15803d; font-size: 24px; text-transform: uppercase; }
                p { margin: 5px 0; color: #666; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
                th { background-color: #16a34a; color: white; padding: 12px; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; border: 1px solid #15803d; }
                td { font-size: 13px; }
                .footer { margin-top: 40px; text-align: right; font-size: 11px; color: #999; border-top: 1px solid #eee; padding-top: 20px; }
                @media print {
                    @page { margin: 1cm; }
                    body { padding: 0; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Pedidos CONFIRMADOS (Pagos) - Camisas CC UNIP</h1>
                <p>Lista de Produção Consolidada</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 30%;">Nome Completo</th>
                        <th style="width: 10%;">Turma</th>
                        <th style="width: 20%;">Apelido da Camisa</th>
                        <th style="width: 15%;">Nº Camisa</th>
                        <th style="width: 10%;">Tamanho</th>
                        <th style="width: 15%;">Quantidade</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
            <div class="footer">
                Documento gerado em: ${new Date().toLocaleString('pt-BR')} <br>
                Total de pedidos confirmados: ${users.length} | Responsável: Representante de Turma
            </div>
            <script>
                window.onload = function() {
                    setTimeout(() => {
                        window.print();
                        window.onafterprint = function() { window.close(); };
                    }, 500);
                };
            </script>
        </body>
        </html>
    `);
    printWindow.document.close();
}

// ==================== PROFILE EDITING ====================
window.showEditProfile = function () {
    if (!state.user) return;
    const content = `
        <form id="profileForm" onsubmit="event.preventDefault(); window.handleProfileUpdate(event)">
            <div class="grid grid-2">
                <div class="form-group">
                    <label class="form-label">Número da Camisa</label>
                    <input type="number" class="form-input" name="numero_camisa" value="${state.user.numero_camisa || ''}" min="1" max="99" placeholder="Ex: 10">
                </div>
                <div class="form-group">
                    <label class="form-label">Apelido na Camisa</label>
                    <input type="text" class="form-input" name="apelido" value="${state.user.apelido || ''}" maxlength="15" placeholder="Ex: Zézinho">
                </div>
            </div>
            <p class="text-secondary mb-md" style="font-size: 0.9em;">* O número deve ser único no sistema.</p>
        </form>
        `;
    showModal('Editar Meu Perfil', content, [
        { label: 'Cancelar', class: 'btn-secondary', onclick: 'closeModal()' },
        { label: 'Salvar', class: 'btn-primary', onclick: 'window.handleProfileUpdate(null)' }
    ]);
}

window.handleProfileUpdate = async function (event) {
    if (event) event.preventDefault();
    const form = document.getElementById('profileForm');
    if (!form) return;
    const formData = new FormData(form);
    const num = formData.get('numero_camisa');

    try {
        const payload = {
            apelido: formData.get('apelido'),
            numero_camisa: num ? parseInt(num) : null
        };

        await apiCall(`/ api / users / ${state.user.id} `, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });

        // Update local state
        state.user.apelido = payload.apelido;
        state.user.numero_camisa = payload.numero_camisa;
        localStorage.setItem('user', JSON.stringify(state.user));

        showToast('Perfil atualizado com sucesso!', 'success');
        closeModal();
        renderDashboard(document.getElementById('mainContent')); // Refresh dashboard
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==================== GLOBAL HANDLERS ====================

window.handleEditUser = async function (event, userId) {
    if (event) event.preventDefault();
    const form = document.getElementById('editUserForm');
    if (!form) return;
    const formData = new FormData(form);
    const semestre = formData.get('semestre');
    const numeroCamisa = formData.get('numero_camisa');
    try {
        await apiCall(`/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify({
                nome: formData.get('nome'),
                curso: formData.get('curso'),
                semestre: semestre ? parseInt(semestre) : null,
                turma: formData.get('turma'),
                numero_camisa: numeroCamisa ? parseInt(numeroCamisa) : null,
                apelido: formData.get('apelido'),
                cargo: formData.get('cargo')
            })
        });
        showToast('Usuário atualizado com sucesso!', 'success');
        closeModal();
        if (typeof renderAdmin === 'function') renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.showEditUserModal = function (userId) {
    const user = state.users.find(u => u.id === userId);
    if (!user) return;
    const content = `
        <form id="editUserForm" onsubmit="event.preventDefault(); window.handleEditUser(event, ${userId})">
            <div class="grid grid-2">
                <div class="form-group"><label class="form-label">Nome</label><input type="text" class="form-input" name="nome" value="${user.nome}" required></div>
                <div class="form-group"><label class="form-label">RA</label><input type="text" class="form-input" value="${user.ra}" disabled></div>
            </div>
            <div class="grid grid-2">
                <div class="form-group"><label class="form-label">Curso</label><input type="text" class="form-input" name="curso" value="${user.curso}" required></div>
                <div class="form-group"><label class="form-label">Turma</label><input type="text" class="form-input" name="turma" value="${user.turma}" required></div>
            </div>
            <div class="grid grid-2">
                <div class="form-group"><label class="form-label">Semestre</label>
                    <select class="form-select" name="semestre" required>
                        ${[1, 2, 3, 4, 5, 6, 7, 8].map(s => `<option value="${s}" ${user.semestre === s ? 'selected' : ''}>${s}º Semestre</option>`).join('')}
                    </select>
                </div>
                <div class="form-group"><label class="form-label">Número da Camisa</label><input type="number" class="form-input" name="numero_camisa" value="${user.numero_camisa || ''}" min="1" max="99" placeholder="1-99"></div>
            </div>
            <div class="form-group">
                <label class="form-label">Apelido</label>
                <input type="text" class="form-input" name="apelido" value="${user.apelido || ''}" placeholder="Apelido na camisa">
            </div>
            <div class="form-group"><label class="form-label">Cargo</label>
                <select class="form-select" name="cargo" required>
                    <option value="Aluno" ${user.cargo === 'Aluno' ? 'selected' : ''}>Aluno</option>
                    <option value="Professor" ${user.cargo === 'Professor' ? 'selected' : ''}>Professor</option>
                    <option value="Responsável" ${user.cargo === 'Responsável' ? 'selected' : ''}>Responsável</option>
                    <option value="Admin" ${user.cargo === 'Admin' ? 'selected' : ''}>Admin</option>
                </select>
            </div>
        </form>
        `;
    showModal('Editar Usuário', content, [
        { label: 'Cancelar', class: 'btn-secondary', onclick: 'closeModal()' },
        { label: 'Salvar', class: 'btn-primary', onclick: `window.handleEditUser(null, ${userId})` }
    ]);
};

window.handleCreatePost = async function (event) {
    if (event) event.preventDefault();
    const form = document.getElementById('createPostForm');
    if (!form) return;
    const formData = new FormData(form);
    try {
        await apiCall('/api/posts', { method: 'POST', body: formData });
        showToast('Postagem criada com sucesso!', 'success');
        closeModal();
        if (typeof renderAdmin === 'function') renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.showCreatePostModal = function () {
    const content = `
        < form id = "createPostForm" onsubmit = "event.preventDefault(); window.handleCreatePost(event)" >
            <div class="form-group"><label class="form-label">Título</label><input type="text" class="form-input" name="titulo" required></div>
            <div class="form-group"><label class="form-label">Tipo</label>
                <select class="form-select" name="tipo" required>
                    <option value="aviso">📢 Aviso</option>
                    <option value="foto">📸 Foto</option>
                    <option value="jogo">⚽ Jogo</option>
                </select>
            </div>
            <div class="form-group"><label class="form-label">Conteúdo</label><textarea class="form-textarea" name="conteudo" required></textarea></div>
            <div class="form-group">
                <label class="form-label">Imagem</label>
                <label class="btn btn-secondary" for="post-image-input" style="display:inline-block; cursor:pointer;">📷 Escolher Imagem</label>
                <input type="file" id="post-image-input" class="form-file-input" name="imagem" accept="image/*" style="display:none;" onchange="this.previousElementSibling.textContent = this.files[0] ? '✅ ' + this.files[0].name : '📷 Escolher Imagem'">
            </div>
        </form >
        `;
    showModal('Nova Postagem', content, [
        { label: 'Cancelar', class: 'btn-secondary', onclick: 'closeModal()' },
        { label: 'Criar', class: 'btn-primary', onclick: 'window.handleCreatePost(null)' }
    ]);
};

window.handleCreateSport = async function (event) {
    if (event) event.preventDefault();
    const form = document.getElementById('createSportForm');
    if (!form) return;
    const formData = new FormData(form);
    try {
        await apiCall('/api/sports', {
            method: 'POST',
            body: JSON.stringify({ nome: formData.get('nome'), descricao: formData.get('descricao') })
        });
        showToast('Esporte criado com sucesso!', 'success');
        closeModal();
        if (typeof renderAdmin === 'function') renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.showCreateSportModal = function () {
    const content = `
        < form id = "createSportForm" onsubmit = "event.preventDefault(); window.handleCreateSport(event)" >
            <div class="form-group"><label class="form-label">Nome do Esporte</label><input type="text" class="form-input" name="nome" required></div>
            <div class="form-group"><label class="form-label">Descrição</label><textarea class="form-textarea" name="descricao"></textarea></div>
        </form >
        `;
    showModal('Novo Esporte', content, [
        { label: 'Cancelar', class: 'btn-secondary', onclick: 'closeModal()' },
        { label: 'Criar', class: 'btn-success', onclick: 'window.handleCreateSport(null)' }
    ]);
};

window.handleEditSport = async function (event, sportId) {
    if (event) event.preventDefault();
    const form = document.getElementById('editSportForm');
    if (!form) return;
    const formData = new FormData(form);
    try {
        await apiCall(`/ api / sports / ${sportId} `, {
            method: 'PUT',
            body: JSON.stringify({
                nome: formData.get('nome'),
                descricao: formData.get('descricao')
            })
        });
        showToast('Esporte atualizado com sucesso!', 'success');
        closeModal();
        if (typeof renderAdmin === 'function') renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.showEditSportModal = function (sportId) {
    const sport = state.sports.find(s => s.id === sportId);
    if (!sport) return;
    const content = `
        < form id = "editSportForm" onsubmit = "event.preventDefault(); window.handleEditSport(event, ${sportId})" >
            <div class="form-group"><label class="form-label">Nome do Esporte</label><input type="text" class="form-input" name="nome" value="${sport.nome}" required></div>
            <div class="form-group"><label class="form-label">Descrição</label><textarea class="form-textarea" name="descricao">${sport.descricao || ''}</textarea></div>
        </form >
        `;
    showModal('Editar Esporte', content, [
        { label: 'Cancelar', class: 'btn-secondary', onclick: 'closeModal()' },
        { label: 'Salvar', class: 'btn-primary', onclick: `window.handleEditSport(null, ${sportId})` }
    ]);
};

// ==================== SHIRT ORDER VIEW ====================
function renderShirtOrder(container) {
    if (!state.user) {
        navigateTo('login');
        return;
    }

    // Shirt Preview Logic
    const shirtNumber = state.user.numero_camisa || '10';
    const shirtName = state.user.apelido || 'SEU NOME';
    const shirtSize = state.user.tamanho_camisa || 'M';
    const shirtQty = state.user.quantidade_camisa || 1;

    container.innerHTML = `
        <div class="animate-slide-in">
             <div class="hero">
                <h1 class="hero-title">Pedido da Camisa <span class="text-icon">👕</span></h1>
                <p class="hero-subtitle">Personalize sua camisa do time</p>
            </div>
            
            <div class="grid grid-2">
                <!-- Shirt Preview -->
                <div class="card flex flex-center flex-col" style="background: var(--bg-tertiary); min-height: 400px;">
                    <div class="shirt-preview" style="position: relative; width: 280px; height: 350px; background: var(--primary-600); border-radius: 30px 30px 10px 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; box-shadow: var(--shadow-xl); border: 2px solid rgba(255,255,255,0.1);">
                        <!-- Collar -->
                        <div style="position: absolute; top: -15px; width: 100px; height: 35px; background: var(--bg-tertiary); border-radius: 0 0 50% 50%; border: 4px solid var(--primary-600); z-index: 2;"></div>
                        <!-- Sleeves -->
                        <div style="position: absolute; top: 10px; left: -40px; width: 60px; height: 140px; background: var(--primary-600); transform: rotate(20deg); border-radius: 20px; z-index: -1; box-shadow: inset -5px -5px 10px rgba(0,0,0,0.2);"></div>
                        <div style="position: absolute; top: 10px; right: -40px; width: 60px; height: 140px; background: var(--primary-600); transform: rotate(-20deg); border-radius: 20px; z-index: -1; box-shadow: inset 5px -5px 10px rgba(0,0,0,0.2);"></div>
                        
                        <!-- Content -->
                        <div style="font-family: 'Inter', sans-serif; font-size: 1.4rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem; z-index: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.3); letter-spacing: 1px;" id="previewName">${shirtName}</div>
                        <div style="font-family: 'Inter', sans-serif; font-size: 7rem; font-weight: 900; line-height: 1; z-index: 1; text-shadow: 0 4px 8px rgba(0,0,0,0.3);" id="previewNumber">${shirtNumber}</div>
                        <div style="position: absolute; bottom: 40px; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 3px; opacity: 0.9; z-index: 1;">UNIP Ciência da Comp.</div>
                        
                        <!-- Pattern/Texture overlay -->
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%); border-radius: inherit; pointer-events: none;"></div>
                    </div>
                    <p class="mt-md text-secondary">Visualização ilustrativa</p>
                </div>
                
                <!-- Order Form -->
                <div class="card">
                    <form id="shirtOrderForm" onsubmit="handleShirtOrder(event)">
                        <div class="form-group">
                            <label class="form-label">Nome na Camisa (Apelido)</label>
                            <input type="text" class="form-input" name="apelido" value="${state.user.apelido || ''}" maxlength="15" required placeholder="Ex: Zézinho" oninput="updatePreview()">
                            <p class="text-secondary" style="font-size: 0.8em; margin-top: 0.25rem;">Nome único na turma</p>
                        </div>
                        
                        <div class="grid grid-2">
                            <div class="form-group">
                                <label class="form-label">Número</label>
                                <input type="number" class="form-input" name="numero_camisa" value="${state.user.numero_camisa || ''}" min="0" max="99" required placeholder="0-99" oninput="updatePreview()">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Tamanho</label>
                                <select class="form-select" name="tamanho_camisa" required>
                                    <option value="">Selecione</option>
                                    ${['P', 'M', 'G', 'GG', 'XG'].map(t => `<option value="${t}" ${shirtSize === t ? 'selected' : ''}>${t}</option>`).join('')}
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Quantidade</label>
                            <input type="number" class="form-input" name="quantidade_camisa" value="${shirtQty}" min="1" max="100" required>
                        </div>
                        
                        <div class="mt-xl">
                            <button type="submit" class="btn btn-primary" style="width: 100%;">💾 Salvar e Encomendar</button>
                        </div>

                        <div class="mt-lg p-md" style="background: rgba(var(--warning-rgb), 0.1); border-radius: var(--radius-md); border-left: 4px solid var(--warning);">
                            <p style="font-size: 0.9em; color: var(--text-secondary);">
                                ⚠️ <strong>Atenção:</strong> O pagamento deve ser feito diretamente ao representante da turma. Este formulário apenas reserva seu pedido.
                            </p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        `;

    // Attach live preview handler
    window.updatePreview = function () {
        const nameInput = document.querySelector('input[name="apelido"]');
        const numberInput = document.querySelector('input[name="numero_camisa"]');
        const name = nameInput ? nameInput.value : '';
        const number = numberInput ? numberInput.value : '';

        const previewName = document.getElementById('previewName');
        const previewNumber = document.getElementById('previewNumber');

        if (previewName) previewName.textContent = name || 'SEU NOME';
        if (previewNumber) previewNumber.textContent = number || '10';
    }
}

async function handleShirtOrder(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const num = formData.get('numero_camisa');

    try {
        const payload = {
            apelido: formData.get('apelido'),
            numero_camisa: num ? parseInt(num) : null,
            tamanho_camisa: formData.get('tamanho_camisa'),
            quantidade_camisa: parseInt(formData.get('quantidade_camisa'))
        };

        await apiCall(`/api/users/${state.user.id}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });

        // Update local state
        state.user = { ...state.user, ...payload };
        localStorage.setItem('user', JSON.stringify(state.user));

        showToast('Pedido da camisa salvo com sucesso!', 'success');
        navigateTo('dashboard'); // Go back to dashboard to see results
    } catch (error) {
        showToast(error.message, 'error');
    }
}

window.deleteUser = async function (userId) {
    if (!confirm('Tem certeza que deseja deletar este usuário?')) return;
    try {
        await apiCall(`/api/users/${userId}`, { method: 'DELETE' });
        showToast('Usuário deletado com sucesso!', 'success');
        if (typeof renderAdmin === 'function') renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.deletePost = async function (postId) {
    if (!confirm('Tem certeza?')) return;
    try {
        await apiCall(`/api/posts/${postId}`, { method: 'DELETE' });
        showToast('Postagem deletada!', 'success');
        if (typeof renderAdmin === 'function') renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.deleteSport = async function (sportId) {
    if (!confirm('Tem certeza que deseja deletar este esporte?')) return;
    try {
        await apiCall(`/api/sports/${sportId}`, { method: 'DELETE' });
        showToast('Esporte deletado com sucesso!', 'success');
        if (typeof renderAdmin === 'function') renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.showSportParticipants = function (sportId) {
    const sport = state.sports.find(s => s.id === sportId);
    if (!sport) return;

    const participants = sport.participants || [];

    const content = `
        <div class="mb-lg">
            <p class="text-secondary">Total de inscritos: <strong>${participants.length}</strong></p>
        </div>
        ${participants.length === 0 ? '<p class="text-center p-xl">Nenhum aluno inscrito neste esporte ainda.</p>' : `
            <div class="table-container">
                <table class="table" style="font-size: 0.9rem;">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Turma</th>
                            <th>Status Atleta</th>
                            <th>Seleção</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${participants.map(p => `
                            <tr>
                                <td>${p.nome}</td>
                                <td>${p.turma}</td>
                                <td>
                                    <span class="badge ${p.status_esporte === 'Titular' ? 'badge-success' : 'badge-info'}">
                                        ${p.status_esporte || 'Inscrito'}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-small ${p.status_esporte === 'Titular' ? 'btn-secondary' : 'btn-primary'}" 
                                            onclick="window.updateParticipantStatus(${p.id}, ${sport.id}, '${p.status_esporte === 'Titular' ? 'Inscrito' : 'Titular'}')">
                                        ${p.status_esporte === 'Titular' ? 'Remover Titular' : 'Tornar Titular'}
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `}
    `;

    showModal(`Inscritos: ${sport.nome}`, content, [
        { label: 'Fechar', class: 'btn-secondary', onclick: 'closeModal()' }
    ]);
};

window.updateParticipantStatus = async function (userId, sportId, newStatus) {
    try {
        await apiCall(`/api/users/${userId}/esporte-status`, {
            method: 'POST',
            body: JSON.stringify({ status: newStatus })
        });

        showToast(`Status atualizado para ${newStatus}!`, 'success');

        // Refresh local data to show changes in modal without closing it
        const [updatedSports] = await Promise.all([
            apiCall('/api/sports?include_participants=true')
        ]);
        state.sports = updatedSports;

        // Re-render the same modal to show updated status
        window.showSportParticipants(sportId);
    } catch (error) {
        showToast(error.message, 'error');
    }
};


// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    const isAuthenticated = loadAuth();
    if (isAuthenticated) {
        navigateTo('dashboard');
    } else {
        navigateTo('home');
    }
});
