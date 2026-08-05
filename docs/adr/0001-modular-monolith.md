# ADR 0001 — Monólito modular orientado a eventos

## Decisão

Iniciar a plataforma como um monólito modular em FastAPI, com PostgreSQL, Redis e padrão Transactional Outbox.

## Contexto

Os domínios são independentes, mas a operação inicial terá uma única pessoa, Docker local e pouca necessidade de deploys separados. Microserviços agora aumentariam custo operacional, superfície de falhas e tempo de desenvolvimento.

## Consequências

Os módulos não devem depender de detalhes de infraestrutura uns dos outros. Eventos de domínio são persistidos no outbox e podem ser consumidos por workers. Um módulo poderá ser extraído no futuro sem alterar o contrato de eventos.
