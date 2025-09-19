import os
import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """
    Estabelece conexão com MySQL usando variáveis de ambiente individuais
    """
    try:
        # Obter configurações do ambiente
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = int(os.getenv('MYSQL_PORT', 3306))
        database = os.getenv('MYSQL_DATABASE', 'estoque_construcao')
        username = os.getenv('MYSQL_USER', 'estoque_user')
        password = os.getenv('MYSQL_PASSWORD', '')
        
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
        
        logger.info("Conexão MySQL estabelecida com sucesso")
        return connection
        
    except Error as e:
        logger.error(f"Erro ao conectar com MySQL: {e}")
        raise

def execute_query(query, params=None):
    """
    Executa queries no MySQL de forma segura
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Para SELECT statements
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            # Para INSERT, UPDATE, DELETE
            connection.commit()
            return cursor.rowcount
            
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Erro na query: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def test_connection():
    """Testa a conexão com o MySQL"""
    try:
        connection = get_db_connection()
        if connection.is_connected():
            logger.info("✅ Conexão MySQL testada com sucesso!")
            return True
    except Error as e:
        logger.error(f"❌ Falha na conexão MySQL: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def create_database_if_not_exists():
    """Cria o banco de dados se não existir"""
    try:
        # Obter configurações
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = int(os.getenv('MYSQL_PORT', 3306))
        database = os.getenv('MYSQL_DATABASE', 'estoque_construcao')
        username = os.getenv('MYSQL_USER', 'estoque_user')
        password = os.getenv('MYSQL_PASSWORD', '')
        
        # Conectar sem especificar database
        temp_conn = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {database}")
        
        logger.info(f"Database {database} verificado/criado com sucesso")
        return True
        
    except Error as e:
        logger.error(f"Erro ao criar database: {e}")
        return False
    finally:
        if 'temp_conn' in locals() and temp_conn.is_connected():
            temp_conn.close()