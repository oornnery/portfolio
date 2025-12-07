"""
JinjaX Catalog configuration for component-based templating.

Why: Centraliza a configuração do sistema de componentes JinjaX,
     permitindo templates modulares e reutilizáveis.

How: Usa jx.Catalog para gerenciar componentes em app/components/,
     com auto_reload baseado no ambiente de desenvolvimento.
"""

from pathlib import Path

from jx import Catalog

from app.config import settings


def create_catalog() -> Catalog:
    """
    Create and configure the JinjaX catalog.

    Returns:
        Configured Catalog instance with components folder registered.
    """
    components_path = Path(__file__).parent / "components"

    catalog = Catalog(
        folder=components_path,
        auto_reload=settings.is_development,
    )

    # Add globals for access in templates
    catalog.jinja_env.globals["settings"] = settings
    catalog.jinja_env.globals["env"] = settings.ENV
    catalog.jinja_env.globals["is_production"] = settings.is_production
    catalog.jinja_env.globals["is_development"] = settings.is_development

    return catalog


# Singleton catalog instance
catalog = create_catalog()
