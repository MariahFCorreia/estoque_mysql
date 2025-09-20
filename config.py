# config.py - Configurações principais do sistema
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações básicas
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua_chave_secreta_muito_segura_altere_isto_123')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    # Database MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'estoque_construcao')
    MYSQL_USER = os.getenv('MYSQL_USER', 'estoque_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'sua_senha_segura_aqui')
    
    # Configurações de licença
    LICENCA_OBRIGATORIA = os.getenv('LICENCA_OBRIGATORIA', 'True').lower() in ['true', '1', 'yes']
    DIAS_AVISO_LICENCA = int(os.getenv('DIAS_AVISO_LICENCA', 7))
    
    # Email (para notificações)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    
    # Uploads
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Configuração de desenvolvimento
class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

# Configuração de produção
class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    LICENCA_OBRIGATORIA = True

# Configuração de teste
class TestingConfig(Config):
    TESTING = True
    DEBUG = True

# Selecionar configuração baseando-se no ambiente
if os.getenv('FLASK_ENV') == 'production':
    config = ProductionConfig()
elif os.getenv('FLASK_ENV') == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()