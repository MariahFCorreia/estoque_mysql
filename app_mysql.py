#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from database_mysql import execute_query, create_database_if_not_exists
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sua_chave_secreta_mysql_altere_em_producao')

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe User para o Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Configuração do banco de dados MySQL
def init_db():
    try:
        # Criar database se não existir
        from database_mysql import create_database_if_not_exists
        create_database_if_not_exists()
        
        # Criar tabela de usuários
        execute_query('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(120),
            data_cadastro DATETIME NOT NULL,
            INDEX idx_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Criar tabela de produtos
        execute_query('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo INT UNIQUE NOT NULL,
            descricao TEXT NOT NULL,
            categoria VARCHAR(50) NOT NULL,
            quantidade INT NOT NULL,
            preco_unitario DECIMAL(10,2) NOT NULL,
            fornecedor VARCHAR(100) NOT NULL,
            estoque_minimo INT NOT NULL,
            data_validade DATE NULL,
            lote VARCHAR(50) NULL,
            data_cadastro DATETIME NOT NULL,
            INDEX idx_codigo (codigo),
            INDEX idx_categoria (categoria)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Criar tabela de movimentações
        execute_query('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            produto_id INT NOT NULL,
            tipo VARCHAR(10) NOT NULL,
            quantidade INT NOT NULL,
            data DATETIME NOT NULL,
            observacao TEXT NULL,
            usuario_id INT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
            INDEX idx_data (data),
            INDEX idx_produto (produto_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Inserir usuário admin padrão se não existir
        usuarios = execute_query('SELECT COUNT(*) as count FROM usuarios WHERE username = "admin"')
        if usuarios and usuarios[0]['count'] == 0:
            password_hash = generate_password_hash('admin123')
            execute_query('''
            INSERT INTO usuarios (username, password_hash, role, nome, email, data_cadastro)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('admin', password_hash, 'admin', 'Administrador', 'admin@empresa.com', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # Inserir alguns dados de exemplo de produtos
        produtos = execute_query('SELECT COUNT(*) as count FROM produtos')
        if produtos and produtos[0]['count'] == 0:
            produtos_exemplo = [
                (1001, 'Cimento CP II 50kg', 'CIMENTO', 500, 28.90, 'Votorantim', 100, '2024-12-31', 'LOTE001'),
                (1002, 'Areia Média m³', 'AGREGADOS', 200, 85.00, 'Pedreira São José', 50, None, None),
                (1003, 'Tijolo Baiano 1000un', 'CERÂMICOS', 150, 450.00, 'Cerâmica Santa Rita', 30, None, None),
                (1004, 'Vergalhão CA-50 6mm', 'FERRO_E_ACO', 80, 25.00, 'Gerdau', 20, None, None),
                (1005, 'Tinta Acrílica Branco Gelo 18L', 'TINTAS', 40, 189.90, 'Suvinil', 10, '2025-06-30', 'LOTE005')
            ]
            
            for produto in produtos_exemplo:
                execute_query('''
                INSERT INTO produtos (codigo, descricao, categoria, quantidade, preco_unitario, 
                                   fornecedor, estoque_minimo, data_validade, lote, data_cadastro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', produto + (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
                
        print("✅ Banco de dados MySQL inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados MySQL: {e}")
        raise
    
# Callback para carregar o usuário
@login_manager.user_loader
def load_user(user_id):
    try:
        user = execute_query('SELECT * FROM usuarios WHERE id = %s', (user_id,))
        if user:
            return User(user[0]['id'], user[0]['username'], user[0]['role'])
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
    return None

# Função para verificar se o usuário atual é administrador
def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'

# Rotas de autenticação (mantidas iguais)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            user = execute_query('SELECT * FROM usuarios WHERE username = %s', (username,))
            
            if user and check_password_hash(user[0]['password_hash'], password):
                user_obj = User(user[0]['id'], user[0]['username'], user[0]['role'])
                login_user(user_obj)
                
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                flash('Usuário ou senha incorretos!', 'danger')
        except Exception as e:
            flash(f'Erro ao fazer login: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        if nova_senha != confirmar_senha:
            flash('As novas senhas não coincidem!', 'danger')
            return render_template('alterar_senha.html')
        
        try:
            user = execute_query('SELECT * FROM usuarios WHERE id = %s', (current_user.id,))
            
            if user and check_password_hash(user[0]['password_hash'], senha_atual):
                new_password_hash = generate_password_hash(nova_senha)
                execute_query('UPDATE usuarios SET password_hash = %s WHERE id = %s', (new_password_hash, current_user.id))
                
                flash('Senha alterada com sucesso!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Senha atual incorreta!', 'danger')
        except Exception as e:
            flash(f'Erro ao alterar senha: {str(e)}', 'danger')
    
    return render_template('alterar_senha.html')

# Rotas principais (adaptadas para MySQL)
@app.route('/')
@login_required
def index():
    try:
        produtos = execute_query('SELECT * FROM produtos ORDER BY descricao')
        
        # Calcular valor total do estoque
        valor_total_result = execute_query('SELECT SUM(quantidade * preco_unitario) as total FROM produtos')
        valor_total = valor_total_result[0]['total'] if valor_total_result and valor_total_result[0]['total'] else 0
        
        # Verificar produtos com estoque baixo
        produtos_baixo_estoque = execute_query(
            'SELECT * FROM produtos WHERE quantidade <= estoque_minimo ORDER BY quantidade ASC'
        )
        
        return render_template('index.html', 
                             produtos=produtos, 
                             valor_total=valor_total,
                             produtos_baixo_estoque=produtos_baixo_estoque)
    except Exception as e:
        flash(f'Erro ao carregar página inicial: {str(e)}', 'danger')
        return render_template('index.html', produtos=[], valor_total=0, produtos_baixo_estoque=[])

# ... (todas as outras rotas mantidas com a mesma lógica, apenas trocando ? por %s)

@app.route('/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar_produto():
    if request.method == 'POST':
        try:
            codigo = int(request.form['codigo'])
            descricao = request.form['descricao']
            categoria = request.form['categoria']
            quantidade = int(request.form['quantidade'])
            preco_unitario = float(request.form['preco_unitario'])
            fornecedor = request.form['fornecedor']
            estoque_minimo = int(request.form['estoque_minimo'])
            data_validade = request.form['data_validade'] or None
            lote = request.form['lote'] or None
            
            # Verificar se código já existe
            existing = execute_query('SELECT id FROM produtos WHERE codigo = %s', (codigo,))
            if existing:
                flash('Erro: Código do produto já existe!', 'danger')
                return redirect(url_for('adicionar_produto'))
            
            execute_query('''
            INSERT INTO produtos (codigo, descricao, categoria, quantidade, preco_unitario, 
                               fornecedor, estoque_minimo, data_validade, lote, data_cadastro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (codigo, descricao, categoria, quantidade, preco_unitario, fornecedor, 
                  estoque_minimo, data_validade, lote, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Registrar a movimentação de entrada
            produto = execute_query('SELECT id FROM produtos WHERE codigo = %s', (codigo,))
            if produto:
                execute_query('''
                INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, observacao, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''', (produto[0]['id'], 'ENTRADA', quantidade, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                      'Cadastro inicial', current_user.id))
            
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('index'))
            
        except ValueError:
            flash('Erro: Valores numéricos inválidos!', 'danger')
        except Exception as e:
            flash(f'Erro ao adicionar produto: {str(e)}', 'danger')
    
    categorias = ['CIMENTO', 'AGREGADOS', 'CERÂMICOS', 'FERRO_E_ACO', 'MADEIRAS', 
                 'TINTAS', 'HIDRAULICA', 'ELETRICA', 'FERRAMENTAS', 'OUTROS']
    
    return render_template('adicionar_produto.html', categorias=categorias)

# ... (as demais rotas seguem o mesmo padrão, substituindo ? por %s)

@app.route('/movimentacoes')
@login_required
def movimentacoes():
    try:
        movimentacoes = execute_query('''
        SELECT m.*, p.descricao as produto_descricao, u.username as usuario
        FROM movimentacoes m 
        JOIN produtos p ON m.produto_id = p.id 
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.data DESC
        ''')
        
        return render_template('movimentacoes.html', movimentacoes=movimentacoes)
    except Exception as e:
        flash(f'Erro ao carregar movimentações: {str(e)}', 'danger')
        return render_template('movimentacoes.html', movimentacoes=[])

# Gestão de Usuários (Apenas para administradores)
@app.route('/usuarios')
@login_required
def usuarios():
    if not is_admin():
        flash('Acesso negado! Apenas administradores podem gerenciar usuários.', 'danger')
        return redirect(url_for('index'))
    
    try:
        usuarios = execute_query('SELECT id, username, role, nome, email, data_cadastro FROM usuarios ORDER BY nome')
        return render_template('usuarios.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Erro ao carregar usuários: {str(e)}', 'danger')
        return render_template('usuarios.html', usuarios=[])

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
def novo_usuario():
    if not is_admin():
        flash('Acesso negado! Apenas administradores podem criar usuários.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            username = request.form['username']
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            confirmar_senha = request.form['confirmar_senha']
            role = request.form['role']
            
            # Verificar se as senhas coincidem
            if senha != confirmar_senha:
                flash('As senhas não coincidem!', 'danger')
                return render_template('novo_usuario.html')
            
            # Verificar se o usuário já existe
            existing = execute_query('SELECT id FROM usuarios WHERE username = %s', (username,))
            if existing:
                flash('Erro: Nome de usuário já existe!', 'danger')
                return render_template('novo_usuario.html')
            
            # Criar hash da senha
            password_hash = generate_password_hash(senha)
            
            # Inserir novo usuário
            execute_query('''
            INSERT INTO usuarios (username, password_hash, role, nome, email, data_cadastro)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (username, password_hash, role, nome, email, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('usuarios'))
            
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
    
    return render_template('novo_usuario.html')

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if not is_admin():
        flash('Acesso negado! Apenas administradores podem editar usuários.', 'danger')
        return redirect(url_for('index'))
    
    try:
        usuario = execute_query('SELECT id, username, role, nome, email FROM usuarios WHERE id = %s', (id,))
        if not usuario:
            flash('Usuário não encontrado!', 'danger')
            return redirect(url_for('usuarios'))
        
        if request.method == 'POST':
            username = request.form['username']
            nome = request.form['nome']
            email = request.form['email']
            role = request.form['role']
            senha = request.form.get('senha')
            
            # Verificar se o username já existe (excluindo o usuário atual)
            existing = execute_query('SELECT id FROM usuarios WHERE username = %s AND id != %s', (username, id))
            if existing:
                flash('Erro: Nome de usuário já existe!', 'danger')
                return render_template('editar_usuario.html', usuario=usuario[0])
            
            # Atualizar usuário
            if senha:
                # Se foi fornecida uma nova senha, atualizar a senha
                password_hash = generate_password_hash(senha)
                execute_query('''
                UPDATE usuarios 
                SET username = %s, nome = %s, email = %s, role = %s, password_hash = %s 
                WHERE id = %s
                ''', (username, nome, email, role, password_hash, id))
            else:
                # Se não foi fornecida uma nova senha, manter a senha atual
                execute_query('''
                UPDATE usuarios 
                SET username = %s, nome = %s, email = %s, role = %s 
                WHERE id = %s
                ''', (username, nome, email, role, id))
            
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('usuarios'))
        
        return render_template('editar_usuario.html', usuario=usuario[0])
        
    except Exception as e:
        flash(f'Erro ao editar usuário: {str(e)}', 'danger')
        return redirect(url_for('usuarios'))

@app.route('/usuarios/excluir/<int:id>')
@login_required
def excluir_usuario(id):
    if not is_admin():
        flash('Acesso negado! Apenas administradores podem excluir usuários.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Não permitir que o administrador exclua a si mesmo
        if id == current_user.id:
            flash('Você não pode excluir sua própria conta!', 'danger')
            return redirect(url_for('usuarios'))
        
        # Verificar se o usuário existe
        usuario = execute_query('SELECT id FROM usuarios WHERE id = %s', (id,))
        if not usuario:
            flash('Usuário não encontrado!', 'danger')
            return redirect(url_for('usuarios'))
        
        # Excluir usuário
        execute_query('DELETE FROM usuarios WHERE id = %s', (id,))
        
        flash('Usuário excluído com sucesso!', 'success')
        return redirect(url_for('usuarios'))
        
    except Exception as e:
        flash(f'Erro ao excluir usuário: {str(e)}', 'danger')
        return redirect(url_for('usuarios'))

@app.route('/api/produtos')
@login_required
def api_produtos():
    try:
        produtos = execute_query('SELECT * FROM produtos ORDER BY descricao')
        return jsonify(produtos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos/<int:id>')
@login_required
def api_produto(id):
    try:
        produto = execute_query('SELECT * FROM produtos WHERE id = %s', (id,))
        if produto:
            return jsonify(produto[0])
        else:
            return jsonify({'error': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)