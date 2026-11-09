"""Practica 2: importacion y exportacion en .jff, .json y .xml."""
import pytest

import formatos as fm


@pytest.mark.parametrize("ext", [".jff", ".json", ".xml"])
def test_ida_y_vuelta(ext, afn_lambda_anexo, tmp_path):
    ruta = fm.escribir_archivo(afn_lambda_anexo, tmp_path / f"a{ext}")
    leido = fm.leer_archivo(ruta)
    assert set(leido.estados) == set(afn_lambda_anexo.estados)
    assert leido.inicial == afn_lambda_anexo.inicial
    assert leido.finales == afn_lambda_anexo.finales
    assert leido.alfabeto == afn_lambda_anexo.alfabeto
    assert leido.transiciones == afn_lambda_anexo.transiciones


def test_jff_del_anexo_con_lambda():
    texto = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<structure><type>fa</type><automaton>
<state id="0" name="q0"><x>80.0</x><y>120.0</y><initial/></state>
<state id="1" name="q1"><x>240.0</x><y>120.0</y><final/></state>
<transition><from>0</from><to>1</to><read>a</read></transition>
<transition><from>0</from><to>0</to><read>b</read></transition>
<transition><from>0</from><to>1</to><read/></transition>
</automaton></structure>"""
    a = fm.leer_texto(texto)
    assert a.tipo() == "AFND-lambda"
    assert a.destinos("q0", "") == {"q1"}


def test_jff_con_cadena_en_transicion():
    texto = """<structure><type>fa</type><automaton>
<state id="0" name="A"><initial/></state><state id="1" name="B"><final/></state>
<transition><from>0</from><to>1</to><read>ab</read></transition></automaton></structure>"""
    a = fm.leer_texto(texto)
    assert a.acepta("ab") and not a.acepta("a")


def test_errores_de_formato():
    with pytest.raises(fm.ErrorFormato):
        fm.leer_texto("<structure><type>pda</type></structure>")
    with pytest.raises(fm.ErrorFormato):
        fm.leer_texto("{ no es json")
