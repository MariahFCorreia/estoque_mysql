# licenca_config.py - Sistema completo de gerenciamento de licenças
import json
import hashlib
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class GerenciadorLicencas:
    def __init__(self):
        self.arquivo_licencas = 'data/licencas_registradas.json'
        self.arquivo_backup = 'backups/licencas_backup.json'
        self.carregar_licencas()
    
    def carregar_licencas(self):
        """Carrega as licenças do arquivo JSON"""
        try:
            # Criar diretório se não existir
            os.makedirs('data', exist_ok=True)
            os.makedirs('backups', exist_ok=True)
            
            if os.path.exists(self.arquivo_licencas):
                with open(self.arquivo_licencas, 'r', encoding='utf-8') as f:
                    self.licencas = json.load(f)
                print(f"✅ Licenças carregadas: {len(self.licencas)} registros")
            else:
                self.licencas = {}
                print("ℹ️ Nenhum arquivo de licenças encontrado. Criando novo.")
        except Exception as e:
            print(f"❌ Erro ao carregar licenças: {e}")
            self.licencas = {}
    
    def salvar_licencas(self):
        """Salva as licenças no arquivo JSON com backup"""
        try:
            # Fazer backup
            if os.path.exists(self.arquivo_licencas):
                import shutil
                shutil.copy2(self.arquivo_licencas, self.arquivo_backup)
            
            # Salvar licenças
            with open(self.arquivo_licencas, 'w', encoding='utf-8') as f:
                json.dump(self.licencas, f, ensure_ascii=False, indent=2)
            
            print("✅ Licenças salvas com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar licenças: {e}")
            return False
    
    def gerar_licenca(self, cliente, email, cnpj=None, dias_validade=365, tipo='standard', valor_pago=0):
        """Gera uma nova licença"""
        try:
            # Gerar chave única
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            chave_base = f"{cliente}{email}{timestamp}{os.urandom(8).hex()}"
            chave_licenca = hashlib.sha256(chave_base.encode()).hexdigest().upper()[:20]
            
            # Formatar para melhor visualização: XXXX-XXXX-XXXX-XXXX
            chave_formatada = '-'.join([chave_licenca[i:i+4] for i in range(0, 16, 4)])
            
            # Data de expiração
            data_expiracao = (datetime.now() + timedelta(days=dias_validade)).strftime('%Y-%m-%d')
            data_geracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Criar registro da licença
            self.licencas[chave_formatada] = {
                'cliente': cliente,
                'email': email,
                'cnpj': cnpj,
                'tipo': tipo,
                'valor_pago': valor_pago,
                'data_geracao': data_geracao,
                'data_expiracao': data_expiracao,
                'ativa': True,
                'ultima_verificacao': None,
                'ativacoes': 0,
                'ultima_ativacao': None
            }
            
            self.salvar_licencas()
            print(f"✅ Licença gerada para {cliente}: {chave_formatada}")
            return chave_formatada, data_expiracao
            
        except Exception as e:
            print(f"❌ Erro ao gerar licença: {e}")
            return None, None
    
    def verificar_licenca(self, chave_licenca):
        """Verifica se uma licença é válida"""
        try:
            # Limpar e formatar a chave
            chave_limpa = chave_licenca.replace('-', '').replace(' ', '').upper().strip()
            
            if len(chave_limpa) != 16:
                return False, "Formato de chave inválido"
            
            # Reformatar para o padrão
            chave_formatada = '-'.join([chave_limpa[i:i+4] for i in range(0, 16, 4)])
            
            if chave_formatada not in self.licencas:
                return False, "Licença não encontrada"
            
            licenca = self.licencas[chave_formatada]
            
            if not licenca['ativa']:
                return False, "Licença desativada"
            
            data_expiracao = datetime.strptime(licenca['data_expiracao'], '%Y-%m-%d')
            if datetime.now() > data_expiracao:
                return False, f"Licença expirada em {licenca['data_expiracao']}"
            
            # Atualizar última verificação
            licenca['ultima_verificacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            licenca['ativacoes'] = licenca.get('ativacoes', 0) + 1
            licenca['ultima_ativacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.salvar_licencas()
            
            return True, f"Licença válida até {licenca['data_expiracao']}"
            
        except Exception as e:
            return False, f"Erro na verificação: {str(e)}"
    
    def listar_licencas(self):
        """Lista todas as licenças"""
        return self.licencas
    
    def desativar_licenca(self, chave_licenca):
        """Desativa uma licença"""
        try:
            chave_limpa = chave_licenca.replace('-', '').replace(' ', '').upper().strip()
            chave_formatada = '-'.join([chave_limpa[i:i+4] for i in range(0, 16, 4)])
            
            if chave_formatada in self.licencas:
                self.licencas[chave_formatada]['ativa'] = False
                self.salvar_licencas()
                print(f"✅ Licença {chave_formatada} desativada")
                return True
            return False
        except Exception as e:
            print(f"❌ Erro ao desativar licença: {e}")
            return False
    
    def estatisticas(self):
        """Retorna estatísticas das licenças"""
        total = len(self.licencas)
        ativas = sum(1 for l in self.licencas.values() if l['ativa'])
        expiradas = sum(1 for l in self.licencas.values() if datetime.strptime(l['data_expiracao'], '%Y-%m-%d') < datetime.now())
        
        return {
            'total': total,
            'ativas': ativas,
            'inativas': total - ativas,
            'expiradas': expiradas,
            'faturamento_total': sum(l.get('valor_pago', 0) for l in self.licencas.values())
        }

# Instância global do gerenciador
gerenciador_licencas = GerenciadorLicencas()