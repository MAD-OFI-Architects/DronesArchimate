"""Detección de cambios en el modelo y las decisiones: `build` reabre lo afectado sin `--force` manual."""
import dataclasses
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forge import cambios, config  # noqa: E402
from forge.config import Domain  # noqa: E402
from forge.runner import Runner  # noqa: E402

DISENO = ROOT.parent / "diseno"
ARCHI = DISENO / "modelo/drones-mantenimiento.archimate"
PATRONES = {"cqrs": {"usar": True}, "memento": {"usar": True}}


def repuestos(**cambio):
    base = dict(context="Repuestos del Taller", language="python", architecture="hexagonal", style="microservicio",
                database="postgresql", port=5101, patterns=dict(PATRONES))
    return Domain(**{**base, **cambio})


def intervenciones():
    return Domain("Intervenciones", "csharp", "clean-ddd", "microservicio", "mongodb", 5102, patterns=dict(PATRONES))


def cfg_en(tmp_path, archimate=ARCHI):
    return dataclasses.replace(config.load(ROOT / "forge.toml"), root=tmp_path, archimate=archimate)


def test_la_huella_es_estable_y_la_decision_la_cambia(tmp_path):
    cfg = cfg_en(tmp_path)
    a, b = cambios.huellas(cfg, repuestos()), cambios.huellas(cfg, repuestos())
    assert a == b
    assert cambios.huellas(cfg, repuestos(language="java"))["modelo"] != a["modelo"]
    assert cambios.huellas(cfg, repuestos(patterns={"cqrs": {"usar": True}}))["modelo"] != a["modelo"]


def test_las_justificaciones_no_cambian_lo_que_se_construye(tmp_path):
    cfg = cfg_en(tmp_path)
    a = cambios.huellas(cfg, repuestos())
    b = cambios.huellas(cfg, repuestos(rationale={"lenguaje": "porque sí"}))
    assert b["modelo"] == a["modelo"] and b["justificaciones"] != a["justificaciones"]


def test_un_cambio_del_archimate_solo_afecta_al_dominio_que_toca(tmp_path):
    copia = tmp_path / "diseno"
    shutil.copytree(DISENO / "modelo", copia / "modelo")
    for fase in DISENO.glob("Fase0*"):
        shutil.copytree(fase, copia / fase.name)
    modelo = copia / "modelo/drones-mantenimiento.archimate"
    original = cfg_en(tmp_path, ARCHI)
    modelo.write_text(modelo.read_text(encoding="utf-8").replace("Existencia", "ExistenciaEnBodega"), encoding="utf-8")
    editado = dataclasses.replace(cfg_en(tmp_path, modelo), docs_dir=copia)
    assert cambios.huellas(editado, repuestos())["modelo"] != cambios.huellas(original, repuestos())["modelo"]
    assert cambios.huellas(editado, intervenciones())["modelo"] == cambios.huellas(original, intervenciones())["modelo"]
    dif = cambios.diferencia(cambios.huellas(original, repuestos()), cambios.huellas(editado, repuestos()))
    assert dif["modelo"] and dif["agregados"] and dif["quitados"]


def _corredor(tmp_path, d):
    run = Runner(cfg_en(tmp_path), d)
    run.sink = lambda _l: None
    return run


def _con_etapas_pasadas(run):
    for s in run.stages:
        run.state[s.id] = {"status": "passed", "attempts": 1}
    run.save()


def test_primera_vez_guarda_la_huella_y_no_reabre_nada(tmp_path):
    run = _corredor(tmp_path, repuestos())
    _con_etapas_pasadas(run)
    run.sincronizar_insumos()
    assert (run.fdir / cambios.ARCHIVO).exists()
    assert all(v["status"] == "passed" for v in run.state.values())


def test_si_el_modelo_o_la_decision_cambian_se_reabren_todas_las_etapas(tmp_path):
    run = _corredor(tmp_path, repuestos())
    _con_etapas_pasadas(run)
    run.sincronizar_insumos()
    nuevo = _corredor(tmp_path, repuestos(style="monolito-modular"))
    nuevo.sincronizar_insumos()
    assert nuevo.state == {}
    again = _corredor(tmp_path, repuestos(style="monolito-modular"))
    _con_etapas_pasadas(again)
    again.sincronizar_insumos()                                    # ya está al día: no vuelve a reabrir
    assert all(v["status"] == "passed" for v in again.state.values())


def test_si_solo_cambian_las_justificaciones_se_rehacen_solo_las_decisiones(tmp_path):
    run = _corredor(tmp_path, repuestos())
    _con_etapas_pasadas(run)
    run.sincronizar_insumos()
    nuevo = _corredor(tmp_path, repuestos(rationale={"lenguaje": "x"}))
    nuevo.sincronizar_insumos()
    assert set(nuevo.state) == {s.id for s in nuevo.stages} - set(cambios.ETAPAS_DE_JUSTIFICACIONES)


def test_el_estado_informa_que_esta_desactualizado(tmp_path):
    run = _corredor(tmp_path, repuestos())
    run.sincronizar_insumos()
    cfg = cfg_en(tmp_path)
    assert cambios.pendiente(cfg, repuestos(), run.fdir) == ""
    assert cambios.pendiente(cfg, repuestos(language="java"), run.fdir) == "modelo"
    assert cambios.pendiente(cfg, repuestos(rationale={"a": "b"}), run.fdir) == "justificaciones"
