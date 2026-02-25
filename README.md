# SpriteTest — AI Testing Platform

SaaS de testes automatizados com IA. Similar ao TestSprite.com, com diferenciais:
- Execução local (mock) + execução real (Playwright)
- Relatórios compartilháveis por link público
- API REST para integração CI/CD
- Self-hostable via Docker

## Stack
- Backend: Django 5.0.6 + Celery + Redis
- Frontend: Tailwind CSS v3 (dark theme navy/yellow)
- AI: Claude API (Anthropic)
- Testing: Playwright (Chromium)
- Deploy: Railway + GitHub Actions

## Desenvolvimento local

```bash
cd spritetest
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
cp .env.example .env       # preencher ANTHROPIC_API_KEY
python manage.py migrate
npm run build:css
python manage.py runserver 8000
```

## Variáveis de ambiente
Ver .env.example para lista completa.

## Deploy Railway
1. Conectar repositório GitHub no Railway
2. Adicionar PostgreSQL e Redis via Railway dashboard
3. Configurar variáveis: DJANGO_SECRET_KEY, DJANGO_SETTINGS_MODULE, ALLOWED_HOSTS, ANTHROPIC_API_KEY
