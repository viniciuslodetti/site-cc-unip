import re

# Read the file
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the login function to support both RA and shirt number
old_login_func = '''async function login(ra, senha) {
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
}'''

new_login_func = '''async function login(ra, senha) {
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

async function loginCamisa(numero_camisa, senha) {
    try {
        const data = await apiCall('/api/login-camisa', {
            method: 'POST',
            body: JSON.stringify({ numero_camisa, senha })
        });

        saveAuth(data.access_token, data.user);
        showToast('Login realizado com sucesso!', 'success');
        navigateTo('dashboard');
    } catch (error) {
        showToast(error.message, 'error');
    }
}'''

content = content.replace(old_login_func, new_login_func)

# Update renderLogin to have tabs
old_render_login = '''// ==================== LOGIN VIEW ====================
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
    const ra = formData.get('ra');
    const senha = formData.get('senha');
    login(ra, senha);
}'''

new_render_login = '''// ==================== LOGIN VIEW ====================
function renderLogin(container) {
    container.innerHTML = `
        <div class="flex flex-center" style="min-height: 60vh;">
            <div class="card" style="max-width: 500px; width: 100%;">
                <div class="card-header text-center">
                    <h2 class="card-title">Entrar no Sistema</h2>
                    <p class="card-subtitle">Escolha como deseja fazer login</p>
                </div>

                <div class="flex gap-md mb-lg" style="border-bottom: 2px solid var(--border-color);">
                    <button class="btn btn-primary" onclick="showLoginTab('ra')" id="tab-login-ra">Login com RA</button>
                    <button class="btn btn-secondary" onclick="showLoginTab('camisa')" id="tab-login-camisa">Login com Camisa</button>
                </div>

                <div id="loginTabContent"></div>

                <p class="text-center mt-md" style="color: var(--text-secondary);">
                    Não tem conta? <a href="#" onclick="navigateTo('register')" style="color: var(--primary-400);">Cadastre-se</a>
                </p>
            </div>
        </div>
    `;
    
    showLoginTab('ra');
}

function showLoginTab(tab) {
    // Update active tab
    const raBtn = document.getElementById('tab-login-ra');
    const camisaBtn = document.getElementById('tab-login-camisa');
    
    if (raBtn && camisaBtn) {
        raBtn.classList.toggle('btn-primary', tab === 'ra');
        raBtn.classList.toggle('btn-secondary', tab !== 'ra');
        camisaBtn.classList.toggle('btn-primary', tab === 'camisa');
        camisaBtn.classList.toggle('btn-secondary', tab !== 'camisa');
    }
    
    const content = document.getElementById('loginTabContent');
    
    if (tab === 'ra') {
        content.innerHTML = `
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
        `;
    } else {
        content.innerHTML = `
            <form id="loginCamisaForm" onsubmit="handleLoginCamisa(event)">
                <div class="form-group">
                    <label class="form-label">Número da Camisa</label>
                    <input type="number" class="form-input" name="numero_camisa" required placeholder="Digite o número da sua camisa" min="1" max="99">
                </div>

                <div class="form-group">
                    <label class="form-label">Senha</label>
                    <input type="password" class="form-input" name="senha" required placeholder="Digite sua senha">
                </div>

                <button type="submit" class="btn btn-primary" style="width: 100%;">Entrar</button>
            </form>
        `;
    }
}

function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const ra = formData.get('ra');
    const senha = formData.get('senha');
    login(ra, senha);
}

function handleLoginCamisa(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const numero_camisa = formData.get('numero_camisa');
    const senha = formData.get('senha');
    loginCamisa(numero_camisa, senha);
}'''

content = content.replace(old_render_login, new_render_login)

# Write back
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added login with shirt number functionality")
