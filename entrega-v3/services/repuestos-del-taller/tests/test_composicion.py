"""Regresiones de la composición: el DSN del compose debe llegar digerible a psycopg."""
import sys
import types

from repuestos_del_taller.adapters.inbound.http.composicion import _repositorios


class _ConexionVacia:
    def execute(self, sql, params=()):
        return self


def test_database_url_estilo_sqlalchemy_se_normaliza_para_psycopg(monkeypatch) -> None:
    urls: list[str] = []

    def connect(url, autocommit):
        urls.append(url)
        return _ConexionVacia()

    monkeypatch.setitem(sys.modules, "psycopg", types.SimpleNamespace(connect=connect))
    _repositorios("postgresql+psycopg://forge:forge@postgres:5432/repuestos_del_taller")
    assert urls == ["postgresql://forge:forge@postgres:5432/repuestos_del_taller"]
