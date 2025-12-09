# 📌 Data Pipeline — MinIO, PostgreSQL e Metabase

## 📖 Visão Geral

Este projeto implementa uma pipeline de dados completa utilizando containers Docker.  
O fluxo consiste em:

1️⃣ **Fetcher** → Ingestão dos dados no MinIO (S3)  
2️⃣ **Processor** → Processa e insere os dados no PostgreSQL  
3️⃣ **Metabase** → Visualização dos dados para análise BI  

Toda a infraestrutura é containerizada via **Docker Compose**.

---

## 🛠️ Tecnologias Utilizadas

| Função | Tecnologia |
|--------|------------|
| Armazenamento de dados brutos | MinIO (S3) |
| Processamento ETL | Python |
| Banco de Dados | PostgreSQL |
| Visualização | Metabase |
| Orquestração | Docker Compose |

---

## 📂 Estrutura do Projeto

📦 Prova-bigdata
┗ 📁 Nova pasta
┣ 📁 fetcher
┃ ┣ fetcher.py
┃ ┣ Dockerfile
┃ ┗ requirements.txt
┣ 📁 processor
┃ ┣ processor.py
┃ ┣ Dockerfile
┃ ┗ requirements.txt
┣ 📁 dashboard <-- (não utilizado nesta entrega)
┣ docker-compose.yml
┗ README.md


🚫 O dashboard Flask não está em uso nesta versão.

---

## 🚀 Execução do Projeto

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/vieira-dih/Prova-bigdata.git

cd Prova-bigdata

Cd nova pasta

``` 

2️⃣ Subir os containers

**C om o Docker aberto **
```bash

docker compose up -d --build

```

Verifique se subiu corretamente:
```bash

docker ps

```

Você deve ver os serviços:

Serviço	Status

postgres  UP
minio	  UP
metabase  UP
fetcher	  UP
processor UP

🔌 Acesso aos Serviços

Serviço	URL	Credenciais
Metabase	http://localhost:3000
	Criar no 1º acesso

MinIO Console	http://localhost:9003
	minioadmin / minioadmin123

PostgreSQL	localhost:5432	metabase / metabase123

📍 Execução da Pipeline

 Ingestão — Fetcher
 ```bash
docker compose exec fetcher python fetcher.py

```
📌 Gera e envia arquivo CSV ao MinIO

🟩 Processamento — Processor
```bash

docker compose exec processor python processor.py

```

📌 Insere dados processados no PostgreSQL

📊 Configuração do Metabase

Acesse:
➡️ http://localhost:3000

Crie o usuário Admin e configure o banco em:

Settings → Databases → Add Database

Preencha:

Campo	Valor
Name	pipeline-db
Type	PostgreSQL
Host	postgres
Port	5432
Database Name	metabase_db
Username	metabase
Password	metabase123

Após salvar:

Browse data → Selecione a tabela → Monte dashboards

🧹 Encerrar a infraestrutura
```bash
docker compose down
```
🔧 Possíveis Problemas e Soluções
Problema/Solução
Processor não encontra arquivo	Execute o fetcher primeiro
Metabase sem tabelas	Admin → Databases → Sync Schema
MinIO não acessa	Verificar porta 9003 e credenciais
Falha ao ler CSV	Verificar bucket/arquivo no MinIO
📌 Repositório Oficial

🔗 https://github.com/vieira-dih/Prova-bigdata