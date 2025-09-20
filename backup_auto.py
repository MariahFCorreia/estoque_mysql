# backup_auto.py - Sistema de backup automático
import os
import shutil
from datetime import datetime
import schedule
import time
from dotenv import load_dotenv

load_dotenv()

class BackupManager:
    def __init__(self):
        self.backup_dir = "backups"
        self.data_dir = "data"
        self.log_file = "logs/backup.log"
        self.retention_days = 30
        
        # Criar diretórios se não existirem
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def log(self, message):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
        
        print(log_message.strip())
    
    def backup_database(self):
        """Faz backup do banco de dados MySQL"""
        try:
            from database_mysql import execute_query
            import mysql.connector
            
            # Configurações do banco
            host = os.getenv('MYSQL_HOST', 'localhost')
            port = int(os.getenv('MYSQL_PORT', 3306))
            database = os.getenv('MYSQL_DATABASE', 'estoque_construcao')
            user = os.getenv('MYSQL_USER', 'estoque_user')
            password = os.getenv('MYSQL_PASSWORD', '')
            
            # Nome do arquivo de backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_dir}/backup_{database}_{timestamp}.sql"
            
            # Comando mysqldump
            cmd = f"mysqldump -h {host} -P {port} -u {user} -p{password} {database} > {backup_file}"
            
            # Executar backup
            os.system(cmd)
            
            # Verificar se o backup foi criado
            if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                self.log(f"✅ Backup do banco realizado: {backup_file}")
                return True
            else:
                self.log("❌ Falha no backup do banco")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro no backup do banco: {str(e)}")
            return False
    
    def backup_data(self):
        """Faz backup dos arquivos de dados"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_dir}/data_backup_{timestamp}.zip"
            
            # Criar zip dos dados
            shutil.make_archive(backup_file.replace('.zip', ''), 'zip', self.data_dir)
            
            self.log(f"✅ Backup de dados realizado: {backup_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no backup de dados: {str(e)}")
            return False
    
    def cleanup_old_backups(self):
        """Remove backups antigos"""
        try:
            for file in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, file)
                if os.path.isfile(file_path):
                    # Verificar se o arquivo é mais antigo que retention_days
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if (datetime.now() - file_time).days > self.retention_days:
                        os.remove(file_path)
                        self.log(f"🗑️ Backup removido: {file}")
            
            self.log("✅ Limpeza de backups concluída")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro na limpeza de backups: {str(e)}")
            return False
    
    def full_backup(self):
        """Executa backup completo"""
        self.log("=" * 50)
        self.log("🚀 INICIANDO BACKUP COMPLETO")
        self.log("=" * 50)
        
        success_db = self.backup_database()
        success_data = self.backup_data()
        success_cleanup = self.cleanup_old_backups()
        
        if success_db and success_data:
            self.log("✅ BACKUP COMPLETO CONCLUÍDO COM SUCESSO")
        else:
            self.log("❌ BACKUP COMPLETO COM FALHAS")
        
        self.log("=" * 50)
        return success_db and success_data
    
    def run_scheduled_backups(self):
        """Executa backups agendados"""
        # Backup diário às 2h da manhã
        schedule.every().day.at("02:00").do(self.full_backup)
        
        # Backup incremental a cada 6 horas
        schedule.every(6).hours.do(self.backup_data)
        
        self.log("📅 Agendador de backups iniciado")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

# Função principal
if __name__ == "__main__":
    backup_manager = BackupManager()
    
    # Se executado com argumento "now", faz backup imediato
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "now":
        backup_manager.full_backup()
    else:
        # Modo agendamento
        backup_manager.run_scheduled_backups()