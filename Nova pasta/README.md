README — Data Pipeline com MinIO, PostgreSQL e Metabase
📖 Visão Geral

Este projeto implementa uma pipeline de dados completa utilizando Docker.
O fluxo consiste em:

1️⃣ Fetcher → Faz ingestão dos dados e os armazena no MinIO (S3)
2️⃣ Processor → Processa os dados ingeridos e insere no PostgreSQL
3️⃣ Metabase → Camada de visualização e BI

Toda a infraestrutura é containerizada via Docker Compose, facilitando deploy e execução.

🛠️ Tecnologias Utilizadas
Função	Tecnologia
Armazenamento de dados brutos	MinIO (S3)
Processamento de dados	Python
Banco de Dados	PostgreSQL
Visualização de dados	Metabase
Orquestração	Docker Compose
📂 Estrutura do Projeto
📦 Prova-bigdata
 ┣ 📁 fetcher
 ┃ ┣ fetcher.py
 ┃ ┣ Dockerfile
 ┃ ┗ requirements.txt
 ┣ 📁 processor
 ┃ ┣ processor.py
 ┃ ┣ Dockerfile
 ┃ ┗ requirements.txt
 ┣ 📁 dashboard  <-- (não utilizado nesta versão)
 ┣ docker-compose.yml
 ┗ README.md

🚀 Execução do Projeto
1️⃣ Clonar o repositório
git clone https://github.com/vieira-dih/Prova-bigdata.git
cd Prova-bigdata

2️⃣ Subir toda a infraestrutura
docker compose up -d --build


Verifique se tudo está rodando:

docker ps


Você deve ver:

Serviço	Status
postgres	UP
minio	UP
metabase	UP
fetcher	UP
processor	UP
🔌 URLs e credenciais dos serviços
Serviço	URL	Credenciais
Metabase	http://localhost:3000
	Criadas ao acessar a 1ª vez
MinIO Console	http://localhost:9003
	minioadmin / minioadmin123
PostgreSQL	localhost:5432	metabase / metabase123
📍 Execução da Pipeline
🟦 1️⃣ Ingestão — Fetcher
docker compose exec fetcher python fetcher.py


📌 Resultado: Arquivo CSV gerado e armazenado no MinIO

🟩 2️⃣ Processamento — Processor
docker compose exec processor python processor.py


📌 Resultado: Dados transformados e inseridos no PostgreSQL

📊 Visualização — Metabase

Acesse:

🔗 http://localhost:3000

Realize a criação do usuário ADM. Depois:

➡️ Settings → Databases → Add Database

Preencha assim:

Campo	Valor
Name	pipeline-db
Type	PostgreSQL
Host	postgres
Port	5432
Database Name	metabase_db
Username	metabase
Password	metabase123

🟢 Após salvar:
→ Vá em Browse data → Selecione a tabela → Crie gráficos e dashboards

🧹 Encerrar serviços
docker compose down

🔧 Possíveis Problemas e Soluções
Problema	Solução
Processo acusa arquivo ausente	Verifique se o fetcher foi executado antes
Tabelas não aparecem no Metabase	Admin → Databases → Sync database schema
Falha ao conectar no MinIO	Confirme porta 9003 e credenciais corretas
Processor falha ao ler CSV	Verificar se o bucket/arquivo existe no MinIO
📌 Repositório Oficial

👉 https://github.com/vieira-dih/Prova-bigdata