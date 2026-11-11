"""Detectores estructurales de patrones sobre código C#, Python y Java (heurísticas: existe la forma, no se juzga su uso)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forge import patrones  # noqa: E402

CS = {
    "abstraccion": "public interface IDescuento { decimal Aplicar(decimal m); }\npublic sealed class DescuentoFijo : IDescuento { public decimal Aplicar(decimal m) => m - 5; }\n"
                   "public sealed class DescuentoPorcentual : IDescuento { public decimal Aplicar(decimal m) => m * 0.9m; }\n",
    "envoltorio": "public interface IRepo { void Guardar(); }\npublic sealed class RepoSql : IRepo { public void Guardar() {} }\n"
                  "public sealed class RepoConCache : IRepo { private readonly IRepo _interno; public RepoConCache(IRepo interno) { _interno = interno; } public void Guardar() => _interno.Guardar(); }\n",
    "instancia_unica": "public sealed class Configuracion { private static readonly Configuracion _i = new(); private Configuracion() {} public static Configuracion Instance => _i; }\n",
    "constructor_fluido": "public class PedidoBuilder { public PedidoBuilder ConCliente(string c) { return this; } public PedidoBuilder ConItem(string i) { return this; } public Pedido Build() => new(); }\n",
    "clonacion": "public class Plantilla { public Plantilla Clone() => (Plantilla)MemberwiseClone(); }\n",
    "suscriptores": "public class Sensor { private readonly List<IObservador> _obs = new(); public void Subscribe(IObservador o) => _obs.Add(o); public void Notificar() { foreach (var o in _obs) o.Actualizar(); } }\n",
    "plantilla": "public abstract class Reporte { public string Generar() { return Encabezado() + Cuerpo(); } protected abstract string Encabezado(); protected abstract string Cuerpo(); }\n",
    "nada": "public class Simple { public int Sumar(int a, int b) => a + b; }\n",
}
JAVA = {
    "abstraccion": "public interface Descuento { double aplicar(double m); }\nclass DescuentoFijo implements Descuento { public double aplicar(double m) { return m - 5; } }\n"
                   "class DescuentoPorcentual implements Descuento { public double aplicar(double m) { return m * 0.9; } }\n",
    "envoltorio": "interface Repo { void guardar(); }\nclass RepoSql implements Repo { public void guardar() {} }\n"
                  "class RepoConCache implements Repo { private final Repo interno; RepoConCache(Repo interno) { this.interno = interno; } public void guardar() { interno.guardar(); } }\n",
    "instancia_unica": "public final class Configuracion { private static final Configuracion INSTANCE = new Configuracion(); private Configuracion() {} public static Configuracion getInstance() { return INSTANCE; } }\n",
    "constructor_fluido": "public class PedidoBuilder { public PedidoBuilder conCliente(String c) { return this; } public PedidoBuilder conItem(String i) { return this; } public Pedido build() { return new Pedido(); } }\n",
    "clonacion": "public class Plantilla implements Cloneable { public Plantilla clone() { return new Plantilla(); } }\n",
    "suscriptores": "public class Sensor { private final List<Observador> obs = new ArrayList<>(); public void subscribe(Observador o) { obs.add(o); } public void notificar() { for (Observador o : obs) o.actualizar(); } }\n",
    "plantilla": "public abstract class Reporte { public String generar() { return encabezado() + cuerpo(); } protected abstract String encabezado(); protected abstract String cuerpo(); }\n",
    "nada": "public class Simple { public int sumar(int a, int b) { return a + b; } }\n",
}
PY = {
    "abstraccion": "from abc import ABC, abstractmethod\nclass Descuento(ABC):\n    @abstractmethod\n    def aplicar(self, m): ...\nclass DescuentoFijo(Descuento):\n    def aplicar(self, m): return m - 5\n"
                   "class DescuentoPorcentual(Descuento):\n    def aplicar(self, m): return m * 0.9\n",
    "envoltorio": "from abc import ABC, abstractmethod\nclass Repo(ABC):\n    @abstractmethod\n    def guardar(self): ...\nclass RepoSql(Repo):\n    def guardar(self): pass\n"
                  "class RepoConCache(Repo):\n    def __init__(self, interno: Repo):\n        self._interno = interno\n    def guardar(self):\n        self._interno.guardar()\n",
    "instancia_unica": "class Configuracion:\n    _instance = None\n    def __new__(cls):\n        if cls._instance is None:\n            cls._instance = super().__new__(cls)\n        return cls._instance\n",
    "constructor_fluido": "class PedidoBuilder:\n    def con_cliente(self, c):\n        return self\n    def con_item(self, i):\n        return self\n    def build(self):\n        return object()\n",
    "clonacion": "import copy\nclass Plantilla:\n    def clone(self):\n        return copy.deepcopy(self)\n",
    "suscriptores": "class Sensor:\n    def __init__(self):\n        self._obs = []\n    def subscribe(self, o):\n        self._obs.append(o)\n    def notificar(self):\n        for o in self._obs:\n            o.actualizar()\n",
    "plantilla": "from abc import ABC, abstractmethod\nclass Reporte(ABC):\n    def generar(self):\n        return self.encabezado() + self.cuerpo()\n    @abstractmethod\n    def encabezado(self): ...\n    @abstractmethod\n    def cuerpo(self): ...\n",
    "nada": "class Simple:\n    def sumar(self, a, b):\n        return a + b\n",
}
SRC = {"csharp": (CS, ".cs", "src/Svc.Domain"), "java": (JAVA, ".java", "src/main/java/svc/domain"), "python": (PY, ".py", "src/svc/domain")}
CHECK = {"abstraccion": "abstraccion_con_implementaciones:2", "envoltorio": "envoltorio", "instancia_unica": "instancia_unica",
         "constructor_fluido": "constructor_fluido", "clonacion": "clonacion", "suscriptores": "suscriptores", "plantilla": "plantilla"}


def decls_of(tmp_path, language, key):
    files, ext, folder = SRC[language]
    f = tmp_path / folder / f"Codigo{ext}"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(files[key], encoding="utf-8")
    return patrones.declarations(tmp_path, language)


@pytest.mark.parametrize("language", ["csharp", "java", "python"])
@pytest.mark.parametrize("key", list(CHECK))
def test_each_detector_finds_its_structure(tmp_path, language, key):
    ok, detail = patrones.run_check(CHECK[key], decls_of(tmp_path, language, key), language)
    assert ok, f"{language}/{key}: {detail}"


@pytest.mark.parametrize("language", ["csharp", "java", "python"])
@pytest.mark.parametrize("key", list(CHECK))
def test_no_detector_fires_on_plain_code(tmp_path, language, key):
    ok, detail = patrones.run_check(CHECK[key], decls_of(tmp_path, language, "nada"), language)
    assert not ok, f"{language}/{key} dio falso positivo: {detail}"


def test_one_implementation_is_not_enough_for_an_abstraction_with_two(tmp_path):
    f = tmp_path / "src/svc/domain/uno.py"
    f.parent.mkdir(parents=True)
    f.write_text(PY["abstraccion"].split("class DescuentoPorcentual")[0], encoding="utf-8")
    ok, detail = patrones.run_check("abstraccion_con_implementaciones:2", patrones.declarations(tmp_path, "python"), "python")
    assert not ok and "se exigen 2" in detail


def test_named_role_check_and_unknown_checks(tmp_path):
    decls = decls_of(tmp_path, "python", "constructor_fluido")
    assert patrones.run_check("clase_con_nombre:(?i)builder", decls, "python")[0]
    assert not patrones.run_check("clase_con_nombre:(?i)saga", decls, "python")[0]
    assert patrones.parse_check("inventado") is None and patrones.run_check("inventado", decls, "python")[0] is False


def test_tests_and_smoke_code_do_not_count(tmp_path):
    f = tmp_path / "tests/test_x.py"
    f.parent.mkdir(parents=True)
    f.write_text(PY["instancia_unica"], encoding="utf-8")
    assert patrones.declarations(tmp_path, "python") == []


# ------------------------------------------------------------------ decisiones, gate estructural y ADR
import dataclasses  # noqa: E402

from forge import config, decisions, gates as G  # noqa: E402
from forge.config import Domain  # noqa: E402

TOOL = Path(__file__).resolve().parents[1]


def dom(**patterns):
    return Domain("Repuestos del Taller", "python", "hexagonal", "microservicio", "postgresql", 5102, patterns=patterns)


def test_validation_asks_where_a_pattern_applies_and_checks_its_dependencies():
    cfg = dataclasses.replace(config.load(TOOL / "forge.toml"), policy={})
    errors, _ = decisions.validate(cfg, dom(strategy={"usar": True}))
    assert any("Strategy" in e and "aplicar_en" in e for e in errors)
    errors, _ = decisions.validate(cfg, dom(strategy={"usar": True, "aplicar_en": "cálculo de la reposición"}))
    assert errors == []
    errors, _ = decisions.validate(cfg, dom(saga={"usar": True, "aplicar_en": "reposición"}))                  # saga requiere eventos
    assert any("eventos" in e for e in errors)
    errors, _ = decisions.validate(cfg, dom(strategy={"usar": False}))                                          # sin elegir: no se pregunta nada
    assert errors == []


def _service(tmp_path, code, slug="repuestos-del-taller"):
    f = tmp_path / "services" / slug / "src" / "repuestos_del_taller" / "domain" / "codigo.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(code, encoding="utf-8")
    return dataclasses.replace(config.load(TOOL / "forge.toml"), out=tmp_path, policy={})


def test_structure_gate_checks_only_the_patterns_the_architect_chose(tmp_path):
    d = dom(strategy={"usar": True, "aplicar_en": "reposición"}, cqrs={"usar": True}, singleton={"usar": False})
    cfg = _service(tmp_path, PY["nada"])
    g = G.patterns_gate(cfg, d)
    assert not g.ok and "Strategy" in g.detail and "reposición" in g.detail and "Singleton" not in g.detail      # cqrs no tiene chequeo; singleton no se eligió
    cfg = _service(tmp_path, PY["abstraccion"])
    assert G.patterns_gate(cfg, d).ok
    assert G.patterns_gate(cfg, dom(cqrs={"usar": True})).ok                                                   # patrones sin chequeo no se tocan


def test_build_gates_run_the_structure_check_in_the_adapters_stage():
    import inspect
    assert "patterns_gate" in inspect.getsource(G.build_gates)


def _adr(cfg, rows):
    doc = cfg.out / "docs" / "repuestos-del-taller" / "decisiones-arquitectura.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("# Decisiones\n## Arquitectura\n## Base de datos\n## Estilo\n## Despliegue\n## Microfrontend\n## Patrones\n"
                   "| Patrón | Dominio | Clases | Por qué |\n|---|---|---|---|\n" + rows, encoding="utf-8")


def test_adr_must_cite_as_many_real_classes_as_the_pattern_has_roles(tmp_path):
    d = dom(strategy={"usar": True, "aplicar_en": "reposición"})
    cfg = _service(tmp_path, PY["abstraccion"])
    cfg.domains = [d]
    _adr(cfg, "| Strategy | Repuestos | `Descuento` | variantes |\n")
    g = G.adr_gate(cfg, {}, final=True)
    assert not g.ok and "al menos 3 clases" in g.detail and "Strategy" in g.detail
    _adr(cfg, "| Strategy | Repuestos | `Descuento`, `DescuentoFijo`, `DescuentoPorcentual` | variantes |\n")
    assert G.adr_gate(cfg, {}, final=True).ok


def test_decisions_prompt_lists_each_chosen_pattern_on_its_own_lines():
    import jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TOOL / "prompts"), undefined=jinja2.StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    d = Domain("Intervenciones", "csharp", "clean-ddd", "microservicio", "mongodb", 5101, patterns={
        "cqrs": {"usar": True}, "strategy": {"usar": True, "aplicar_en": "el cálculo de horas-hombre"}, "singleton": {"usar": False}})
    text = env.get_template("_decisions.md.j2").render(d=d, cat=decisions.catalog(TOOL), info={"env": {}})
    lines = text.splitlines()
    head = [l for l in lines if l.startswith("- **Patrón elegido**")]
    assert len(head) == 2 and all("**Patrón elegido**" not in l[3:] for l in head)                    # nada pegado en una sola línea
    assert any("**Estructura canónica**" in l and "ConcreteStrategy" in l for l in lines)
    assert any("Aplícalo SOLO ahí" in l and "el cálculo de horas-hombre" in l for l in lines)
    assert any("al menos 3 clases reales" in l for l in lines) and any("refactoring.guru/es/design-patterns/strategy" in l for l in lines)
    assert not any("Singleton" in l and "Patrón elegido" in l for l in lines)
