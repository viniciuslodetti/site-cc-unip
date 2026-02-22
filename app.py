from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Fix for Render PostgreSQL URL (change postgres:// to postgresql://)
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB max
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== MODELS ====================

# Association table for many-to-many relationship between users and sports
user_sports = db.Table('user_sports',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('sport_id', db.Integer, db.ForeignKey('sports.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    ra = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(200), nullable=False)
    curso = db.Column(db.String(100), nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    numero_camisa = db.Column(db.Integer, unique=True, nullable=True)
    apelido = db.Column(db.String(100))  # Apelido na camisa
    tamanho_camisa = db.Column(db.String(10))  # P, M, G, GG, XG
    quantidade_camisa = db.Column(db.Integer, default=1)
    camisa_paga = db.Column(db.Boolean, default=False)  # Tag de pagamento (apenas ADM pode alterar)
    senha_hash = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(50), default='Aluno', nullable=False)  # Aluno, Professor, Responsável, Admin
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sports = db.relationship('Sport', secondary=user_sports, backref=db.backref('participants', lazy='dynamic'))
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys='Post.admin_id')
    
    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)
    
    def to_dict(self, include_sports=False):
        data = {
            'id': self.id,
            'ra': self.ra,
            'nome': self.nome,
            'curso': self.curso,
            'semestre': self.semestre,
            'turma': self.turma,
            'numero_camisa': self.numero_camisa,
            'apelido': self.apelido,
            'tamanho_camisa': self.tamanho_camisa,
            'quantidade_camisa': self.quantidade_camisa,
            'camisa_paga': self.camisa_paga if self.camisa_paga is not None else False,
            'cargo': self.cargo,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sports:
            data['sports'] = [sport.to_dict() for sport in self.sports]
        return data

class Sport(db.Model):
    __tablename__ = 'sports'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_participants=False):
        data = {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_participants:
            data['participants'] = [user.to_dict() for user in self.participants.all()]
            data['total_participants'] = self.participants.count()
        return data

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'aviso', 'foto', 'jogo'
    imagem_url = db.Column(db.String(500))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'tipo': self.tipo,
            'imagem_url': self.imagem_url,
            'admin_id': self.admin_id,
            'admin_nome': self.author.nome if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ==================== ROUTES ====================

# Serve index.html
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ==================== AUTH ROUTES ====================

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields (numero_camisa is now optional)
        required_fields = ['ra', 'nome', 'curso', 'semestre', 'turma', 'senha']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Check if RA already exists
        if User.query.filter_by(ra=data['ra']).first():
            return jsonify({'error': 'RA já cadastrado no sistema'}), 400
        
        # Check if numero_camisa already exists (if provided)
        if data.get('numero_camisa'):
            if User.query.filter_by(numero_camisa=data['numero_camisa']).first():
                return jsonify({'error': f'Número da camisa {data["numero_camisa"]} já está em uso'}), 400
        
        # Create new user
        user = User(
            ra=data['ra'],
            nome=data['nome'],
            curso=data['curso'],
            semestre=int(data['semestre']),
            turma=data['turma'],
            numero_camisa=int(data['numero_camisa']) if data.get('numero_camisa') else None,
            apelido=data.get('apelido'),
            cargo='Aluno',
            is_admin=False
        )
        user.set_password(data['senha'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Cadastro realizado com sucesso!',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('ra') or not data.get('senha'):
            return jsonify({'error': 'RA e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(ra=data['ra']).first()
        
        if not user or not user.check_password(data['senha']):
            return jsonify({'error': 'RA ou senha incorretos'}), 401
        
        # Create access token - identity must be string
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'access_token': access_token,
            'user': user.to_dict(include_sports=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login-camisa', methods=['POST'])
def login_camisa():
    try:
        data = request.get_json()
        
        if not data.get('numero_camisa') or not data.get('senha'):
            return jsonify({'error': 'Número da camisa e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(numero_camisa=int(data['numero_camisa'])).first()
        
        if not user:
            return jsonify({'error': 'Número da camisa não encontrado'}), 401
        
        if not user.check_password(data['senha']):
            return jsonify({'error': 'Senha incorreta'}), 401
        
        # Create access token - identity must be string
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'access_token': access_token,
            'user': user.to_dict(include_sports=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify(user.to_dict(include_sports=True)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== USER ROUTES ====================

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem acessar esta rota'}), 403
        
        users = User.query.all()
        return jsonify([user.to_dict(include_sports=True) for user in users]), 200
        
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(current_user_id)
        
        # Only admin or the user themselves can update
        if not current_user.is_admin and current_user_id != user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Check if numero_camisa is being changed and if it's already in use
        if 'numero_camisa' in data and data['numero_camisa'] != user.numero_camisa:
            if data['numero_camisa']:  # Only check if not None
                existing = User.query.filter_by(numero_camisa=data['numero_camisa']).first()
                if existing and existing.id != user_id:
                    return jsonify({'error': f'Número da camisa {data["numero_camisa"]} já está em uso'}), 400
        
        # Update allowed fields
        if 'nome' in data:
            user.nome = data['nome']
        if 'curso' in data:
            user.curso = data['curso']
        if 'semestre' in data:
            user.semestre = int(data['semestre'])
        if 'turma' in data:
            user.turma = data['turma']
        if 'numero_camisa' in data:
            user.numero_camisa = int(data['numero_camisa']) if data['numero_camisa'] else None
        if 'apelido' in data:
            user.apelido = data['apelido']
        if 'tamanho_camisa' in data:
            user.tamanho_camisa = data['tamanho_camisa']
        if 'quantidade_camisa' in data:
            try:
                user.quantidade_camisa = int(data['quantidade_camisa'])
            except:
                user.quantidade_camisa = 1
        
        # Only admin can change admin status, cargo and camisa_paga
        if current_user.is_admin:
            if 'is_admin' in data:
                user.is_admin = bool(data['is_admin'])
            if 'cargo' in data:
                user.cargo = data['cargo']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário atualizado com sucesso!',
            'user': user.to_dict(include_sports=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(current_user_id)
        
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem deletar usuários'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== SPORT ROUTES ====================

@app.route('/api/sports', methods=['GET'])
def get_sports():
    try:
        include_participants = request.args.get('include_participants', 'false').lower() == 'true'
        sports = Sport.query.all()
        return jsonify([sport.to_dict(include_participants=include_participants) for sport in sports]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sports', methods=['POST'])
@jwt_required()
def create_sport():
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(user_id)
        
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem criar esportes'}), 403
        
        data = request.get_json()
        
        if not data.get('nome'):
            return jsonify({'error': 'Nome do esporte é obrigatório'}), 400
        
        # Check if sport already exists
        if Sport.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Esporte já cadastrado'}), 400
        
        sport = Sport(
            nome=data['nome'],
            descricao=data.get('descricao', '')
        )
        
        db.session.add(sport)
        db.session.commit()
        
        return jsonify({
            'message': 'Esporte criado com sucesso!',
            'sport': sport.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sports/<int:sport_id>/join', methods=['POST'])
@jwt_required()
def join_sport(sport_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        user = User.query.get(user_id)
        sport = Sport.query.get(sport_id)
        
        if not sport:
            return jsonify({'error': 'Esporte não encontrado'}), 404
        
        # Check if already in THIS sport
        if sport in user.sports:
            return jsonify({'error': 'Você já está participando deste esporte'}), 400
            
        # Check if in ANY sport (limit to 1) and remove if so
        if len(user.sports) > 0:
            user.sports = [] # Remove all other sports
        
        user.sports.append(sport)
        db.session.commit()
        
        return jsonify({
            'message': f'Você agora está participando de {sport.nome}!',
            'sport': sport.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sports/<int:sport_id>/leave', methods=['POST'])
@jwt_required()
def leave_sport(sport_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        user = User.query.get(user_id)
        sport = Sport.query.get(sport_id)
        
        if not sport:
            return jsonify({'error': 'Esporte não encontrado'}), 404
        
        if sport not in user.sports:
            return jsonify({'error': 'Você não está participando deste esporte'}), 400
        
        user.sports.remove(sport)
        db.session.commit()
        
        return jsonify({
            'message': f'Você saiu de {sport.nome}',
            'sport': sport.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sports/<int:sport_id>', methods=['DELETE'])
@jwt_required()
def delete_sport(sport_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(user_id)
        
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem deletar esportes'}), 403
        
        sport = Sport.query.get(sport_id)
        if not sport:
            return jsonify({'error': 'Esporte não encontrado'}), 404
        
        # Remove sport from all participants first (optional, but good for clarity)
        # SQLAlchemy handles this with the relationship if not explicitly stated, 
        # but here we can just delete the sport and it should clear the association table.
        
        db.session.delete(sport)
        db.session.commit()
        
        return jsonify({'message': 'Esporte deletado com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        tipo = request.args.get('tipo')
        
        query = Post.query
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        posts = query.order_by(Post.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(user_id)
        
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem criar postagens'}), 403
        
        # Handle multipart form data (for image upload)
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        tipo = request.form.get('tipo')
        
        if not titulo or not conteudo or not tipo:
            return jsonify({'error': 'Título, conteúdo e tipo são obrigatórios'}), 400
        
        if tipo not in ['aviso', 'foto', 'jogo']:
            return jsonify({'error': 'Tipo inválido. Use: aviso, foto ou jogo'}), 400
        
        imagem_url = None
        
        # Handle image upload
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagem_url = f"/uploads/{filename}"
        
        post = Post(
            titulo=titulo,
            conteudo=conteudo,
            tipo=tipo,
            imagem_url=imagem_url,
            admin_id=user_id
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Postagem criada com sucesso!',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(user_id)
        
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem editar postagens'}), 403
        
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Postagem não encontrada'}), 404
        
        # Handle multipart form data
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        tipo = request.form.get('tipo')
        
        if titulo:
            post.titulo = titulo
        if conteudo:
            post.conteudo = conteudo
        if tipo and tipo in ['aviso', 'foto', 'jogo']:
            post.tipo = tipo
        
        # Handle new image upload
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image if exists
                if post.imagem_url:
                    old_filepath = os.path.join('static', post.imagem_url.lstrip('/'))
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                post.imagem_url = f"/uploads/{filename}"
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Postagem atualizada com sucesso!',
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        current_user = User.query.get(user_id)
        
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem deletar postagens'}), 403
        
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Postagem não encontrada'}), 404
        
        # Delete associated image if exists
        if post.imagem_url:
            filepath = os.path.join('static', post.imagem_url.lstrip('/'))
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Postagem deletada com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== UTILITY ROUTES ====================

@app.route('/api/check-ra/<ra>', methods=['GET'])
def check_ra(ra):
    """Check if RA is available"""
    user = User.query.filter_by(ra=ra).first()
    return jsonify({'available': user is None}), 200

@app.route('/api/check-camisa/<int:numero>', methods=['GET'])
def check_camisa(numero):
    """Check if shirt number is available"""
    user = User.query.filter_by(numero_camisa=numero).first()
    return jsonify({'available': user is None}), 200

@app.route('/api/users/<int:user_id>/pagar-camisa', methods=['POST'])
@jwt_required()
def toggle_camisa_paga(user_id):
    """Toggle payment status of shirt - ADM only"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Apenas administradores podem alterar o status de pagamento.'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Toggle the payment status
        user.camisa_paga = not bool(user.camisa_paga)
        db.session.commit()

        status = 'PAGO' if user.camisa_paga else 'NÃO PAGO'
        return jsonify({
            'message': f'Status de pagamento atualizado para {status}',
            'camisa_paga': user.camisa_paga,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(ra='admin').first():
            admin = User(
                ra='admin',
                nome='Administrador',
                curso='Ciência da Computação',
                semestre=8,
                turma='A',
                numero_camisa=None,
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create sample sports if not exist
        sports_data = [
            {'nome': 'Futebol', 'descricao': 'Futebol de campo ou society'},
            {'nome': 'Vôlei', 'descricao': 'Vôlei de quadra'},
            {'nome': 'Basquete', 'descricao': 'Basquete 5x5'},
            {'nome': 'Futsal', 'descricao': 'Futebol de salão'},
            {'nome': 'Handebol', 'descricao': 'Handebol de quadra'},
        ]
        
        for sport_data in sports_data:
            if not Sport.query.filter_by(nome=sport_data['nome']).first():
                sport = Sport(**sport_data)
                db.session.add(sport)
        
        db.session.commit()
        print("✅ Database initialized successfully!")

# Initialize database on import (for Render/Gunicorn)
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
