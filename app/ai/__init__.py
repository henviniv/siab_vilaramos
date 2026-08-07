"""
Módulo de Inteligência Artificial do SIAB.

Responsabilidades:
- Gerar consultas SQL a partir de linguagem natural.
- Validar a segurança das consultas.
- Executar consultas no Supabase.
- Formatar respostas para o usuário.
"""

from .chat import perguntar

__all__ = ["perguntar"]