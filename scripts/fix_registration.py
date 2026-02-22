import re

# Read the file
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the shirt number field from registration form
# Find and replace the grid-2 div that contains turma and numero_camisa
old_pattern = r'''                    <div class="grid grid-2">
                        <div class="form-group">
                            <label class="form-label">Turma \*</label>
                            <input type="text" class="form-input" name="turma" required placeholder="Ex: A, B, C">
                        </div>

                        <div class="form-group">
                            <label class="form-label">Número da Camisa</label>
                            <input type="number" class="form-input" name="numero_camisa" min="1" max="99" placeholder="1-99 \(opcional\)">
                        </div>
                    </div>'''

new_pattern = '''                    <div class="form-group">
                        <label class="form-label">Turma *</label>
                        <input type="text" class="form-input" name="turma" required placeholder="Ex: A, B, C">
                    </div>'''

content = re.sub(old_pattern, new_pattern, content, flags=re.DOTALL)

# Write back
with open(r'c:\Users\vinil\Desktop\Ciência da Computação - UNIP\sistema-turma-unip\static\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Removed shirt number field from registration form")
