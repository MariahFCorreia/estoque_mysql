# licenca_routes.py - Rotas para gerenciamento de licenças
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
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

licenca_bp = Blueprint('licenca', __name__)

@licenca_bp.route('/licenca/ativar', methods=['GET', 'POST'])
def ativar_licenca():
    if not gerenciador_licencas:
        flash('❌ Sistema de licenças não disponível no momento', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        chave_licenca = request.form.get('chave_licenca', '').strip()
        
        if not chave_licenca:
            flash('Por favor, insira a chave de licença', 'danger')
            return render_template('ativar_licenca.html')
        
        # Verificar licença
        valida, mensagem = gerenciador_licencas.verificar_licenca(chave_licenca)
        
        if valida:
            # Salvar licença ativada no banco de dados
            try:
                from database_mysql import execute_query
                
                # Verificar se já existe uma licença ativa
                licenca_existente = execute_query(
                    "SELECT * FROM licencas_ativas WHERE ativa = TRUE LIMIT 1"
                )
                
                if licenca_existente:
                    # Atualizar licença existente
                    execute_query(
                        "UPDATE licencas_ativas SET chave_licenca = %s, data_ativacao = %s, usuario_id = %s, ultima_verificacao = %s WHERE ativa = TRUE",
                        (chave_licenca, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                         current_user.id if current_user.is_authenticated else None,
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )
                else:
                    # Inserir nova licença ativa
                    execute_query(
                        "INSERT INTO licencas_ativas (chave_licenca, data_ativacao, usuario_id, ultima_verificacao) VALUES (%s, %s, %s, %s)",
                        (chave_licenca, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                         current_user.id if current_user.is_authenticated else None,
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )
                
                flash('✅ Licença ativada com sucesso! Sistema liberado.', 'success')
                return render_template('licenca_sucesso.html', 
                                     chave_licenca=chave_licenca,
                                     mensagem=mensagem)
            except Exception as e:
                flash(f'❌ Erro ao salvar licença: {str(e)}', 'danger')
        else:
            flash(f'❌ Erro na ativação: {mensagem}', 'danger')
    
    return render_template('ativar_licenca.html')

@licenca_bp.route('/licenca/verificar')
@login_required
def verificar_licenca():
    try:
        from database_mysql import execute_query
        
        # Verificar se há licença ativa
        licenca_ativa = execute_query(
            "SELECT * FROM licencas_ativas WHERE ativa = TRUE ORDER BY data_ativacao DESC LIMIT 1"
        )
        
        if licenca_ativa and gerenciador_licencas:
            chave_licenca = licenca_ativa[0]['chave_licenca']
            valida, mensagem = gerenciador_licencas.verificar_licenca(chave_licenca)
            
            # Atualizar última verificação
            execute_query(
                "UPDATE licencas_ativas SET ultima_verificacao = %s WHERE id = %s",
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), licenca_ativa[0]['id'])
            )
            
            return jsonify({
                'valida': valida,
                'mensagem': mensagem,
                'licenca': licenca_ativa[0]
            })
        
        return jsonify({'valida': False, 'mensagem': 'Nenhuma licença ativa encontrada'})
    except Exception as e:
        return jsonify({'valida': False, 'mensagem': f'Erro na verificação: {str(e)}'})
    

@licenca_bp.route('/licenca/status')
@login_required
def status_licenca():
    """Página de status da licença atual - VERSÃO CORRIGIDA"""
    try:
        from database_mysql import execute_query
        from datetime import datetime
        
        licenca_ativa = execute_query(
            "SELECT * FROM licencas_ativas WHERE ativa = TRUE ORDER BY data_ativacao DESC LIMIT 1"
        ) or []
        
        status_info = {
            'ativa': False,
            'mensagem': 'Nenhuma licença ativa encontrada',
            'detalhes': None
        }
        
        if licenca_ativa and len(licenca_ativa) > 0:
            if gerenciador_licencas:
                chave_licenca = licenca_ativa[0]['chave_licenca']
                valida, mensagem = gerenciador_licencas.verificar_licenca(chave_licenca)
                
                status_info = {
                    'ativa': valida,
                    'mensagem': mensagem,
                    'detalhes': licenca_ativa[0]
                }
            else:
                status_info = {
                    'ativa': True,
                    'mensagem': 'Licença ativa (sistema offline)',
                    'detalhes': licenca_ativa[0]
                }
        
        return render_template('status_licenca.html', 
                             status=status_info,
                             now=datetime.now())
        
    except Exception as e:
        print(f"❌ Erro ao verificar status da licença: {e}")
        # Em caso de erro, mostrar página com mensagem de erro
        return render_template('status_licenca.html', 
                             status={'ativa': False, 'mensagem': f'Erro: {str(e)}', 'detalhes': None},
                             now=datetime.now())

# Middleware de verificação de licença
def verificar_licenca_middleware():
    """Middleware para verificar licença em todas as rotas"""
    from flask import request, redirect, url_for
    
    # Rotas que não requerem licença
    rotas_publicas = [
        'licenca.ativar_licenca',
        'licenca.verificar_licenca', 
        'licenca.status_licenca',
        'login',
        'logout',
        'static'
    ]
    
    if request.endpoint in rotas_publicas:
        return None
    
    try:
        from database_mysql import execute_query
        
        # Verificar se há licença ativa
        licenca_ativa = execute_query(
            "SELECT * FROM licencas_ativas WHERE ativa = TRUE ORDER BY data_ativacao DESC LIMIT 1"
        )
        
        if not licenca_ativa:
            # Redirecionar para ativação se não houver licença
            if request.endpoint != 'licenca.ativar_licenca':
                flash('❌ Sistema requer ativação de licença', 'warning')
                return redirect(url_for('licenca.ativar_licenca'))
            return None
        
        # Verificar validade da licença se o gerenciador estiver disponível
        if gerenciador_licencas:
            chave_licenca = licenca_ativa[0]['chave_licenca']
            valida, mensagem = gerenciador_licencas.verificar_licenca(chave_licenca)
            
            if not valida:
                if request.endpoint != 'licenca.ativar_licenca':
                    flash(f'❌ Licença inválida: {mensagem}', 'danger')
                    return redirect(url_for('licenca.ativar_licenca'))
                    
    except Exception as e:
        print(f"⚠️ Erro no middleware de licença: {e}")
        # Em caso de erro, permitir o acesso para não bloquear o sistema
        return None
    
    return None