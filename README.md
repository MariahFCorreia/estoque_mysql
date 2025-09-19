# Sistema de Controle de Estoque para Construção Civil

Sistema completo para gerenciamento de estoque de materiais de construção, desenvolvido em Python Flask com MySQL.

## 🚀 Funcionalidades

- ✅ Controle completo de produtos e categorias
- ✅ Gestão de entradas e saídas de estoque
- ✅ Alertas de estoque mínimo
- ✅ Relatórios e dashboard em tempo real
- ✅ Sistema multi-usuário com perfis diferentes
- ✅ Interface responsiva com Bootstrap 5
- ✅ Segurança robusta com hash de senhas

## 📋 Requisitos do Sistema

- Python 3.8 ou superior
- MySQL Server 5.7 ou superior
- Windows 10/11 ou Linux

## 🛠️ Instalação no Windows

### 1. Instalar Python
Baixe e instale Python em: https://www.python.org/downloads/

### 2. Instalar MySQL
Baixe o MySQL Installer: https://dev.mysql.com/downloads/installer/

### 3. Configurar o Sistema
```cmd
# Execute o instalador automático
instalar_windows.bat

# Configure o banco de dados (como administrador MySQL)
mysql -u root -p < create_mysql_user.sql

# Configure as variáveis de ambiente
copy .env.example .env
# Edite o arquivo .env com suas configurações