# licenca_routes.py - Rotas para gerenciamento de licenças
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from licenca_config import gerenciador_licencas
from datetime import datetime
import json

licenca_bp = Blueprint('licenca', __name__)

@licenca_bp.route('/licenca/ativar', methods=['GET', 'POST'])
def ativar_licenca():
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
                execute_query(
                    "INSERT INTO licencas_ativas (chave_licenca, data_ativacao, usuario_id) VALUES (%s, %s, %s)",
                    (chave_licenca, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), current_user.id if current_user.is_authenticated else None)
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
            "SELECT * FROM licencas_ativas ORDER BY data_ativacao DESC LIMIT 1"
        )
        
        if licenca_ativa:
            chave_licenca = licenca_ativa[0]['chave_licenca']
            valida, mensagem = gerenciador_licencas.verificar_licenca(chave_licenca)
            
            return jsonify({
                'valida': valida,
                'mensagem': mensagem,
                'licenca': licenca_ativa[0]
            })
        
        return jsonify({'valida': False, 'mensagem': 'Nenhuma licença ativa encontrada'})
    except Exception as e:
        return jsonify({'valida': False, 'mensagem': f'Erro na verificação: {str(e)}'})

@licenca_bp.route('/admin/licencas')
@login_required
def admin_licencas():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('❌ Acesso restrito a administradores', 'danger')
        return redirect(url_for('index'))
    
    try:
        licencas = gerenciador_licencas.listar_licencas()
        estatisticas = gerenciador_licencas.estatisticas()
        
        return render_template('admin_licencas.html', 
                             licencas=licencas,
                             estatisticas=estatisticas)
    except Exception as e:
        flash(f'❌ Erro ao carregar licenças: {str(e)}', 'danger')
        return redirect(url_for('index'))

@licenca_bp.route('/admin/licenca/gerar', methods=['POST'])
@login_required
def admin_gerar_licenca():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        data = request.get_json()
        cliente = data.get('cliente')
        email = data.get('email')
        cnpj = data.get('cnpj')
        dias = int(data.get('dias', 365))
        tipo = data.get('tipo', 'standard')
        valor = float(data.get('valor', 0))
        
        chave, expiracao = gerenciador_licencas.gerar_licenca(
            cliente, email, cnpj, dias, tipo, valor
        )
        
        if chave:
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

# Middleware de verificação de licença
def verificar_licenca_middleware():
    """Middleware para verificar licença em todas as rotas"""
    from flask import request, redirect, url_for
    
    # Rotas que não requerem licença
    rotas_publicas = [
        'licenca.ativar_licenca',
        'licenca.verificar_licenca', 
        'login',
        'static',
        'licenca.licenca_sucesso'
    ]
    
    if request.endpoint in rotas_publicas:
        return
    
    try:
        from database_mysql import execute_query
        from licenca_config import gerenciador_licencas
        
        # Verificar se há licença ativa
        licenca_ativa = execute_query(
            "SELECT * FROM licencas_ativas ORDER BY data_ativacao DESC LIMIT 1"
        )
        
        if not licenca_ativa:
            return redirect(url_for('licenca.ativar_licenca'))
        
        # Verificar validade da licença
        chave_licenca = licenca_ativa[0]['chave_licenca']
        valida, mensagem = gerenciador_licencas.verificar_licenca(chave_licenca)
        
        if not valida:
            flash(f'❌ Licença inválida: {mensagem}', 'danger')
            return redirect(url_for('licenca.ativar_licenca'))
            
    except Exception as e:
        flash(f'❌ Erro na verificação de licença: {str(e)}', 'danger')
        return redirect(url_for('licenca.ativar_licenca'))