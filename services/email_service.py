class EmailService:
    
    @staticmethod
    def enviar_email_recuperacao(email, token):
        """
        Simula envio de email com link de recuperação
        Em produção, integrar com SendGrid, Mailgun, etc.
        """
        # URL de recuperação (ajustar para sua URL)
        url_recuperacao = f"http://localhost:5000/recuperar-senha/{token}"
        
        assunto = "Recuperação de Senha - Sistema de Estoque"
        mensagem = f"""
        Olá,
        
        Você solicitou a recuperação de senha para sua conta no Sistema de Estoque.
        
        Clique no link abaixo para redefinir sua senha (válido por 1 hora):
        {url_recuperacao}
        
        Se você não solicitou esta recuperação, ignore este email.
        
        Atenciosamente,
        Sistema de Estoque
        """
        
        # Em produção, enviar email real aqui
        print(f"📧 Email simulado para {email}:")
        print(f"Assunto: {assunto}")
        print(f"Mensagem: {mensagem}")
        print(f"URL: {url_recuperacao}")
        
        return True