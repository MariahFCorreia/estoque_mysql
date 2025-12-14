# routes/ti_routes.py - Blueprint para usuários de TI - VERSÃO CORRIGIDA
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from services.permissoes import requer_permissao
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from licenca_config import gerenciador_licencas
    from datetime import datetime
    import json
except ImportError as e:
    print(f"⚠️ Módulos de licença não disponíveis: {e}")
    gerenciador_licencas = None

ti_bp = Blueprint('ti', __name__)

@ti_bp.route('/ti/dashboard')
@login_required
@requer_permissao('ti')
def dashboard():
    """Dashboard do TI - VERSÃO CORRIGIDA"""
    try:
        from database_mysql import execute_query
        
        # Estatísticas gerais - CORRIGIDO
        usuarios_total_result = execute_query('SELECT COUNT(*) as total FROM usuarios')
        produtos_total_result = execute_query('SELECT COUNT(*) as total FROM produtos')
        licencas_ativas_result = execute_query('SELECT COUNT(*) as total FROM licencas_ativas WHERE ativa = TRUE')
        
        # Extrair valores dos resultados
        usuarios_total = usuarios_total_result[0]['total'] if usuarios_total_result else 0
        produtos_total = produtos_total_result[0]['total'] if produtos_total_result else 0
        licencas_ativas = licencas_ativas_result[0]['total'] if licencas_ativas_result else 0
        
        # Últimas licenças ativadas
        ultimas_licencas = execute_query('''
            SELECT la.*, u.username, u.nome 
            FROM licencas_ativas la
            LEFT JOIN usuarios u ON la.usuario_id = u.id
            ORDER BY la.data_ativacao DESC 
            LIMIT 5
        ''') or []
        
        # Verificar status da licença atual - CORRIGIDO
        status_info = {'ativa': False, 'mensagem': 'Não verificada'}
        if gerenciador_licencas:
            licenca_ativa = execute_query(
                "SELECT * FROM licencas_ativas WHERE ativa = TRUE ORDER BY data_ativacao DESC LIMIT 1"
            )
            if licenca_ativa:
                valida, mensagem = gerenciador_licencas.verificar_licenca(licenca_ativa[0]['chave_licenca'])
                status_info = {'ativa': valida, 'mensagem': mensagem}
        
        return render_template('ti/dashboard.html',
                             usuarios_total=usuarios_total,
                             produtos_total=produtos_total,
                             licencas_ativas=licencas_ativas,
                             ultimas_licencas=ultimas_licencas,
                             status_info=status_info)  # Alterado para status_info
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        # Retornar valores padrão em caso de erro
        return render_template('ti/dashboard.html',
                             usuarios_total=0,
                             produtos_total=0,
                             licencas_ativas=0,
                             ultimas_licencas=[],
                             status_info={'ativa': False, 'mensagem': 'Erro ao verificar'})

# ... restante do código permanece o mesmo ...
@ti_bp.route('/ti/licencas')
@login_required
@requer_permissao('ti')
def gerenciar_licencas():
    """Gerenciamento de licenças"""
    if not gerenciador_licencas:
        flash('❌ Sistema de licenças não disponível', 'danger')
        return redirect(url_for('ti.dashboard'))
    
    try:
        licencas = gerenciador_licencas.listar_licencas() or {}
        estatisticas = gerenciador_licencas.estatisticas()
        
        return render_template('ti/licencas.html', 
                             licencas=licencas,
                             estatisticas=estatisticas)
    except Exception as e:
        flash(f'❌ Erro ao carregar licenças: {str(e)}', 'danger')
        return redirect(url_for('ti.dashboard'))

# ... resto do código ...


