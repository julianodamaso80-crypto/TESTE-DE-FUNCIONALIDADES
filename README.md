# SpriteTest

AI-Powered Testing Platform — autonomous test generation, execution, and reporting.

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Linux/Mac

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Copy environment file
cp .env.example .env

# 4. Install Node dependencies and build CSS
npm install
npm run build:css

# 5. Run migrations
python manage.py migrate

# 6. Start development server
python manage.py runserver
```

## Development

- **Watch CSS changes:** `npm run watch:css`
- **Build for production:** `npm run build:css:prod`
- **Django settings:** `config/settings/development.py`

## Project Structure

```
spritetest/
├── config/          # Django settings (base, development, production)
├── apps/
│   ├── core/        # Landing page, health check
│   └── accounts/    # Auth (future)
├── templates/       # Global templates
├── static/          # Static assets (Tailwind source + compiled CSS)
└── manage.py
```
