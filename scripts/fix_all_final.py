import re

filepath = r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. FIX HANDLE EDIT USER (ADMIN)
# Make sure it's global and correctly implemented
fixed_handle_edit_user = '''
window.handleEditUser = async function(event, userId) {
    if(event) event.preventDefault();
    
    // Get form by ID directly to be safe
    const form = document.getElementById('editUserForm');
    if(!form) return;

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

        const data = await apiCall(`/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        
        showToast('Usuário atualizado com sucesso!', 'success');
        closeModal();
        // Force refresh of admin panel
        if(typeof renderAdmin === 'function') {
            renderAdmin(document.getElementById('mainContent'));
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}
'''
# Replace or append
if 'async function handleEditUser' in content:
    content = re.sub(r'async function handleEditUser.*?^\}', fixed_handle_edit_user.strip(), content, flags=re.DOTALL | re.MULTILINE)
else:
    content += '\n' + fixed_handle_edit_user


# 2. FIX EDIT USER MODAL BUTTON
# Direct call to the function instead of form submit
content = content.replace(
    'onclick: \'document.getElementById("editUserForm").requestSubmit()\'',
    'onclick: \'handleEditUser(null, "\' + userId + \'")\''
)
# Fix for the new robust way (regex replacement for safety)
content = re.sub(
    r'onclick:\s*[\'"`]document\.getElementById\("editUserForm"\)\.requestSubmit\(\)[\'"`]',
    'onclick: `handleEditUser(null, ${userId})`',
    content
)


# 3. FIX HANDLE EDIT PROFILE (DASHBOARD)
fixed_handle_edit_profile = '''
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
        if(typeof renderDashboard === 'function') {
            renderDashboard(document.getElementById('mainContent'));
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}
'''
if 'async function handleEditProfile' in content:
    content = re.sub(r'async function handleEditProfile.*?^\}', fixed_handle_edit_profile.strip(), content, flags=re.DOTALL | re.MULTILINE)
else:
    content += '\n' + fixed_handle_edit_profile

# Fix Profile Button
content = content.replace(
    'onclick: \'document.getElementById("editProfileForm").requestSubmit()\'',
    'onclick: \'handleEditProfile(null)\''
)


# 4. FIX HANDLE CREATE POST
fixed_handle_create_post = '''
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
            renderAdmin(document.getElementById('mainContent'));
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}
'''
if 'async function handleCreatePost' in content:
    content = re.sub(r'async function handleCreatePost.*?^\}', fixed_handle_create_post.strip(), content, flags=re.DOTALL | re.MULTILINE)
else:
    content += '\n' + fixed_handle_create_post

# Fix Post Button
content = content.replace(
    'onclick: \'document.getElementById("createPostForm").requestSubmit()\'',
    'onclick: \'handleCreatePost(null)\''
)


# 5. FIX HANDLE CREATE SPORT
fixed_handle_create_sport = '''
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
            renderAdmin(document.getElementById('mainContent'));
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}
'''
if 'async function handleCreateSport' in content:
    content = re.sub(r'async function handleCreateSport.*?^\}', fixed_handle_create_sport.strip(), content, flags=re.DOTALL | re.MULTILINE)
else:
    content += '\n' + fixed_handle_create_sport


# Fix Sport Button
content = content.replace(
    'onclick: \'document.getElementById("createSportForm").requestSubmit()\'',
    'onclick: \'handleCreateSport(null)\''
)


# 6. FIX SHOW EDIT USER MODAL (Ensure correct onclick for button generation)
# We need to regenerate the modal content string to use the direct function call
fixed_show_edit_user = '''
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
        { label: 'Salvar', class: 'btn-primary', onclick: `handleEditUser(null, ${userId})` }
    ]);
}
'''
content = re.sub(r'function showEditUserModal\(userId\) \{.*?^\}', fixed_show_edit_user.strip(), content, flags=re.DOTALL | re.MULTILINE)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Rewrote all handlers to be robust and directly callable.")
