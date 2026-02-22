import re

filepath = r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# REWRITE RENDER ADMIN
clean_render_admin = '''
// ==================== ADMIN VIEW ====================
function renderAdmin(container) {
    container.innerHTML = `
        <div class="animate-slide-in">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2 style="font-size: 1.5rem; font-weight: 700;">Painel de Controle 🔧</h2>
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
                <button class="tab active" onclick="switchTab(event, 'users')">Alunos</button>
                <button class="tab" onclick="switchTab(event, 'sports')">Esportes</button>
                <button class="tab" onclick="switchTab(event, 'posts')">Postagens</button>
            </div>

            <div id="tab-content" class="card">
                <!-- Content will be loaded here -->
            </div>
        </div>
    `;

    // Load initial tab
    loadAdminTab('users');
}

function switchTab(event, tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    loadAdminTab(tabName);
}

function loadAdminTab(tabName) {
    const container = document.getElementById('tab-content');
    
    if (tabName === 'users') {
        renderUsersTable(container);
    } else if (tabName === 'sports') {
        renderSportsTable(container);
    } else if (tabName === 'posts') {
        renderPostsTable(container);
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
                                <button class="btn btn-small btn-primary" onclick="window.showEditUserModal(${user.id})" style="margin-right: 0.5rem;">Editar</button>
                                <button class="btn btn-small btn-danger" onclick="deleteUser(${user.id})">Deletar</button>
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
            <button class="btn btn-primary" onclick="showCreateSportModal()">Novo Esporte</button>
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
                            <td>${sport.users ? sport.users.length : 0}</td>
                            <td>
                                <button class="btn btn-small btn-danger" onclick="deleteSport(${sport.id})">Deletar</button>
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
            <button class="btn btn-primary" onclick="showCreatePostModal()">Nova Postagem</button>
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
                            <td>${post.author_name}</td>
                            <td><span class="badge badge-secondary">${post.tipo}</span></td>
                            <td>
                                <button class="btn btn-small btn-danger" onclick="deletePost(${post.id})">Deletar</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function showCreatePostModal() {
    const content = `
        <form id="createPostForm" onsubmit="event.preventDefault(); window.handleCreatePost(event)">
            <div class="form-group">
                <label class="form-label">Título</label>
                <input type="text" class="form-input" name="titulo" required>
            </div>
            <div class="form-group">
                <label class="form-label">Tipo</label>
                <select class="form-select" name="tipo" required>
                    <option value="aviso">📢 Aviso</option>
                    <option value="foto">📸 Foto</option>
                    <option value="jogo">⚽ Jogo</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Conteúdo</label>
                <textarea class="form-textarea" name="conteudo" required></textarea>
            </div>
        </form>
    `;
    showModal('Nova Postagem', content, [
        { label: 'Cancelar', class: 'btn-secondary', onclick: 'closeModal()' },
        { label: 'Criar', class: 'btn-primary', onclick: 'window.handleCreatePost(null)' }
    ]);
}

function showCreateSportModal() {
    const content = `
        <form id="createSportForm" onsubmit="event.preventDefault(); window.handleCreateSport(event)">
            <div class="form-group">
                <label class="form-label">Nome do Esporte</label>
                <input type="text" class="form-input" name="nome" required>
            </div>
            <div class="form-group">
                <label class="form-label">Descrição</label>
                <textarea class="form-textarea" name="descricao"></textarea>
            </div>
        </form>
    `;
    showModal('Novo Esporte', content, [
        { label: 'Cancelar', class: 'btn-secondary', onclick: 'closeModal()' },
        { label: 'Criar', class: 'btn-success', onclick: 'window.handleCreateSport(null)' }
    ]);
}
'''

# Replace whatever old implementation of renderAdmin exists
if 'function renderAdmin(container)' in content:
     # Regex to remove old renderAdmin blocks roughly
     content = re.sub(r'function renderAdmin\(container\) \{.*?^\}', '', content, flags=re.DOTALL | re.MULTILINE)
     content = re.sub(r'function switchTab\(event, tabName\) \{.*?^\}', '', content, flags=re.DOTALL | re.MULTILINE)
     content = re.sub(r'function loadAdminTab\(tabName\) \{.*?^\}', '', content, flags=re.DOTALL | re.MULTILINE)
     content = re.sub(r'function renderUsersTable\(container\) \{.*?^\}', '', content, flags=re.DOTALL | re.MULTILINE)
     content = re.sub(r'function renderSportsTable\(container\) \{.*?^\}', '', content, flags=re.DOTALL | re.MULTILINE)
     content = re.sub(r'function renderPostsTable\(container\) \{.*?^\}', '', content, flags=re.DOTALL | re.MULTILINE)
     
# Append the clean new version before Global Handlers
if '// ==================== GLOBAL HANDLERS' in content:
    content = content.replace('// ==================== GLOBAL HANDLERS', clean_render_admin + '\n\n// ==================== GLOBAL HANDLERS')
else:
    # Just append before initialization
    content = content.replace('// ==================== INITIALIZATION', clean_render_admin + '\n\n// ==================== INITIALIZATION')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Defined all Admin View internal functions.")
