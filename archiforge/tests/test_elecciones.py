"""Elecciones dentro de un patrón (p. ej. el algoritmo de cifrado): el arquitecto las toma, la herramienta no elige por él."""
import dataclasses
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forge import config, decisions  # noqa: E402
from forge.archimate import build_ir  # noqa: E402
from forge.config import Domain  # noqa: E402
from forge.manifest import build_manifest  # noqa: E402


def dominio(**cifrado):
    return Domain("Repuestos del Taller", "python", "hexagonal", "microservicio", "postgresql", 5102,
                  patterns={"cifrado": {"usar": True, **cifrado}}, rationale={})


def test_el_algoritmo_de_cifrado_no_viene_elegido_y_se_exige():
    cfg = config.load(ROOT / "forge.toml")
    errores, _ = decisions.validate(cfg, dominio())
    assert any("Elige algoritmo" in e and "aes-256-gcm" in e and "chacha20-poly1305" in e for e in errores)
    assert not [e for e in decisions.validate(cfg, dominio(algoritmo="aes-256-gcm"))[0] if "algoritmo" in e]
    assert any("Elige algoritmo" in e for e in decisions.validate(cfg, dominio(algoritmo="rot13"))[0])


def test_el_manifiesto_pide_la_clase_del_algoritmo_elegido():
    ir = build_ir(config.load(ROOT / "forge.toml").archimate, ROOT.parent / "diseno")
    nombres = lambda d: [i["name"] for i in build_manifest(ir, [d])["items"] if i["kind"] == "crypto_impl"]  # noqa: E731
    assert nombres(dominio(algoritmo="aes-256-gcm")) == ["CifradorAes"]
    assert nombres(dominio(algoritmo="chacha20-poly1305")) == ["CifradorChaCha20"]


def test_el_prompt_de_infraestructura_toma_la_clase_del_algoritmo_elegido():
    plantilla = (ROOT / "prompts/layer.md.j2").read_text(encoding="utf-8")
    assert "d.patterns.cifrado.algoritmo" in plantilla and "{{ cif[0] }}" in plantilla      # el nombre sale de la decisión, no está fijo
    assert "`CifradorAes` (AES‑GCM" not in plantilla


def test_decide_acepta_la_eleccion_con_detail_y_rechaza_un_patron_no_elegido(tmp_path):
    (tmp_path / "forge.toml").write_text(f'[inputs]\narchimate = "{ROOT.parent / "diseno/modelo/drones-mantenimiento.archimate"}"\ndocs_dir = "{ROOT.parent / "diseno"}"\n'
                                         '[output]\ndir = "out"\n[decisions]\ndir = "decisiones"\n', encoding="utf-8")
    run = lambda *a: subprocess.run([sys.executable, "-m", "forge", "-c", str(tmp_path / "forge.toml"), "decide", "Repuestos del Taller", "--lang", "python",
                                     "--arch", "hexagonal", "--style", "microservicio", "--db", "postgresql", "--why", "lenguaje=x", *a],
                                    cwd=ROOT, capture_output=True, text=True)
    sin = run("--patterns", "cifrado")
    assert sin.returncode != 0 and "Elige algoritmo" in (sin.stdout + sin.stderr)
    ok = run("--patterns", "cifrado", "--detail", "cifrado.algoritmo=chacha20-poly1305")
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert 'algoritmo = "chacha20-poly1305"' in (tmp_path / "decisiones/repuestos-del-taller.toml").read_text(encoding="utf-8")
    mal = run("--patterns", "cqrs", "--detail", "cifrado.algoritmo=aes-256-gcm")
    assert mal.returncode != 0 and "--detail" in (mal.stdout + mal.stderr)
