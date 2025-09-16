import mysql.connector
from mysql.connector import Error
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def migrate_from_sqlite():
    """Migra dados do SQLite para MySQL"""
    
    # Configurações MySQL do .env
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'estoque_construcao'),
        'charset': 'utf8mb4'
    }
    
    try:
        # Conectar ao SQLite
        sqlite_conn = sqlite3.connect('estoque_construcao.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()
        
        # Conectar ao MySQL
        mysql_conn = mysql.connector.connect(**db_config)
        mysql_cur = mysql_conn.cursor(dictionary=True)
        
        print("🚀 Iniciando migração SQLite → MySQL...")
        
        # Migrar usuários
        print("📦 Migrando usuários...")
        sqlite_cur.execute('SELECT * FROM usuarios')
        for user in sqlite_cur.fetchall():
            mysql_cur.execute('''
                INSERT INTO usuarios (id, username, password_hash, role, nome, email, data_cadastro)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (user['id'], user['username'], user['password_hash'], user['role'], 
                  user['nome'], user['email'], user['data_cadastro']))
        
        # Migrar produtos
        print("📦 Migrando produtos...")
        sqlite_cur.execute('SELECT * FROM produtos')
        for product in sqlite_cur.fetchall():
            mysql_cur.execute('''
                INSERT INTO produtos (id, codigo, descricao, categoria, quantidade, preco_unitario, 
                                   fornecedor, estoque_minimo, data_validade, lote, data_cadastro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (product['id'], product['codigo'], product['descricao'], product['categoria'],
                  product['quantidade'], product['preco_unitario'], product['fornecedor'],
                  product['estoque_minimo'], product['data_validade'], product['lote'],
                  product['data_cadastro']))
        
        # Migrar movimentações
        print("📦 Migrando movimentações...")
        sqlite_cur.execute('SELECT * FROM movimentacoes')
        for movement in sqlite_cur.fetchall():
            mysql_cur.execute('''
                INSERT INTO movimentacoes (id, produto_id, tipo, quantidade, data, observacao, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (movement['id'], movement['produto_id'], movement['tipo'], movement['quantidade'],
                  movement['data'], movement['observacao'], movement['usuario_id']))
        
        mysql_conn.commit()
        print("✅ Migração concluída com sucesso!")
        
    except Error as e:
        print(f"❌ Erro MySQL: {e}")
        if 'mysql_conn' in locals():
            mysql_conn.rollback()
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'mysql_conn' in locals() and mysql_conn.is_connected():
            mysql_conn.close()

if __name__ == '__main__':
    migrate_from_sqlite()