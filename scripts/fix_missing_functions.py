import re

filepath = r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any partial or broken definitions of these functions to avoid syntax errors
# We will append clean versions at the end.

functions_to_remove = [
    'showEditUserModal', 'handleEditUser', 
    'handleCreatePost', 'handleCreateSport', 
    'handleEditProfile'
]

for func in functions_to_remove:
    # Remove async function ... { ... }
    content = re.sub(f'async function {func}.*?^}}', '', content, flags=re.DOTALL | re.MULTILINE)
    # Remove function ... { ... }
    content = re.sub(f'function {func}.*?^}}', '', content, flags=re.DOTALL | re.MULTILINE)
    # Remove window.func = ...
    content = re.sub(f'window.{func} =.*?^}}', '', content, flags=re.DOTALL | re.MULTILINE)


# Append the robust functions at the end
additional_code = '''

// ==================== GLOBAL HANDLERS (FIXED) ====================

window.handleEditUser = async function(event, userId) {
    if(event) event.preventDefault();
    
    const form = document.getElementById('editUserForm');
    if(!form) {
        console.error('Form editUserForm not found');
        return;
    }

    const formData = new FormData(form);
    const semestre = formData.get('semestre');
    const numeroCamisa = formData.get('numero_camisa');
    
    try {
        const payload = {
            nome: formData.get('nome'),
            curso: formData.get('curso'),
            semestre: semestre ? parseInt(semestre) : null,
            turma: formData.get('turma'),
            numero_camisa: numeroCamisa ? parseInt(numeroCamisa) : null,
            cargo: formData.get('cargo')
        };

        await apiCall(`/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        
        showToast('Usuário atualizado com sucesso!', 'success');
        closeModal();
        if(typeof renderAdmin === 'function') {
            renderView('admin'); // Reload admin view
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.showEditUserModal = function(userId) {
    const user = state.users.find(u => u.id === userId);
    if (!user) return;
    
    const content = `
        <form id="editUserForm" onsubmit="event.preventDefault(); window.handleEditUser(event, ${userId})">
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
        { label: 'Salvar', class: 'btn-primary', onclick: `window.handleEditUser(null, ${userId})` }
    ]);
};

window.handleCreatePost = async function(event) {
    if(event) event.preventDefault();
    
    const form = document.getElementById('createPostForm');
    if(!form) return;

    const formData = new FormData(form);

    try {
        await apiCall('/api/posts', {
            method: 'POST',
            body: formData
        });

        showToast('Postagem criada com sucesso!', 'success');
        closeModal();
        if(typeof renderAdmin === 'function') {
             renderView('admin');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.handleCreateSport = async function(event) {
    if(event) event.preventDefault();
    
    const form = document.getElementById('createSportForm');
    if(!form) return;
    const formData = new FormData(form);

    try {
        await apiCall('/api/sports', {
            method: 'POST',
            body: JSON.stringify({
                nome: formData.get('nome'),
                descricao: formData.get('descricao')
            })
        });

        showToast('Esporte criado com sucesso!', 'success');
        closeModal();
        if(typeof renderAdmin === 'function') {
             renderView('admin');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
};

window.handleEditProfile = async function(event) {
    if(event) event.preventDefault();
    
    const form = document.getElementById('editProfileForm');
    if(!form) return;

    const formData = new FormData(form);
    const numeroCamisa = formData.get('numero_camisa');

    try {
        const data = await apiCall(`/api/users/${state.user.id}`, {
            method: 'PUT',
            body: JSON.stringify({
                numero_camisa: numeroCamisa ? parseInt(numeroCamisa) : null
            })
        });

        state.user = data.user;
        localStorage.setItem('user', JSON.stringify(data.user));
        showToast('Perfil atualizado com sucesso!', 'success');
        closeModal();
        renderView('dashboard');
    } catch (error) {
        showToast(error.message, 'error');
    }
};
'''

# Insert before initialization
if '// ==================== INITIALIZATION' in content:
    content = content.replace('// ==================== INITIALIZATION', additional_code + '\n\n// ==================== INITIALIZATION')
else:
    content += additional_code

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Added all missing functions globally.")
