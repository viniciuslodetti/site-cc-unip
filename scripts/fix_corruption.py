# Fix the corrupted app.js file
import re

# Read the backup or current file
try:
    with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js.backup', 'r', encoding='utf-8') as f:
        content = f.read()
except:
    # If backup doesn't exist, we'll need to reconstruct from scratch
    print("No backup found, will need manual reconstruction")
    exit(1)

# Find and fix the login function that got corrupted
# Look for the pattern where the function got broken
content = re.sub(
    r'\}\s*\)\s*;\s*saveAuth\(data\.access_token, data\.user\);',
    '''    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function register(formData) {
    try {
        const data = await apiCall('/api/register', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        showToast('Cadastro realizado com sucesso! Faça login para continuar.', 'success');
        navigateTo('home');''',
    content,
    flags=re.DOTALL
)

# Write the fixed version
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed corrupted app.js")
