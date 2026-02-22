import re

# Read the file
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix handleEditProfile to convert numero_camisa to integer
content = content.replace(
    '''    try {
        const data = await apiCall(`/api/users/${state.user.id}`, {
            method: 'PUT',
            body: JSON.stringify({
                numero_camisa: numeroCamisa ? parseInt(numeroCamisa) : null
            })
        });''',
    '''    try {
        const numeroCamisa = formData.get('numero_camisa');
        const data = await apiCall(`/api/users/${state.user.id}`, {
            method: 'PUT',
            body: JSON.stringify({
                numero_camisa: numeroCamisa ? parseInt(numeroCamisa) : null
            })
        });'''
)

# 2. Fix handleEditUser to convert numero_camisa and semestre to integers
old_handle_edit_user = '''async function handleEditUser(event, userId) {
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
        });'''

new_handle_edit_user = '''async function handleEditUser(event, userId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    try {
        const numeroCamisa = formData.get('numero_camisa');
        const semestre = formData.get('semestre');
        
        const data = await apiCall(`/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify({
                nome: formData.get('nome'),
                curso: formData.get('curso'),
                semestre: semestre ? parseInt(semestre) : null,
                turma: formData.get('turma'),
                numero_camisa: numeroCamisa ? parseInt(numeroCamisa) : null,
                cargo: formData.get('cargo')
            })
        });'''

content = content.replace(old_handle_edit_user, new_handle_edit_user)

# Write back
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed handleEditProfile and handleEditUser to properly convert numbers")
