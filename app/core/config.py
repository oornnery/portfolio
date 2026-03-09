from typing import TYPE_CHECKING, cast
from urllib.parse import urlsplit, urlunsplit

from pydantic import AliasChoices, AnyHttpUrl, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # App
    app_name: str = "Portfolio"
    app_description: str = "My personal portfolio website"
    debug: bool = False
    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"
    telemetry_enabled: bool = True
    telemetry_service_name: str = Field(
        default="portfolio-backend",
        validation_alias=AliasChoices("TELEMETRY_SERVICE_NAME", "OTEL_SERVICE_NAME"),
    )
    telemetry_service_namespace: str = "portfolio"
    telemetry_traces_sample_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    telemetry_exporter_otlp_endpoint: str = Field(
        default="",
        validation_alias=AliasChoices(
            "TELEMETRY_EXPORTER_OTLP_ENDPOINT",
            "OTEL_EXPORTER_OTLP_ENDPOINT",
        ),
    )
    telemetry_exporter_otlp_insecure: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "TELEMETRY_EXPORTER_OTLP_INSECURE",
            "OTEL_EXPORTER_OTLP_INSECURE",
        ),
    )
    telemetry_exporter_otlp_headers: str = Field(
        default="",
        validation_alias=AliasChoices(
            "TELEMETRY_EXPORTER_OTLP_HEADERS",
            "OTEL_EXPORTER_OTLP_HEADERS",
        ),
    )
    telemetry_console_exporters: bool = False
    telemetry_logs_enabled: bool = True
    otel_sdk_disabled_raw: str | None = Field(
        default=None,
        validation_alias="OTEL_SDK_DISABLED",
        exclude=True,
        repr=False,
    )
    otel_logs_exporter_raw: str | None = Field(
        default=None,
        validation_alias="OTEL_LOGS_EXPORTER",
        exclude=True,
        repr=False,
    )

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
    frontend_telemetry_enabled: bool = True
    frontend_telemetry_service_name: str = "portfolio-frontend"
    frontend_telemetry_otlp_endpoint: str = ""
    frontend_telemetry_sample_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    frontend_telemetry_proxy_path: str = "/otel/v1/traces"

    # Security
    secret_key: str = Field(min_length=16)
    csrf_token_expiry: int = 3600
    default_rate_limit: str = "60/minute"
    rate_limit: str = "10/minute"
    trust_forwarded_ip_headers: bool = False
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    cors_allow_origins: str = ""
    cors_allow_methods: str = "GET,POST,OPTIONS"
    cors_allow_headers: str = "Content-Type,X-Request-ID"
    cors_allow_credentials: bool = False
    max_request_body_bytes: int = Field(default=1_048_576, ge=1024)
    contact_max_body_bytes: int = Field(default=65_536, ge=1024)

    # Content
    markdown_cache_ttl: int = Field(default=300, ge=0)
    dev_csp_enabled: bool = True
    github_token: str = ""
    github_api_timeout_seconds: int = Field(default=8, ge=1, le=60)
    github_gist_comments_limit: int = Field(default=20, ge=1, le=100)

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

    @model_validator(mode="after")
    def _apply_otel_fallbacks(self) -> "Settings":
        if (
            "telemetry_enabled" not in self.model_fields_set
            and self.otel_sdk_disabled_raw is not None
        ):
            value = self.otel_sdk_disabled_raw.strip().lower()
            self.telemetry_enabled = value not in {"1", "true", "yes", "on"}

        if (
            "telemetry_logs_enabled" not in self.model_fields_set
            and self.otel_logs_exporter_raw is not None
        ):
            value = self.otel_logs_exporter_raw.strip().lower()
            self.telemetry_logs_enabled = value not in {"", "none"}

        return self

    def frontend_telemetry_collector_endpoint(self) -> str:
        explicit = self.frontend_telemetry_otlp_endpoint.strip()
        if explicit:
            return explicit

        backend = self.telemetry_exporter_otlp_endpoint.strip()
        if not backend:
            return ""

        parsed = urlsplit(backend)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return ""

        port = parsed.port
        path = parsed.path.strip() or "/"
        if port == 4317:
            netloc = parsed.hostname
            if parsed.username:
                credentials = parsed.username
                if parsed.password:
                    credentials = f"{credentials}:{parsed.password}"
                netloc = f"{credentials}@{netloc}"
            netloc = f"{netloc}:4318"
            return urlunsplit((parsed.scheme, netloc, "/v1/traces", "", ""))

        if port == 4318 and path == "/":
            return urlunsplit(
                (
                    parsed.scheme,
                    parsed.netloc,
                    "/v1/traces",
                    parsed.query,
                    parsed.fragment,
                )
            )

        return backend

    def frontend_telemetry_browser_endpoint(self) -> str:
        if not self.frontend_telemetry_is_enabled():
            return ""
        return self.frontend_telemetry_proxy_path

    def frontend_telemetry_is_enabled(self) -> bool:
        return self.frontend_telemetry_enabled and bool(
            self.frontend_telemetry_collector_endpoint()
        )


def split_csv(value: str) -> tuple[str, ...]:
    """Split a comma-separated string, stripping whitespace and dropping empties."""
    return tuple(item.strip() for item in value.split(",") if item.strip())


if TYPE_CHECKING:
    settings = cast(Settings, object())
else:
    settings = Settings()
