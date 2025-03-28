CREATE TABLE `users` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` text UNIQUE NOT NULL,
  `password` text NOT NULL,
  `is_admin` boolean DEFAULT false,
  `is_active` boolean DEFAULT true
);

CREATE TABLE `clientes` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `numero_contato` varchar(20),
  `sequencia` varchar(20),
  `cadastramento` date,
  `atualizacao` date,
  `razao_social` varchar(100) NOT NULL,
  `nome_fantasia` varchar(100),
  `contato_principal` varchar(100),
  `email` varchar(100),
  `telefone` varchar(20),
  `tipo` varchar(30),
  `cnpj` varchar(18),
  `ie` varchar(20),
  `im` varchar(20),
  `revenda` varchar(100),
  `vendedor` varchar(100),
  `tipo_servico` varchar(50),
  `localidade` varchar(50),
  `regiao` varchar(50),
  `atividade` varchar(50),
  `cep` varchar(10),
  `endereco` varchar(200),
  `complemento` varchar(100),
  `bairro` varchar(100),
  `cidade` varchar(100),
  `estado` varchar(2),
  `cobranca_cep` varchar(10),
  `cobranca_endereco` varchar(200),
  `cobranca_complemento` varchar(100),
  `cobranca_bairro` varchar(100),
  `cobranca_cidade` varchar(100),
  `cobranca_estado` varchar(2),
  `cobranca_tipo` varchar(50),
  `cliente_revenda` boolean DEFAULT false,
  `fator_juros` numeric(5,2),
  `estado_atual` varchar(30),
  `data_estado` date,
  `plano_nome` varchar(100),
  `dia_vencimento` integer,
  `motivo_estado` varchar(200)
);

CREATE TABLE `contratos` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `numero` varchar(50) UNIQUE NOT NULL,
  `cadastramento` date,
  `atualizacao` date,
  `tipo` varchar(50),
  `id_matriz_portal` varchar(50),
  `responsavel` varchar(100),
  `razao_social` varchar(100),
  `nome_fantasia` varchar(100),
  `contato` varchar(100),
  `email` varchar(100),
  `telefone` varchar(20),
  `cep` varchar(10),
  `endereco` varchar(200),
  `complemento` varchar(100),
  `bairro` varchar(100),
  `cidade` varchar(100),
  `estado` varchar(2),
  `cobranca_cep` varchar(10),
  `cobranca_endereco` varchar(200),
  `cobranca_complemento` varchar(100),
  `cobranca_bairro` varchar(100),
  `cobranca_cidade` varchar(100),
  `cobranca_estado` varchar(2),
  `dia_vencimento` integer,
  `fator_juros` numeric(5,2),
  `contrato_revenda` boolean DEFAULT false,
  `faturamento_contrato` boolean DEFAULT false,
  `estado_contrato` varchar(30),
  `data_estado` date,
  `motivo_estado` varchar(200),
  `cliente_id` integer
);

CREATE TABLE `instalacoes` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `numero_serie` varchar(50),
  `data_cadastramento` date,
  `data_instalacao` date,
  `data_retirada` date,
  `data_substituicao` date,
  `plano_nome` varchar(100),
  `estado_atual` varchar(30),
  `cliente_id` integer
);

CREATE TABLE `planos_contrato` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(100),
  `valor_plano` numeric(10,2),
  `valor_contrato` numeric(10,2),
  `contrato_id` integer
);

CREATE TABLE `produtos` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `codigo` varchar(50) UNIQUE,
  `nome` varchar(100) NOT NULL,
  `descricao` text,
  `preco_base` numeric(10,2)
);

CREATE TABLE `grupos` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` text
);

CREATE TABLE `contrato_produto` (
  `contrato_id` integer,
  `produto_id` integer,
  `quantidade` integer DEFAULT 1,
  `valor_unitario` numeric(10,2),
  `primary` key(contrato_id,produto_id)
);

CREATE TABLE `produto_grupo` (
  `produto_id` integer,
  `grupo_id` integer,
  `data_associacao` timestamp DEFAULT (now()),
  `primary` key(produto_id,grupo_id)
);

CREATE TABLE `regras_faturamento` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` text,
  `tipo` varchar(50),
  `valor` numeric(10,2),
  `ativa` boolean DEFAULT true,
  `contrato_id` integer,
  `grupo_id` integer
);

ALTER TABLE `contratos` ADD FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`);

ALTER TABLE `instalacoes` ADD FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`);

ALTER TABLE `planos_contrato` ADD FOREIGN KEY (`contrato_id`) REFERENCES `contratos` (`id`);

ALTER TABLE `contrato_produto` ADD FOREIGN KEY (`contrato_id`) REFERENCES `contratos` (`id`);

ALTER TABLE `contrato_produto` ADD FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`);

ALTER TABLE `produto_grupo` ADD FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`);

ALTER TABLE `produto_grupo` ADD FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`);

ALTER TABLE `regras_faturamento` ADD FOREIGN KEY (`contrato_id`) REFERENCES `contratos` (`id`);

ALTER TABLE `regras_faturamento` ADD FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`);
