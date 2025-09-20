-- licenca_tables.sql
-- Execute este arquivo após criar o banco de dados

USE estoque_construcao;

-- Tabela de licenças ativas
CREATE TABLE IF NOT EXISTS licencas_ativas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chave_licenca VARCHAR(100) UNIQUE NOT NULL,
    data_ativacao DATETIME NOT NULL,
    usuario_id INT NULL,
    ip_ativacao VARCHAR(45),
    dispositivo VARCHAR(255),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    INDEX idx_chave_licenca (chave_licenca),
    INDEX idx_data_ativacao (data_ativacao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabela de histórico de licenças
CREATE TABLE IF NOT EXISTS licencas_historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chave_licenca VARCHAR(100) NOT NULL,
    acao VARCHAR(50) NOT NULL COMMENT 'ativacao, verificacao, renovacao, etc',
    data_hora DATETIME NOT NULL,
    usuario_id INT NULL,
    ip VARCHAR(45),
    detalhes TEXT,
    INDEX idx_chave_acao (chave_licenca, acao),
    INDEX idx_data_hora (data_hora),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Inserir licença de demonstração (opcional)
INSERT IGNORE INTO licencas_ativas (chave_licenca, data_ativacao, usuario_id, ip_ativacao, dispositivo)
VALUES (
    'DEMO-0000-0000-0000-0000', 
    NOW(), 
    (SELECT id FROM usuarios WHERE username = 'admin' LIMIT 1),
    '127.0.0.1',
    'Sistema Demo'
);

-- Trigger para registrar ativações automaticamente
DELIMITER //
CREATE TRIGGER after_licenca_ativa_insert
AFTER INSERT ON licencas_ativas
FOR EACH ROW
BEGIN
    INSERT INTO licencas_historico (chave_licenca, acao, data_hora, usuario_id, ip, detalhes)
    VALUES (NEW.chave_licenca, 'ativacao', NEW.data_ativacao, NEW.usuario_id, NEW.ip_ativacao, 
            CONCAT('Dispositivo: ', NEW.dispositivo));
END//
DELIMITER ;

SELECT '✅ Tabelas de licença criadas com sucesso!' as Status;