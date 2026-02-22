import re

# Read the file
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove login with shirt number functionality
# Remove the loginCamisa function
content = re.sub(
    r'async function loginCamisa\(numero_camisa, senha\) \{[^}]+\}[^}]+\}',
    '',
    content,
    flags=re.DOTALL
)

# Remove handleLoginCamisa function
content = re.sub(
    r'function handleLoginCamisa\(event\) \{[^}]+\}',
    '',
    content,
    flags=re.DOTALL
)

# 2. Restore simple login form (remove tabs)
old_login = r'''// ==================== LOGIN VIEW ====================
function renderLogin\(container\) \{
    container\.innerHTML = `
        <div class="flex flex-center" style="min-height: 60vh;">
            <div class="card" style="max-width: 500px; width: 100%;">
                <div class="card-header text-center">
                    <h2 class="card-title">Entrar no Sistema</h2>
                    <p class="card-subtitle">Escolha como deseja fazer login</p>
                </div>

                <div class="flex gap-md mb-lg" style="border-bottom: 2px solid var\(--border-color\);">
                    <button class="btn btn-primary" onclick="showLoginTab\('ra'\)" id="tab-login-ra">Login com RA</button>
                    <button class="btn btn-secondary" onclick="showLoginTab\('camisa'\)" id="tab-login-camisa">Login com Camisa</button>
                </div>

                <div id="loginTabContent"></div>

                <p class="text-center mt-md" style="color: var\(--text-secondary\);">
                    Não tem conta\? <a href="#" onclick="navigateTo\('register'\)" style="color: var\(--primary-400\);">Cadastre-se</a>
                </p>
            </div>
        </div>
    `;
    
    showLoginTab\('ra'\);
\}'''

new_login = '''// ==================== LOGIN VIEW ====================
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
}'''

content = re.sub(old_login, new_login, content, flags=re.DOTALL)

# Remove showLoginTab function
content = re.sub(
    r'function showLoginTab\(tab\) \{[^}]+\}[^}]+\}[^}]+\}',
    '',
    content,
    flags=re.DOTALL
)

# 3. Change admin panel title to "Painel de Controle"
content = content.replace(
    '<h2 style="font-size: 1.5rem; font-weight: 700;">Admin 🔧</h2>',
    '<h2 style="font-size: 1.5rem; font-weight: 700;">Painel de Controle 🔧</h2>'
)

# Write back
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed login (removed shirt number login)")
print("✓ Changed admin title to 'Painel de Controle'")
