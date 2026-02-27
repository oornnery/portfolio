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
    telemetry_enabled: bool = True
    telemetry_service_name: str = "portfolio-backend"
    telemetry_service_namespace: str = "portfolio"
    telemetry_traces_sample_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    telemetry_exporter_otlp_endpoint: str = ""
    telemetry_exporter_otlp_insecure: bool = True
    telemetry_exporter_otlp_headers: str = ""
    telemetry_console_exporters: bool = False
    telemetry_logs_enabled: bool = True

    # Site
    site_name: str = "Fabio Souza"
    base_url: AnyHttpUrl = cast(AnyHttpUrl, "http://localhost:8000")
    default_og_image: str = "/static/images/og-default.png"

    # Profile fallback data (used only if content/about.md does not define them)
    social_links: dict[str, AnyHttpUrl] = Field(
        default_factory=lambda: {
            "github": cast(AnyHttpUrl, "https://github.com/oornnery"),
            "linkedin": cast(AnyHttpUrl, "https://www.linkedin.com/in/fabiohcsouza/"),
            "x": cast(AnyHttpUrl, "https://x.com/fabiohcsouza"),
        }
    )
    default_language: str = "en"
    supported_languages: list[str] = Field(default_factory=lambda: ["en", "pt"])
    analytics_enabled: bool = True
    analytics_log_events: bool = True

    # Security
    secret_key: str = Field(min_length=16)
    csrf_token_expiry: int = 3600
    default_rate_limit: str = "60/minute"
    rate_limit: str = "10/minute"
    analytics_rate_limit: str = "30/minute"
    analytics_allowed_sources: str = "127.0.0.1,::1"
    analytics_allowed_origins: str = ""
    trust_forwarded_ip_headers: bool = False
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    cors_allow_origins: str = ""
    cors_allow_methods: str = "GET,POST,OPTIONS"
    cors_allow_headers: str = "Content-Type,X-Request-ID"
    cors_allow_credentials: bool = False
    max_request_body_bytes: int = Field(default=1_048_576, ge=1024)
    contact_max_body_bytes: int = Field(default=65_536, ge=1024)
    analytics_max_body_bytes: int = Field(default=262_144, ge=1024)

    # Content
    markdown_cache_ttl: int = Field(default=300, ge=0)
    dev_csp_enabled: bool = True

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
