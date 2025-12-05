# routes/vendas_routes.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from database_mysql import execute_query
from services.permissoes import requer_permissao
from datetime import datetime
import math

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/painel-vendas')
@login_required
@requer_permissao('admin', 'vendedor')
def painel_vendas():
    """Dashboard do vendedor"""
    try:
        # Estatísticas do dia
        vendas_hoje = execute_query('''
            SELECT COUNT(*) as total, COALESCE(SUM(valor_total), 0) as valor_total
            FROM vendas 
            WHERE DATE(data_venda) = CURDATE() AND vendedor_id = %s
        ''', (current_user.id,))
        
        # Total de produtos disponíveis
        total_produtos = execute_query('SELECT COUNT(*) as total FROM produtos WHERE quantidade > 0')
        
        # Vendas recentes (últimas 5)
        vendas_recentes = execute_query('''
            SELECT * FROM vendas 
            WHERE vendedor_id = %s 
            ORDER BY data_venda DESC 
            LIMIT 5
        ''', (current_user.id,))
        
        return render_template('vendas/dashboard_vendas.html', 
                             vendas_hoje=vendas_hoje[0] if vendas_hoje else {'total': 0, 'valor_total': 0},
                             total_produtos=total_produtos[0]['total'] if total_produtos else 0,
                             vendas_recentes=vendas_recentes)
                             
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return render_template('vendas/dashboard_vendas.html', 
                             vendas_hoje={'total': 0, 'valor_total': 0},
                             total_produtos=0,
                             vendas_recentes=[])

@vendas_bp.route('/venda-rapida')
@login_required
@requer_permissao('admin', 'vendedor')
def venda_rapida():
    """Interface de venda rápida"""
    # Se veio com produto pré-selecionado
    produto_id = request.args.get('produto')
    produto = None
    if produto_id:
        produto = execute_query('SELECT * FROM produtos WHERE id = %s', (produto_id,))
        produto = produto[0] if produto else None
    
    return render_template('vendas/venda_rapida.html', produto=produto)

@vendas_bp.route('/api/produtos-venda')
@login_required
@requer_permissao('admin', 'vendedor')
def api_produtos_venda():
    """API para busca de produtos no painel de vendas"""
    query = request.args.get('q', '')
    
    try:
        produtos = execute_query('''
            SELECT id, codigo, descricao, preco_unitario, quantidade, estoque_minimo
            FROM produtos 
            WHERE (codigo LIKE %s OR descricao LIKE %s)
            AND quantidade > 0
            ORDER BY 
                CASE WHEN quantidade <= estoque_minimo THEN 0 ELSE 1 END,
                descricao
            LIMIT 20
        ''', (f'%{query}%', f'%{query}%'))
        
        return jsonify(produtos)
        
    except Exception as e:
        return jsonify([])

@vendas_bp.route('/venda/finalizar', methods=['POST'])
@login_required
@requer_permissao('admin', 'vendedor')
def finalizar_venda():
    """Finaliza uma venda rápida"""
    try:
        data = request.get_json()
        produto_id = data['produto_id']
        quantidade = int(data['quantidade'])
        cliente_nome = data.get('cliente_nome', 'Consumidor Final').strip()
        
        if not cliente_nome:
            cliente_nome = 'Consumidor Final'
        
        # Verificar estoque
        produto = execute_query('SELECT * FROM produtos WHERE id = %s', (produto_id,))
        if not produto:
            return jsonify({'success': False, 'error': 'Produto não encontrado'})
        
        produto = produto[0]
        
        if produto['quantidade'] < quantidade:
            return jsonify({'success': False, 'error': f'Estoque insuficiente. Disponível: {produto["quantidade"]}'})
        
        if quantidade <= 0:
            return jsonify({'success': False, 'error': 'Quantidade deve ser maior que zero'})
        
        # Calcular valores
        valor_total = float(produto['preco_unitario']) * quantidade
        
        # Gerar código da venda
        codigo_venda = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Inserir venda
        execute_query('''
            INSERT INTO vendas (codigo, cliente_nome, vendedor_id, data_venda, valor_total, status)
            VALUES (%s, %s, %s, %s, %s, 'finalizada')
        ''', (codigo_venda, cliente_nome, current_user.id, datetime.now(), valor_total))
        
        # Pegar ID da venda inserida
        venda_inserida = execute_query('SELECT id FROM vendas WHERE codigo = %s', (codigo_venda,))
        venda_id = venda_inserida[0]['id'] if venda_inserida else None
        
        if not venda_id:
            return jsonify({'success': False, 'error': 'Erro ao criar venda'})
        
        # Inserir item da venda
        execute_query('''
            INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario, valor_total)
            VALUES (%s, %s, %s, %s, %s)
        ''', (venda_id, produto_id, quantidade, produto['preco_unitario'], valor_total))
        
        # Baixar estoque
        execute_query('''
            UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s
        ''', (quantidade, produto_id))
        
        # Registrar movimentação
        execute_query('''
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, observacao, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (produto_id, 'SAIDA', quantidade, datetime.now(), f'Venda #{codigo_venda} - {cliente_nome}', current_user.id))
        
        return jsonify({
            'success': True, 
            'venda_id': venda_id,
            'codigo_venda': codigo_venda,
            'valor_total': valor_total,
            'mensagem': f'Venda {codigo_venda} finalizada com sucesso! Total: R$ {valor_total:.2f}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@vendas_bp.route('/historico-vendas')
@login_required
@requer_permissao('admin', 'vendedor')
def historico_vendas():
    """Histórico de vendas do vendedor"""
    try:
        # Paginação
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 10
        
        # Total de vendas
        total_vendas = execute_query('''
            SELECT COUNT(*) as total FROM vendas WHERE vendedor_id = %s
        ''', (current_user.id,))
        total = total_vendas[0]['total'] if total_vendas else 0
        
        # Vendas com paginação
        vendas = execute_query('''
            SELECT v.*, 
                   GROUP_CONCAT(CONCAT(vi.quantidade, 'x ', p.descricao) SEPARATOR '; ') as itens
            FROM vendas v
            LEFT JOIN venda_itens vi ON v.id = vi.venda_id
            LEFT JOIN produtos p ON vi.produto_id = p.id
            WHERE v.vendedor_id = %s
            GROUP BY v.id
            ORDER BY v.data_venda DESC
            LIMIT %s OFFSET %s
        ''', (current_user.id, por_pagina, (pagina - 1) * por_pagina))
        
        total_paginas = math.ceil(total / por_pagina) if total > 0 else 1
        
        return render_template('vendas/historico_vendas.html',
                             vendas=vendas,
                             pagina=pagina,
                             total_paginas=total_paginas,
                             total=total)
                             
    except Exception as e:
        flash(f'Erro ao carregar histórico: {str(e)}', 'danger')
        return render_template('vendas/historico_vendas.html',
                             vendas=[],
                             pagina=1,
                             total_paginas=1,
                             total=0)