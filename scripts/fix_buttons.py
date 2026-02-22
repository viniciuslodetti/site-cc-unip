import re

filepath = r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. FIXED handleEditUser
# Replaces the buggy implementation with one that correctly converts types
fixed_handle_edit_user = '''
async function handleEditUser(event, userId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    // Convert values to correct types
    const semestre = formData.get('semestre');
    const numeroCamisa = formData.get('numero_camisa');
    
    try {
        const body = JSON.stringify({
            nome: formData.get('nome'),
            curso: formData.get('curso'),
            semestre: semestre ? parseInt(semestre) : null,
            turma: formData.get('turma'),
            numero_camisa: numeroCamisa ? parseInt(numeroCamisa) : null,
            cargo: formData.get('cargo')
        });

        const data = await apiCall(`/api/users/${userId}`, {
            method: 'PUT',
            body: body
        });
        
        showToast('Usuário atualizado com sucesso!', 'success');
        closeModal();
        // Refresh the admin panel
        renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
}
'''
# Using regex to replace the existing function body loosely to catch variants
content = re.sub(
    r'async function handleEditUser\(event, userId\) \{.*?^\}', 
    fixed_handle_edit_user.strip(), 
    content, 
    flags=re.DOTALL | re.MULTILINE
)


# 2. FIXED handleCreatePost
# Ensuring it works perfectly with files and text
fixed_handle_create_post = '''
async function handleCreatePost(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        // apiCall handles FormData automatically (removes Content-Type header)
        await apiCall('/api/posts', {
            method: 'POST',
            body: formData
        });

        showToast('Postagem criada com sucesso!', 'success');
        closeModal();
        renderAdmin(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
}
'''
content = re.sub(
    r'async function handleCreatePost\(event\) \{.*?^\}', 
    fixed_handle_create_post.strip(), 
    content, 
    flags=re.DOTALL | re.MULTILINE
)


# 3. FIXED handleEditProfile
# Ensuring user can set shirt number in dashboard
fixed_handle_edit_profile = '''
async function handleEditProfile(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
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
        renderDashboard(document.getElementById('mainContent'));
    } catch (error) {
        showToast(error.message, 'error');
    }
}
'''

# Check if handleEditProfile exists, if so replace, if not append
if 'async function handleEditProfile' in content:
    content = re.sub(
        r'async function handleEditProfile\(event\) \{.*?^\}', 
        fixed_handle_edit_profile.strip(), 
        content, 
        flags=re.DOTALL | re.MULTILINE
    )
else:
    # Append before the last few lines or initialization
    content = content.replace('// ==================== INITIALIZATION', fixed_handle_edit_profile + '\n\n// ==================== INITIALIZATION')


# 4. FIXING MODAL BUTTONS
# Sometimes requestSubmit() fails if the form isn't perfectly linked.
# Let's ensure the form exists before submitting.
content = content.replace(
    'onclick: \'document.getElementById("createPostForm").requestSubmit()\'',
    'onclick: \'document.getElementById("createPostForm") && document.getElementById("createPostForm").requestSubmit()\''
)
content = content.replace(
    'onclick: \'document.getElementById("editUserForm").requestSubmit()\'',
    'onclick: \'document.getElementById("editUserForm") && document.getElementById("editUserForm").requestSubmit()\''
)
content = content.replace(
    'onclick: \'document.getElementById("editProfileForm").requestSubmit()\'',
    'onclick: \'document.getElementById("editProfileForm") && document.getElementById("editProfileForm").requestSubmit()\''
)
content = content.replace(
    'onclick: \'document.getElementById("createSportForm").requestSubmit()\'',
    'onclick: \'document.getElementById("createSportForm") && document.getElementById("createSportForm").requestSubmit()\''
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Fixed all handlers and button actions.")
