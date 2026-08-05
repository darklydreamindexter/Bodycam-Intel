# Bodycam Intelligence Platform

Plataforma local para descoberta, consolidação, priorização e acompanhamento de casos públicos dos Estados Unidos. A criação e o envio de pedidos de registros são separados: pedidos começam sempre como rascunho e exigem aprovação humana antes do envio.

## Início rápido

Pré-requisito: Docker Desktop com Docker Compose habilitado.

1. Copie `.env.example` para `.env` e ajuste as credenciais locais se desejar.
2. Execute `docker compose up --build`.
3. Abra o dashboard em `http://localhost:3000` e a documentação da API em `http://localhost:8000/docs`.

O primeiro levantamento de dados pode ser feito pela API Swagger. O endpoint `POST /api/v1/bootstrap/demo` cria exemplos locais, explicitamente identificados como demonstração, para explorar o dashboard.

## Serviços locais

- Dashboard: `http://localhost:3000`
- API e Swagger: `http://localhost:8000/docs`
- MinIO Console: `http://localhost:9001`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Descoberta automática de fontes

Na aba **Fontes**, cadastre apenas feeds RSS/Atom de veículos e órgãos públicos que você deseja acompanhar. A plataforma registra cada item coletado, preserva a URL e os metadados, e cria casos candidatos somente quando encontrar palavras-chave relevantes. Cada fonte possui seu próprio intervalo (mínimo: 15 minutos); o processo `scheduler` coloca as coletas na fila e o processo `worker` as executa.

Esta fase não cria nem envia pedidos FOIA. Ela constrói uma fila de casos verificáveis, sempre com a evidência de origem. Um caso sem estado identificável é marcado temporariamente como `US`, até a consolidação humana ou uma futura etapa de enriquecimento.

## Estado atual

Esta primeira versão estabelece a fundação: casos, agências, scorecards explicáveis, pedidos em rascunho, auditoria, outbox de eventos e dashboard de navegação. Coletores de fontes, enriquecimento por IA, integração de portais e produção editorial serão adicionados incrementalmente sobre estes contratos.

## Princípios operacionais

- Somente dados e fontes públicas são processados.
- Evidências e decisões devem ser rastreáveis.
- A IA sugere conteúdo; revisão humana decide.
- Pedidos de registros não são enviados automaticamente.
