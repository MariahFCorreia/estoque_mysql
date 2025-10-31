import secrets
import string
from datetime import datetime, timedelta
from database_mysql import execute_query

class RecuperacaoSenhaService:
    
    @staticmethod
    def gerar_token_seguro():
        """Gera token seguro com 32 caracteres"""
        alfabeto = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alfabeto) for i in range(32))
    
    @staticmethod
    def criar_solicitacao(email, ip_address):
        """
        Cria solicitação de recuperação sem revelar se email existe
        Retorna True sempre para evitar user enumeration
        """
        try:
            # Buscar usuário sem revelar existência
            usuario = execute_query(
                'SELECT id, username, tentativas_recuperacao FROM usuarios WHERE email = %s', 
                (email,)
            )
            
            if not usuario:
                # Não revelar que email não existe
                return True
                
            usuario_id = usuario[0]['id']
            tentativas = usuario[0]['tentativas_recuperacao'] or 0
            
            # Rate limiting: máximo 3 tentativas por hora
            if tentativas >= 3:
                ultima_tentativa = execute_query(
                    'SELECT ultima_recuperacao FROM usuarios WHERE id = %s',
                    (usuario_id,)
                )
                if ultima_tentativa and ultima_tentativa[0]['ultima_recuperacao']:
                    tempo_decorrido = datetime.now() - ultima_tentativa[0]['ultima_recuperacao']
                    if tempo_decorrido.total_seconds() < 3600:  # 1 hora
                        return True  # Silenciosamente
                
                # Resetar contador se passou 1 hora
                execute_query(
                    'UPDATE usuarios SET tentativas_recuperacao = 0 WHERE id = %s',
                    (usuario_id,)
                )
            
            # Gerar token seguro
            token = RecuperacaoSenhaService.gerar_token_seguro()
            data_expiracao = datetime.now() + timedelta(hours=1)  # 1 hora de validade
            
            # Salvar token
            execute_query('''
                INSERT INTO recuperacao_senha 
                (usuario_id, token, data_criacao, data_expiracao, ip_solicitacao)
                VALUES (%s, %s, %s, %s, %s)
            ''', (usuario_id, token, datetime.now(), data_expiracao, ip_address))
            
            # Atualizar contador
            execute_query(
                'UPDATE usuarios SET tentativas_recuperacao = tentativas_recuperacao + 1, ultima_recuperacao = %s WHERE id = %s',
                (datetime.now(), usuario_id)
            )
            
            # Aqui você integraria com serviço de email
            # Por enquanto, vamos retornar o token para teste
            print(f"🔐 Token de recuperação para {email}: {token}")
            return True
            
        except Exception as e:
            print(f"Erro na recuperação: {e}")
            return True  # Sempre retorna True para segurança
    
    @staticmethod
    def validar_token(token):
        """Valida se token existe e não expirou"""
        try:
            resultado = execute_query('''
                SELECT r.*, u.email, u.username 
                FROM recuperacao_senha r
                JOIN usuarios u ON r.usuario_id = u.id
                WHERE r.token = %s AND r.utilizado = FALSE AND r.data_expiracao > %s
            ''', (token, datetime.now()))
            
            return resultado[0] if resultado else None
            
        except Exception as e:
            print(f"Erro na validação do token: {e}")
            return None
    
    @staticmethod
    def utilizar_token(token):
        """Marca token como utilizado"""
        execute_query(
            'UPDATE recuperacao_senha SET utilizado = TRUE WHERE token = %s',
            (token,)
        )