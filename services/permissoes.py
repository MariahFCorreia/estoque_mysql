# services/permissoes.py - ATUALIZADO
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def requer_permissao(*permissoes):
    """
    Decorator para verificar permissões de usuário
    
    Uso:
    @requer_permissao('admin', 'ti')  # Apenas admin e TI
    @requer_permissao('vendedor')     # Apenas vendedores
    @requer_permissao('ti')           # Apenas TI
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Faça login para acessar esta página.', 'warning')
                return redirect(url_for('login'))
            
            if current_user.role not in permissoes:
                flash(f'Acesso não autorizado! Seu perfil ({current_user.role}) não tem permissão para esta função.', 'danger')
                
                # Redireciona para o painel apropriado baseado no role
                if current_user.role == 'vendedor':
                    return redirect(url_for('vendas.painel_vendas'))
                elif current_user.role == 'ti':
                    return redirect(url_for('ti.dashboard'))
                elif current_user.role == 'estoque':
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def is_admin():
    """Verifica se o usuário atual é administrador"""
    return current_user.is_authenticated and current_user.role == 'admin'

def is_ti():
    """Verifica se o usuário atual é do TI"""
    return current_user.is_authenticated and current_user.role == 'ti'

def is_vendedor():
    """Verifica se o usuário atual é vendedor"""
    return current_user.is_authenticated and current_user.role == 'vendedor'

def is_estoque():
    """Verifica se o usuário atual é gestor de estoque"""
    return current_user.is_authenticated and current_user.role == 'estoque'

def pode_gerenciar_usuarios():
    """Verifica se usuário pode gerenciar outros usuários"""
    return current_user.is_authenticated and current_user.role in ['admin']

def pode_gerenciar_licencas():
    """Verifica se usuário pode gerenciar licenças"""
    return current_user.is_authenticated and current_user.role in ['ti']

def pode_ver_relatorios():
    """Verifica se usuário pode ver relatórios avançados"""
    return current_user.is_authenticated and current_user.role in ['admin', 'estoque', 'ti']

def pode_fazer_vendas():
    """Verifica se usuário pode realizar vendas"""
    return current_user.is_authenticated and current_user.role in ['vendedor']

def pode_gerenciar_estoque():
    """Verifica se usuário pode gerenciar estoque"""
    return current_user.is_authenticated and current_user.role in ['admin', 'estoque']

# Mapeamento de permissões por role
PERMISSOES_POR_ROLE = {
    'admin': {
        'nome': 'Administrador',
        'descricao': 'Acesso completo ao sistema',
        'permissoes': [
            'gerenciar_usuarios',
            'gerenciar_estoque',
            'ver_relatorios',
            'configurar_sistema',
            'backup_dados'
        ]
    },
    'ti': {
        'nome': 'Técnico de TI',
        'descricao': 'Gerencia licenças e suporte técnico',
        'permissoes': [
            'gerenciar_licencas',
            'ver_relatorios',
            'suporte_tecnico',
            'backup_dados',
            'configurar_integracao'
        ]
    },
    'estoque': {
        'nome': 'Gestor de Estoque',
        'descricao': 'Gerencia estoque e movimentações',
        'permissoes': [
            'gerenciar_estoque',
            'ver_relatorios',
            'fazer_vendas'
        ]
    },
    'vendedor': {
        'nome': 'Vendedor',
        'descricao': 'Apenas realiza vendas',
        'permissoes': [
            'fazer_vendas',
            'ver_produtos',
            'consultar_estoque'
        ]
    }
}

def get_permissoes_usuario(role):
    """Retorna as permissões disponíveis para um role específico"""
    return PERMISSOES_POR_ROLE.get(role, {}).get('permissoes', [])

def get_descricao_role(role):
    """Retorna a descrição de um role"""
    role_info = PERMISSOES_POR_ROLE.get(role, {})
    return f"{role_info.get('nome', role)} - {role_info.get('descricao', 'Sem descrição')}"

def usuario_tem_permissao(permissao):
    """Verifica se o usuário atual tem uma permissão específica"""
    if not current_user.is_authenticated:
        return False
    
    permissoes_usuario = get_permissoes_usuario(current_user.role)
    return permissao in permissoes_usuario