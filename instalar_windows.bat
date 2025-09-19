@echo off
chcp 65001 > nul
echo ========================================
echo  INSTALADOR SISTEMA CONTROLE DE ESTOQUE
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não está instalado!
    echo Baixe em: https://www.python.org/downloads/
    echo Instale Python e execute este script novamente.
    pause
    exit /b 1
)

echo [1/4] Criando ambiente virtual Python...
python -m venv venv

echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [3/4] Instalando dependências...
pip install -r requirements.txt

echo [4/4] Configuração concluída!
echo.
echo ⚠️  ATENÇÃO: IMPORTANTE!
echo 1. Configure o arquivo .env com a senha do MySQL
echo 2. Execute o script SQL: mysql -u root -p < create_mysql_user.sql
echo 3. Execute o sistema: python app_mysql.py
echo.
echo 📋 O arquivo .env deve conter:
echo MYSQL_PASSWORD=sua_senha_do_mysql_aqui
echo.
pause