-- Script para criar usuário e database automaticamente
-- Execute como root: mysql -u root -p < create_mysql_user.sql

-- Criar database
CREATE DATABASE IF NOT EXISTS estoque_construcao 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Criar usuário
CREATE USER IF NOT EXISTS 'estoque_user'@'localhost' IDENTIFIED BY 'sua_senha_segura_aqui';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON estoque_construcao.* TO 'estoque_user'@'localhost';

-- Privilégios para procedures e functions (opcional)
GRANT EXECUTE ON estoque_construcao.* TO 'estoque_user'@'localhost';

-- Atualizar privilégios
FLUSH PRIVILEGES;

-- Mostrar resultado
SELECT 'Database e usuário criados com sucesso!' as Status;