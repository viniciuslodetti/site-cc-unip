import re

# Read the file
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Update admin panel header
old_admin_header = '''                <div class="hero">
                    <h1 class="hero-title">Painel Administrativo 🔧</h1>
                    <p class="hero-subtitle">Gerencie alunos, esportes e postagens</p>
                </div>'''

new_admin_header = '''                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                    <h2 style="font-size: 1.5rem; font-weight: 700;">Admin 🔧</h2>
                </div>'''

content = content.replace(old_admin_header, new_admin_header)

# Update users table to include cargo column and edit button
old_users_table = '''function renderUsersTable(container) {
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
                            <td>${user.sports ? user.sports.length : 0}</td>
                            <td>
                                <button class="btn btn-small btn-danger" onclick="deleteUser(${user.id})">Deletar</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}'''

new_users_table = '''function renderUsersTable(container) {
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
                                <button class="btn btn-small btn-primary" onclick="showEditUserModal(${user.id})" style="margin-right: 0.5rem;">Editar</button>
                                <button class="btn btn-small btn-danger" onclick="deleteUser(${user.id})">Deletar</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}'''

content = content.replace(old_users_table, new_users_table)

# Add edit user modal and handler functions before deleteUser function
edit_user_functions = '''
function showEditUserModal(userId) {
    const user = state.users.find(u => u.id === userId);
    if (!user) return;
    
    const content = `
        <form id="editUserForm" onsubmit="handleEditUser(event, ${userId})">
            <div class="grid grid-2">
                <div class="form-group">
                    <label class="form-label">Nome</label>
                    <input type="text" class="form-input" name="nome" value="${user.nome}" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">RA</label>
                    <input type="text" class="form-input" value="${user.ra}" disabled>
                </div>
            </div>
            
            <div class="grid grid-2">
                <div class="form-group">
                    <label class="form-label">Curso</label>
                    <input type="text" class="form-input" name="curso" value="${user.curso}" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Turma</label>
                    <input type="text" class="form-input" name="turma" value="${user.turma}" required>
                </div>
            </div>
            
            <div class="grid grid-2">
                <div class="form-group">
                    <label class="form-label">Semestre</label>
                    <select class="form-select" name="semestre" required>
                        ${[1, 2, 3, 4, 5, 6, 7, 8].map(s => `<option value="${s}" ${user.semestre === s ? 'selected' : ''}>${s}º Semestre</option>`).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Número da Camisa</label>
                    <input type="number" class="form-input" name="numero_camisa" value="${user.numero_camisa || ''}" min="1" max="99" placeholder="1-99 (opcional)">
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Cargo</label>
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
        { label: 'Salvar', class: 'btn-primary', onclick: 'document.getElementById("editUserForm").requestSubmit()' }
    ]);
}

async function handleEditUser(event, userId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    try {
        const data = await apiCall(`/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify({
                nome: formData.get('nome'),
                curso: formData.get('curso'),
                semestre: formData.get('semestre'),
                turma: formData.get('turma'),
                numero_camisa: formData.get('numero_camisa') || null,
                cargo: formData.get('cargo')
            })
        });
        
        showToast('Usuário atualizado com sucesso!', 'success');
        closeModal();
        navigateTo('admin');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

'''

# Find the deleteUser function and add the new functions before it
delete_user_pattern = r'(async function deleteUser\(userId\))'
content = re.sub(delete_user_pattern, edit_user_functions + r'\1', content)

# Write back
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Updated admin panel with cargo field and edit functionality")
