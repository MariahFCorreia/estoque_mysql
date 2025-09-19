@echo off
chcp 65001 > nul
echo ========================================
echo  BACKUP DO BANCO DE DADOS - CONTROLE ESTOQUE
echo ========================================
echo.

:: Verificar se o diretório de backups existe
if not exist backups mkdir backups

:: Obter timestamp para o nome do arquivo
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

:: Nome do arquivo de backup
set backup_file=backup_estoque_%timestamp%.sql

echo [1/3] Lendo configurações do banco de dados...
for /f "tokens=1,2 delims==" %%a in ('.env') do (
    if "%%a"=="MYSQL_DATABASE" set database=%%b
    if "%%a"=="MYSQL_USER" set user=%%b
    if "%%a"=="MYSQL_PASSWORD" set password=%%b
)

echo [2/3] Executando backup do banco %database%...
mysqldump -u %user% -p%password% %database% > backups\%backup_file%

if %errorlevel% neq 0 (
    echo ERRO: Falha ao executar backup!
    echo Verifique as credenciais no arquivo .env
    pause
    exit /b 1
)

echo [3/3] Backup concluído: backups\%backup_file%
echo.
echo Tamanho do arquivo: 
for %%I in ("backups\%backup_file%") do echo %%~zI bytes
echo.
echo Backup realizado com sucesso!
pause