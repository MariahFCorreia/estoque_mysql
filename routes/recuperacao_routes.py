from flask import Blueprint, request, jsonify, render_template, flash, redirect
from services.recuperacao_service import RecuperacaoSenhaService
from services.email_service import EmailService
from werkzeug.security import generate_password_hash
from database_mysql import execute_query

recuperacao_bp = Blueprint('recuperacao', __name__)

@recuperacao_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Página para solicitar recuperação de senha"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        ip_address = request.remote_addr
        
        # Sempre processa, mesmo se email não existir (segurança)
        sucesso = RecuperacaoSenhaService.criar_solicitacao(email, ip_address)
        
        if sucesso:
            flash('Se o email existir em nosso sistema, você receberá um link de recuperação em alguns minutos.', 'info')
        else:
            flash('Erro ao processar solicitação. Tente novamente.', 'danger')
            
        return render_template('esqueci_senha.html')
    
    return render_template('esqueci_senha.html')

@recuperacao_bp.route('/recuperar-senha/<token>', methods=['GET', 'POST'])
def recuperar_senha(token):
    """Página para redefinir senha com token válido"""
    # Validar token
    token_valido = RecuperacaoSenhaService.validar_token(token)
    
    if not token_valido:
        flash('Link de recuperação inválido ou expirado. Solicite um novo.', 'danger')
        return redirect('/esqueci-senha')
    
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not nova_senha or not confirmar_senha:
            flash('Preencha todos os campos.', 'danger')
            return render_template('redefinir_senha.html', token=token)
        
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('redefinir_senha.html', token=token)
        
        if len(nova_senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('redefinir_senha.html', token=token)
        
        try:
            # Atualizar senha
            password_hash = generate_password_hash(nova_senha)
            execute_query(
                'UPDATE usuarios SET password_hash = %s WHERE id = %s',
                (password_hash, token_valido['usuario_id'])
            )
            
            # Marcar token como utilizado
            RecuperacaoSenhaService.utilizar_token(token)
            
            # Resetar contador de tentativas
            execute_query(
                'UPDATE usuarios SET tentativas_recuperacao = 0 WHERE id = %s',
                (token_valido['usuario_id'],)
            )
            
            flash('Senha redefinida com sucesso! Você já pode fazer login.', 'success')
            return redirect('/login')
            
        except Exception as e:
            flash('Erro ao redefinir senha. Tente novamente.', 'danger')
            return render_template('redefinir_senha.html', token=token)
    
    return render_template('redefinir_senha.html', token=token, email=token_valido['email'])