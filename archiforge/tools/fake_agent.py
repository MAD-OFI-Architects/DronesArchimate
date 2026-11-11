"""Agente SIMULADO para probar el orquestador sin gastar un agente real (solo dominio Python).
Lee la orden de trabajo, y declara cada símbolo del manifiesto en su capa. Uso: fake_agent.py <orden.md>"""
import re, sys
from pathlib import Path

work = Path(sys.argv[1]); text = work.read_text(encoding="utf-8")
stage = re.search(r"# Orden de trabajo — (\S+)", text).group(1)
root = Path.cwd()
DIRS = {"domain": "domain", "application": "application", "contracts": "contracts",
        "infrastructure": "adapters/outbound", "api": "adapters/inbound/http", "tests": None}

if stage in ("S03-adr", "S50-verify"):
    slug = re.search(r"out/docs/([a-z0-9-]+)/", text).group(1)
    base = root / "out_dryrun/docs" / slug; base.mkdir(parents=True, exist_ok=True)
    if stage == "S50-verify":
        (base / "verificacion.md").write_text("# Verificación\n\n| Hallazgo | Severidad |\n|---|---|\n| ninguno | - |\n\nVeredicto: aprobado (agente simulado).\n", encoding="utf-8")
        sys.exit(0)
    import json
    man = json.loads((root / ".forge-dry" / slug / "manifest.json").read_text(encoding="utf-8"))
    cls = [i["name"] for i in man["items"] if i["kind"] in ("aggregate_root", "repository_port")][:2] or ["X"]
    pats = re.findall(r"\*\*Patrón elegido\*\* `\w+` — ([^\n]+)", text)
    rows = "".join(f"| {p} | {slug} | `{cls[i % len(cls)]}` | x |\n" for i, p in enumerate(pats)) or f"| Repository | {slug} | `{cls[0]}` | x |\n"
    (base / "decisiones-arquitectura.md").write_text(
        "# Decisiones\n## Arquitectura\n## Estilo\n## Base de datos\n## Patrones\n| Patrón | Dominio | Clases | Por qué |\n|---|---|---|---|\n" + rows +
        "## Despliegue\n## Microfrontend\n", encoding="utf-8")
    sys.exit(0)

slug = re.search(r"out/services/([a-z0-9-]+)/", text).group(1)
pkg = slug.replace("-", "_")
svc = root / "out_dryrun/services" / slug
rows = re.findall(r"^\| (\w+) \| (\w+) \| `([^`]+)` \|", text, re.M)
(svc / "src" / pkg).mkdir(parents=True, exist_ok=True)
(svc / "src" / pkg / "__init__.py").touch()
(svc / "pyproject.toml").write_text(f'[project]\nname="{slug}"\nversion="0.0.1"\nrequires-python=">=3.11"\n[project.optional-dependencies]\ndev=["pytest"]\n'
                                    '[tool.setuptools.packages.find]\nwhere=["src"]\n[tool.pytest.ini_options]\npythonpath=["src"]\n', encoding="utf-8")
tests = []
for layer, kind, name in rows:
    if kind == "file":
        (svc / ("Dockerfile" if name == "Dockerfile" else "README.md")).write_text("x\n", encoding="utf-8"); continue
    if layer == "tests":
        tests.append(name); continue
    if kind == "route":
        d = svc / "src" / pkg / "adapters/inbound/http"; d.mkdir(parents=True, exist_ok=True)
        (d / "__init__.py").touch(); (d / f"route_{re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')}.py").write_text(f'ROUTE = "{name}"\n', encoding="utf-8"); continue
    sub = DIRS.get(layer)
    if not sub: continue
    d = svc / "src" / pkg / sub; d.mkdir(parents=True, exist_ok=True)
    for part in [d] + [d.parents[i] for i in range(len(sub.split("/")) - 1)]:
        (part / "__init__.py").touch()
    (d / f"{name.lower()}.py").write_text(f"class {name}:\n    pass\n", encoding="utf-8")
if True:
    t = svc / "tests"; t.mkdir(exist_ok=True)
    (t / f"test_{stage.replace('-', '_')}.py").write_text("NAMES = " + repr(tests) + "\n\ndef test_ok():\n    assert isinstance(NAMES, list)\n", encoding="utf-8")
print("ok", stage, len(rows))
