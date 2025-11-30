"""
Utility functions for common operations across the application.

Why: Centraliza funções auxiliares para evitar duplicação de código
     e garantir consistência no tratamento de dados.

How: Funções puras e type-safe para parsing de formulários,
     validação de dados e operações comuns.
"""

from __future__ import annotations

import json
from typing import Any


def get_form_str(form_data: Any, key: str, default: str = "") -> str:
    """
    Extrai um valor string de um formulário de forma segura.

    Why: form.get() retorna Union[UploadFile, str], precisamos garantir
         que sempre retornamos uma string para evitar erros de tipo.

    Args:
        form_data: Dados do formulário (Starlette FormData)
        key: Chave do campo a ser extraído
        default: Valor padrão se o campo não existir ou for vazio

    Returns:
        String extraída do formulário ou valor padrão
    """
    value = form_data.get(key)
    if value is None:
        return default
    if isinstance(value, str):
        return value
    # Se for UploadFile ou outro tipo, retorna default
    return default


def get_form_int(form_data: Any, key: str, default: int = 0) -> int:
    """
    Extrai um valor inteiro de um formulário de forma segura.

    Why: Formulários sempre enviam strings, precisamos converter
         para int de forma segura com fallback para default.

    Args:
        form_data: Dados do formulário
        key: Chave do campo
        default: Valor padrão se conversão falhar

    Returns:
        Inteiro extraído ou valor padrão
    """
    value = get_form_str(form_data, key)
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_form_bool(form_data: Any, key: str) -> bool:
    """
    Extrai um valor booleano de um formulário.

    Why: Checkboxes HTML enviam valor apenas quando marcados,
         então a presença do campo indica True.

    Args:
        form_data: Dados do formulário
        key: Chave do campo

    Returns:
        True se o campo existe e tem valor, False caso contrário
    """
    value = form_data.get(key)
    return bool(value)


def get_form_list(form_data: Any, key: str, separator: str = ",") -> list[str]:
    """
    Extrai uma lista de strings de um campo de formulário separado por vírgulas.

    Why: Tags e tech_stack são enviados como strings separadas por vírgula,
         precisamos converter para lista de forma limpa.

    Args:
        form_data: Dados do formulário
        key: Chave do campo
        separator: Caractere separador (default: vírgula)

    Returns:
        Lista de strings limpas (sem espaços extras)
    """
    value = get_form_str(form_data, key)
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]


def get_form_json(form_data: Any, key: str, default: Any = None) -> Any:
    """
    Extrai e parseia um campo JSON de um formulário.

    Why: Campos estruturados como work_experience são enviados como JSON string,
         precisamos parsear de forma segura com fallback.

    Args:
        form_data: Dados do formulário
        key: Chave do campo
        default: Valor padrão se parsing falhar

    Returns:
        Objeto Python parseado do JSON ou valor padrão
    """
    value = get_form_str(form_data, key)
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default
