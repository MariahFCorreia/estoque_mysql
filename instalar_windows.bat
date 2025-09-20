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
    echo.
    echo Baixe Python em: https://www.python.org/downloads/
    echo Instale Python e marque a opção "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: pip não está disponível!
    echo Reinstale Python marcando a opção "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/6] Criando ambiente virtual Python...
python -m venv venv

echo [2/6] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [3/6] Instalando dependências...
pip install -r requirements.txt

echo [4/6] Criando diretórios necessários...
if not exist backups mkdir backups
if not exist data mkdir data
if not exist logs mkdir logs
if not exist uploads mkdir uploads

echo [5/6] Configurando arquivo de ambiente...
if not exist .env (
    copy .env.example .env
    echo.
    echo ⚠️  Arquivo .env criado. Configure com suas informações:
    echo    - MYSQL_PASSWORD: Sua senha do MySQL
    echo    - SECRET_KEY: Altere para uma chave segura
    echo.
) else (
    echo ✅ Arquivo .env já existe
)

echo [6/6] Instalação concluída!
echo.
echo ========================================
echo  PRÓXIMOS PASSOS:
echo ========================================
echo.
echo 1. Configure o banco de dados MySQL:
echo    mysql -u root -p ^< create_mysql_user.sql
echo.
echo 2. Edite o arquivo .env com suas configurações
echo    notepad .env
echo.
echo 3. Execute o sistema:
echo    python app_mysql.py
echo.
echo 4. Acesse no navegador:
echo    http://localhost:5000
echo.
echo 5. Use as credenciais padrão:
echo    Usuário: admin
echo    Senha: admin123
echo.
echo ========================================
pause