@ti_bp.route('/ti/licenca/gerar', methods=['POST'])
@login_required
@requer_permissao('ti')
def gerar_licenca():
    """Gerar nova licença"""
    if not gerenciador_licencas:
        return jsonify({'success': False, 'message': 'Sistema de licenças não disponível'})
    
    try:
        data = request.get_json()
        cliente = data.get('cliente')
        email = data.get('email')
        cnpj = data.get('cnpj')
        dias = int(data.get('dias', 365))
        tipo = data.get('tipo', 'standard')
        valor = float(data.get('valor', 0))
        
        if not cliente or not email:
            return jsonify({'success': False, 'message': 'Cliente e email são obrigatórios'})
        
        chave, expiracao = gerenciador_licencas.gerar_licenca(
            cliente, email, cnpj, dias, tipo, valor
        )
        
        if chave:
            # Registrar no banco de dados
            from database_mysql import execute_query
            execute_query(
                "INSERT INTO licencas_ativas (chave_licenca, data_ativacao, usuario_id, ultima_verificacao) VALUES (%s, %s, %s, %s)",
                (chave, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                 current_user.id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            
            return jsonify({
                'success': True,
                'message': 'Licença gerada com sucesso',
                'licenca': chave,
                'expiracao': expiracao
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao gerar licença'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@ti_bp.route('/ti/licenca/desativar/<string:chave>')
@login_required
@requer_permissao('ti')
def desativar_licenca(chave):
    """Desativar uma licença"""
    if not gerenciador_licencas:
        return jsonify({'success': False, 'message': 'Sistema de licenças não disponível'})
    
    try:
        success = gerenciador_licencas.desativar_licenca(chave)
        if success:
            # Atualizar no banco de dados
            from database_mysql import execute_query
            execute_query(
                "UPDATE licencas_ativas SET ativa = FALSE WHERE chave_licenca = %s",
                (chave,)
            )
            return jsonify({'success': True, 'message': 'Licença desativada com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Licença não encontrada'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@ti_bp.route('/ti/licenca/renovar/<string:chave>', methods=['POST'])
@login_required
@requer_permissao('ti')
def renovar_licenca(chave):
    """Renovar uma licença expirada"""
    if not gerenciador_licencas:
        return jsonify({'success': False, 'message': 'Sistema de licenças não disponível'})
    
    try:
        data = request.get_json()
        dias_adicionais = int(data.get('dias', 365))
        
        # Verificar se a licença existe
        if chave not in gerenciador_licencas.licencas:
            return jsonify({'success': False, 'message': 'Licença não encontrada'})
        
        licenca = gerenciador_licencas.licencas[chave]
        
        # Calcular nova data de expiração
        from datetime import datetime, timedelta
        data_expiracao = datetime.strptime(licenca['data_expiracao'], '%Y-%m-%d')
        nova_expiracao = data_expiracao + timedelta(days=dias_adicionais)
        
        # Atualizar licença
        licenca['data_expiracao'] = nova_expiracao.strftime('%Y-%m-%d')
        licenca['ativa'] = True
        
        # Salvar alterações
        gerenciador_licencas.salvar_licencas()
        
        return jsonify({
            'success': True,
            'message': f'Licença renovada por {dias_adicionais} dias',
            'nova_expiracao': licenca['data_expiracao']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@ti_bp.route('/ti/usuarios/licencas')
@login_required
@requer_permissao('ti')
def usuarios_licencas():
    """Listar usuários com informações de licença - VERSÃO SIMPLIFICADA"""
    try:
        from database_mysql import execute_query
        
        usuarios = execute_query('''
            SELECT u.id, u.username, u.nome, u.email, u.role, u.data_cadastro,
                   COUNT(la.id) as total_licencas,
                   MAX(la.data_ativacao) as ultima_ativacao
            FROM usuarios u
            LEFT JOIN licencas_ativas la ON u.id = la.usuario_id
            GROUP BY u.id
            ORDER BY u.nome
        ''') or []  # Garantir que seja uma lista
        
        return render_template('ti/usuarios_licencas.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Erro ao carregar usuários: {str(e)}', 'danger')
        return render_template('ti/usuarios_licencas.html', usuarios=[])
@ti_bp.route('/ti/backup')
@login_required
@requer_permissao('ti', 'admin')
def backup_sistema():
    """Página de backup do sistema - VERSÃO SIMPLIFICADA"""
    import os
    from datetime import datetime
    
    backup_dir = 'backups'
    backups = []
    
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Listar backups existentes de forma simplificada
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.endswith('.json') or file.endswith('.csv'):
                    file_path = os.path.join(backup_dir, file)
                    if os.path.isfile(file_path):
                        stats = os.stat(file_path)
                        backups.append({
                            'nome': file,
                            'tamanho': stats.st_size,
                            'data_modificacao': datetime.fromtimestamp(stats.st_mtime),
                            'caminho': file_path
                        })
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['data_modificacao'], reverse=True)
        
        return render_template('ti/backup.html', backups=backups)
    except Exception as e:
        print(f"Erro no backup: {e}")
        return render_template('ti/backup.html', backups=[])

@ti_bp.route('/ti/licenca/exportar')
@login_required
@requer_permissao('ti')
def exportar_licencas():
    """Exportar todas as licenças para CSV"""
    if not gerenciador_licencas:
        flash('Sistema de licenças não disponível', 'danger')
        return redirect(url_for('ti.dashboard'))
    
    try:
        import csv
        from io import StringIO
        from flask import make_response
        
        licencas = gerenciador_licencas.listar_licencas()
        
        # Criar CSV em memória
        output = StringIO()
        writer = csv.writer(output)
        
        # Escrever cabeçalho
        writer.writerow(['Chave', 'Cliente', 'Email', 'CNPJ', 'Tipo', 'Valor Pago', 
                        'Data Geração', 'Data Expiração', 'Status', 'Ativações'])
        
        # Escrever dados
        for chave, licenca in licencas.items():
            writer.writerow([
                chave,
                licenca['cliente'],
                licenca['email'],
                licenca['cnpj'] or '',
                licenca['tipo'],
                licenca['valor_pago'],
                licenca['data_geracao'],
                licenca['data_expiracao'],
                'Ativa' if licenca['ativa'] else 'Inativa',
                licenca.get('ativacoes', 0)
            ])
        
        # Criar resposta
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=licencas_exportadas.csv'
        response.headers['Content-type'] = 'text/csv'
        
        return response
    except Exception as e:
        flash(f'Erro ao exportar licenças: {str(e)}', 'danger')
        return redirect(url_for('ti.gerenciar_licencas'))