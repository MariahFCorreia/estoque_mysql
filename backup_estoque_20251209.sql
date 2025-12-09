-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: estoque_construcao
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `licencas_ativas`
--

DROP TABLE IF EXISTS `licencas_ativas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `licencas_ativas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chave_licenca` varchar(100) NOT NULL,
  `data_ativacao` datetime NOT NULL,
  `usuario_id` int DEFAULT NULL,
  `ip_ativacao` varchar(45) DEFAULT NULL,
  `dispositivo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_licenca` (`chave_licenca`),
  KEY `usuario_id` (`usuario_id`),
  KEY `idx_chave_licenca` (`chave_licenca`),
  KEY `idx_data_ativacao` (`data_ativacao`),
  CONSTRAINT `licencas_ativas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `licencas_ativas`
--

LOCK TABLES `licencas_ativas` WRITE;
/*!40000 ALTER TABLE `licencas_ativas` DISABLE KEYS */;
INSERT INTO `licencas_ativas` VALUES (1,'DEMO-0000-0000-0000-0000','2025-10-03 17:01:31',1,'127.0.0.1','Sistema Demo');
/*!40000 ALTER TABLE `licencas_ativas` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_licenca_ativa_insert` AFTER INSERT ON `licencas_ativas` FOR EACH ROW BEGIN
    INSERT INTO licencas_historico (chave_licenca, acao, data_hora, usuario_id, ip, detalhes)
    VALUES (NEW.chave_licenca, 'ativacao', NEW.data_ativacao, NEW.usuario_id, NEW.ip_ativacao, 
            CONCAT('Dispositivo: ', NEW.dispositivo));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `licencas_historico`
--

DROP TABLE IF EXISTS `licencas_historico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `licencas_historico` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chave_licenca` varchar(100) NOT NULL,
  `acao` varchar(50) NOT NULL COMMENT 'ativacao, verificacao, renovacao, etc',
  `data_hora` datetime NOT NULL,
  `usuario_id` int DEFAULT NULL,
  `ip` varchar(45) DEFAULT NULL,
  `detalhes` text,
  PRIMARY KEY (`id`),
  KEY `idx_chave_acao` (`chave_licenca`,`acao`),
  KEY `idx_data_hora` (`data_hora`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `licencas_historico_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `licencas_historico`
--

LOCK TABLES `licencas_historico` WRITE;
/*!40000 ALTER TABLE `licencas_historico` DISABLE KEYS */;
/*!40000 ALTER TABLE `licencas_historico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimentacoes`
--

DROP TABLE IF EXISTS `movimentacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimentacoes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `produto_id` int NOT NULL,
  `tipo` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantidade` int NOT NULL,
  `data` datetime NOT NULL,
  `observacao` text COLLATE utf8mb4_unicode_ci,
  `usuario_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `idx_data` (`data`),
  KEY `idx_produto` (`produto_id`),
  CONSTRAINT `movimentacoes_ibfk_1` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `movimentacoes_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimentacoes`
--

LOCK TABLES `movimentacoes` WRITE;
/*!40000 ALTER TABLE `movimentacoes` DISABLE KEYS */;
INSERT INTO `movimentacoes` VALUES (1,6,'ENTRADA',3,'2025-10-03 20:25:25','Cadastro inicial',1),(2,7,'ENTRADA',3,'2025-10-03 20:26:28','Cadastro inicial',1),(3,2,'SAIDA',15,'2025-10-04 14:57:43','',1),(4,3,'SAIDA',1,'2025-10-31 23:40:35','Venda #V20251031234034 - Consumidor Final',2),(5,5,'SAIDA',1,'2025-11-02 21:31:38','Venda #V20251102213137 - Consumidor Final',2),(6,2,'SAIDA',3,'2025-12-05 16:34:25','Venda #V20251205163424 - Consumidor Final',2);
/*!40000 ALTER TABLE `movimentacoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nfe_configuracoes`
--

DROP TABLE IF EXISTS `nfe_configuracoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nfe_configuracoes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa_id` int NOT NULL,
  `certificado_digital` longblob,
  `senha_certificado` varchar(255) DEFAULT NULL,
  `ambiente` varchar(20) DEFAULT 'homologacao',
  `token_api` varchar(255) DEFAULT NULL,
  `sequencia_numeracao` int DEFAULT '1',
  `serie_nfe` varchar(3) DEFAULT '1',
  `data_atualizacao` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nfe_configuracoes`
--

LOCK TABLES `nfe_configuracoes` WRITE;
/*!40000 ALTER TABLE `nfe_configuracoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `nfe_configuracoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nfe_referencias`
--

DROP TABLE IF EXISTS `nfe_referencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nfe_referencias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `venda_id` int NOT NULL,
  `referencia_focus` varchar(255) NOT NULL,
  `status` varchar(50) NOT NULL,
  `chave_acesso` varchar(50) DEFAULT NULL,
  `numero_nfe` varchar(50) DEFAULT NULL,
  `serie_nfe` varchar(10) DEFAULT NULL,
  `data_criacao` datetime NOT NULL,
  `data_autorizacao` datetime DEFAULT NULL,
  `xml_content` longtext,
  `pdf_content` longblob,
  `erro_mensagem` text,
  PRIMARY KEY (`id`),
  KEY `idx_referencia` (`referencia_focus`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nfe_referencias`
--

LOCK TABLES `nfe_referencias` WRITE;
/*!40000 ALTER TABLE `nfe_referencias` DISABLE KEYS */;
/*!40000 ALTER TABLE `nfe_referencias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produtos`
--

DROP TABLE IF EXISTS `produtos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produtos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` int NOT NULL,
  `descricao` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `categoria` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantidade` int NOT NULL,
  `preco_unitario` decimal(10,2) NOT NULL,
  `fornecedor` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estoque_minimo` int NOT NULL,
  `data_validade` date DEFAULT NULL,
  `lote` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_cadastro` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `idx_codigo` (`codigo`),
  KEY `idx_categoria` (`categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produtos`
--

LOCK TABLES `produtos` WRITE;
/*!40000 ALTER TABLE `produtos` DISABLE KEYS */;
INSERT INTO `produtos` VALUES (1,1001,'Cimento CP II 50kg','CIMENTO',500,28.90,'Votorantim',100,'2024-12-31','LOTE001','2025-09-09 21:39:25'),(2,1002,'Areia Média m³','AGREGADOS',182,85.00,'Pedreira São José',50,NULL,NULL,'2025-09-09 21:39:25'),(3,1003,'Tijolo Baiano 1000un','CERÂMICOS',149,450.00,'Cerâmica Santa Rita',30,NULL,NULL,'2025-09-09 21:39:25'),(4,1004,'Vergalhão CA-50 6mm','FERRO_E_ACO',80,25.00,'Gerdau',20,NULL,NULL,'2025-09-09 21:39:25'),(5,1005,'Tinta Acrílica Branco Gelo 18L','TINTAS',39,189.90,'Suvinil',10,'2025-06-30','LOTE005','2025-09-09 21:39:25'),(6,202,'Tinta interna branco gelo (GAL-3L)','TINTAS',3,21.44,'Gmix',2,NULL,NULL,'2025-10-03 20:25:25'),(7,251,'Tinta interna branco neve (GAL-3L)','TINTAS',3,21.44,'Gmix',2,NULL,NULL,'2025-10-03 20:26:28');
/*!40000 ALTER TABLE `produtos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recuperacao_senha`
--

DROP TABLE IF EXISTS `recuperacao_senha`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recuperacao_senha` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `token` varchar(100) NOT NULL,
  `data_criacao` datetime NOT NULL,
  `data_expiracao` datetime NOT NULL,
  `utilizado` tinyint(1) DEFAULT '0',
  `ip_solicitacao` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `idx_token` (`token`),
  KEY `idx_expiracao` (`data_expiracao`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `recuperacao_senha_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recuperacao_senha`
--

LOCK TABLES `recuperacao_senha` WRITE;
/*!40000 ALTER TABLE `recuperacao_senha` DISABLE KEYS */;
/*!40000 ALTER TABLE `recuperacao_senha` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user',
  `nome` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_cadastro` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `idx_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin','pbkdf2:sha256:600000$aeWH3HOlEYnypdBN$8f27ec0488070a4ad4309346015e73db74ea93ca3ef6c4c3efdd32f5f7717544','admin','Administrador','admin@empresa.com','2025-09-09 21:39:25'),(2,'vendedor','pbkdf2:sha256:600000$teMpONeP3PAdEPGV$62c5ff3ebab342bd3b93490c506642416818b81d7bb0f9db90f63c27c8251a0e','vendedor','Vendedor Teste','vendedor@empresa.com','2025-10-31 23:28:29'),(3,'ti_system','pbkdf2:sha256:600000$fxjq1OJZs16JskxY$00557752d7398bc68640bd4f3ade754a19ad4ed356bbc3fbcda6290fed14e318','ti_system','Suporte Técnico','ti@empresa.com','2025-12-06 21:27:27');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venda_itens`
--

DROP TABLE IF EXISTS `venda_itens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venda_itens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `venda_id` int NOT NULL,
  `produto_id` int NOT NULL,
  `quantidade` int NOT NULL,
  `preco_unitario` decimal(10,2) NOT NULL,
  `valor_total` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `produto_id` (`produto_id`),
  KEY `idx_venda` (`venda_id`),
  CONSTRAINT `venda_itens_ibfk_1` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `venda_itens_ibfk_2` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venda_itens`
--

LOCK TABLES `venda_itens` WRITE;
/*!40000 ALTER TABLE `venda_itens` DISABLE KEYS */;
INSERT INTO `venda_itens` VALUES (1,1,3,1,450.00,450.00),(2,2,5,1,189.90,189.90),(3,3,2,3,85.00,255.00);
/*!40000 ALTER TABLE `venda_itens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendas`
--

DROP TABLE IF EXISTS `vendas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_nome` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `vendedor_id` int NOT NULL,
  `data_venda` datetime NOT NULL,
  `valor_total` decimal(10,2) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'finalizada',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `idx_data_venda` (`data_venda`),
  KEY `idx_vendedor` (`vendedor_id`),
  CONSTRAINT `vendas_ibfk_1` FOREIGN KEY (`vendedor_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendas`
--

LOCK TABLES `vendas` WRITE;
/*!40000 ALTER TABLE `vendas` DISABLE KEYS */;
INSERT INTO `vendas` VALUES (1,'V20251031234034','Consumidor Final',2,'2025-10-31 23:40:34',450.00,'finalizada'),(2,'V20251102213137','Consumidor Final',2,'2025-11-02 21:31:37',189.90,'finalizada'),(3,'V20251205163424','Consumidor Final',2,'2025-12-05 16:34:25',255.00,'finalizada');
/*!40000 ALTER TABLE `vendas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-09 14:37:58
