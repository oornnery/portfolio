from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import TYPE_CHECKING, cast


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Portfolio"
    app_description: str = "My personal portfolio website"
    debug: bool = False
    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"

    # Site
    site_name: str = "Your Name"
    base_url: AnyHttpUrl = cast(AnyHttpUrl, "http://localhost:8000")
    default_og_image: str = "/static/images/og-default.png"

    # Custom profile data
    author_name: str = "Fabio Souza"
    author_email: str = "contato@fabiohcsouza.com"
    social_links: dict[str, AnyHttpUrl] = Field(
        default_factory=lambda: {
            "github": cast(AnyHttpUrl, "https://github.com/oornnery"),
            "linkedin": cast(AnyHttpUrl, "https://www.linkedin.com/in/fabiohcsouza/"),
            "x": cast(AnyHttpUrl, "https://x.com/fabiohcsouza"),
        }
    )
    default_language: str = "en"
    supported_languages: list[str] = Field(default_factory=lambda: ["en", "pt"])

    # Security
    secret_key: str = Field(min_length=16)
    csrf_token_expiry: int = 3600
    rate_limit: str = "10/minute"

    # Contact
    contact_webhook_url: str = ""
    contact_email_to: str = ""
    contact_email_subject: str = "New contact form submission from portfolio website"
    smtp_host: str = ""
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_timeout_seconds: int = Field(default=10, ge=1, le=120)


if TYPE_CHECKING:
    settings = cast(Settings, object())
else:
    settings = Settings()
