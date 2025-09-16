import os
import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Estabelece conexão com MySQL baseado na DATABASE_URL
    """
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('mysql://'):
        try:
            result = urlparse(database_url)
            
            # Extrair credenciais da URL
            username = result.username
            password = result.password
            hostname = result.hostname
            port = result.port or 3306
            database = result.path[1:]  # Remove a barra inicial
            
            connection = mysql.connector.connect(
                host=hostname,
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
    else:
        logger.error("DATABASE_URL não configurada ou não é MySQL")
        raise ValueError("URL de banco de dados MySQL não configurada")

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
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return False
    
    result = urlparse(database_url)
    db_name = result.path[1:]
    
    try:
        # Conectar sem especificar database
        temp_conn = mysql.connector.connect(
            host=result.hostname,
            port=result.port or 3306,
            user=result.username,
            password=result.password,
            charset='utf8mb4'
        )
        
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {db_name}")
        
        logger.info(f"Database {db_name} verificado/criado com sucesso")
        return True
        
    except Error as e:
        logger.error(f"Erro ao criar database: {e}")
        return False
    finally:
        if 'temp_conn' in locals() and temp_conn.is_connected():
            temp_conn.close()