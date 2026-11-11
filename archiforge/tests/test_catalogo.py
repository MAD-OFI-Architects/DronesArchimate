"""El catálogo de patrones: completo, consistente y neutral (describe; no recomienda ni preselecciona)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forge import decisions  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GOF = {
    "creacional": ["factory-method", "abstract-factory", "builder", "prototype", "singleton"],
    "estructural": ["adapter", "bridge", "composite", "decorator", "facade", "flyweight", "proxy"],
    "comportamiento": ["chain-of-responsibility", "command", "interpreter", "iterator", "mediator", "memento", "observer", "state",
                       "strategy", "template-method", "visitor"],
}
CATEGORIAS = {"creacional", "estructural", "comportamiento", "aplicación", "dominio", "integración", "infraestructura", "persistencia", "resiliencia"}


@pytest.fixture(scope="module")
def cat():
    return decisions.catalog(ROOT)


def test_all_23_gof_patterns_are_in_the_catalog_with_their_category(cat):
    for categoria, ids in GOF.items():
        for pid in ids:
            assert pid in cat, f"falta {pid}"
            assert cat[pid]["categoria"] == categoria, pid
    assert sum(len(v) for v in GOF.values()) == 23


def test_catalog_covers_domain_integration_persistence_and_resilience_patterns(cat):
    for pid in ("repository", "unit-of-work", "domain-events", "domain-service", "null-object", "dto", "service-layer", "data-mapper",
                "identity-map", "event-sourcing", "saga", "idempotent-consumer", "dead-letter-queue", "circuit-breaker", "retry", "timeout",
                "bulkhead", "rate-limiter", "materialized-view", "cqrs", "outbox", "eventos", "acl", "cache", "cifrado", "specification", "pipeline"):
        assert pid in cat, pid
    assert len(cat) >= 50


def test_existing_pattern_ids_keep_working(cat):
    for pid in ("cqrs", "pipeline", "memento", "state", "specification", "outbox", "eventos", "acl", "cache", "cifrado"):
        assert pid in cat


def test_every_entry_is_complete_and_consistent(cat):
    for pid, p in cat.items():
        assert re.fullmatch(r"[a-z][a-z0-9-]*", pid), pid
        for k in ("nombre", "categoria", "que_es", "cuando_si", "cuando_no", "costo"):
            assert isinstance(p.get(k), str) and p[k].strip(), (pid, k)
        assert p["categoria"] in CATEGORIAS, (pid, p["categoria"])
        for req in p.get("requiere", []):
            assert req in cat, (pid, req)
        for k in ("roles", "principios", "chequeo"):
            assert isinstance(p.get(k, []), list), (pid, k)
        assert set(p.get("principios", [])) <= {"SRP", "OCP", "LSP", "ISP", "DIP"}, pid
        if p.get("fuente"):
            assert p["fuente"].startswith("https://"), pid


def test_patterns_that_target_arbitrary_code_ask_where_they_apply(cat):
    for pid in [i for ids in GOF.values() for i in ids if i not in ("memento", "state")]:
        assert cat[pid].get("requiere_donde") is True, pid
        assert cat[pid].get("roles"), f"{pid} sin roles"


def test_checks_reference_known_detectors(cat):
    from forge import patrones
    for pid, p in cat.items():
        for chk in p.get("chequeo", []):
            assert patrones.parse_check(chk) is not None, (pid, chk)


def test_catalog_text_is_neutral_reference(cat):
    text = " ".join(str(v) for p in cat.values() for v in p.values()).lower()
    assert not any(w in text for w in ("evaluaci", "rúbrica", "profesor", "recomend", "aconsej", "sugier", "deberías", "debes usar"))


def test_cli_lists_and_filters_the_catalog():
    import subprocess
    run = lambda *a: subprocess.run([sys.executable, "-m", "forge", "patterns", *a], cwd=ROOT, capture_output=True, text=True)  # noqa: E731
    all_ = run().stdout
    assert "factory-method" in all_ and "circuit-breaker" in all_ and len(all_.splitlines()) >= 51
    gof = run("--categoria", "estructural").stdout
    assert "decorator" in gof and "strategy" not in gof
    assert run("--categoria", "inexistente").returncode != 0
    ficha = run("strategy").stdout
    assert "Qué es:" in ficha and "Se usa cuando:" in ficha and "ConcreteStrategy" in ficha and "refactoring.guru" in ficha and "aplicar_en" in ficha
