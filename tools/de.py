"""Definitive Edition: revisar los cambios y armar ISO de prueba.

Uso:
  python tools/de.py verificar                 # que ninguna opción pise a otra
  python tools/de.py resumen [perfil]          # qué cambia cada opción, con ejemplos
  python tools/de.py iso PERFIL ENTRADA SALIDA [opcion=nivel ...]
      Copia ENTRADA (ISO original o ya traducida, de cualquiera de los dos discos) y le aplica
      el perfil, con los ajustes opcionales. Ejemplo:
      python tools/de.py iso definitiva work/es1.iso work/es1_de.iso deuda=0
"""
import argparse
import shutil
import sys
from collections import Counter

from juego import BATDAT, SECTOR, Datos, Iso, Volume, aplicar
from opciones import OPCIONES, PERFILES, POR_ID, POR_PERFIL, cambios


def verificar(datos):
    """Comprueba que dos opciones distintas no toquen el mismo byte y que cada cambio cambie algo."""
    dueño = {}
    for o in OPCIONES:
        for nivel in range(1, max(1, len(o.niveles)) + 1):
            cs = o.cambios(datos, nivel)
            assert cs, f"{o.id} nivel {nivel} no cambia nada"
            for c in cs:
                for b in range(c.ancho):
                    clave = (c.archivo, c.seccion, c.pos + b)
                    otro = dueño.setdefault(clave, o.id)
                    assert otro == o.id, f"{o.id} y {otro} tocan {clave}"
    for p in PERFILES:
        for id_, nivel in p.niveles.items():
            assert 1 <= nivel <= max(1, len(POR_ID[id_].niveles)), (p.id, id_)
            assert POR_ID[id_].probada, f"{p.id} trae {id_}, que falta probar en el juego"
    print(f"{len(OPCIONES)} opciones y {len(PERFILES)} perfiles sin conflictos")


def resumen(datos, perfil):
    niveles = POR_PERFIL[perfil].niveles if perfil else {o.id: 1 for o in OPCIONES}
    por_enemigo = {e.n: e for e in datos.enemigos}
    for o in OPCIONES:
        if not niveles.get(o.id):
            continue
        nivel = niveles[o.id]
        etiqueta = o.niveles[nivel - 1]["es"] if o.niveles else ""
        cs = o.cambios(datos, nivel)
        aviso = "" if o.probada else "  [falta probar en el juego]"
        print(f"\n{o.nombre['es']} {etiqueta}: {len(cs)} cambios{aviso}")
        for c in cs[:6]:
            quien = ""
            if c.archivo == BATDAT and c.seccion == 1:
                quien = por_enemigo[c.pos // 0x5C].nombre
            print(f"  {c.archivo} s{c.seccion} +{c.pos:#06x}: {c.original} -> {c.nuevo}  {quien}")
    clases = Counter(e.clase for e in datos.enemigos)
    print("\nEnemigos:", dict(clases))


def parchear_iso(perfil, entrada, salida, ajustes):
    niveles = dict(POR_PERFIL[perfil].niveles)
    for a in ajustes:
        id_, nivel = a.split("=")
        assert id_ in POR_ID, f"opción desconocida: {id_}"
        niveles[id_] = int(nivel)
    datos = Datos()
    lista = cambios(datos, niveles)
    shutil.copyfile(entrada, salida)
    iso = Iso(salida)
    vol = Volume(iso, 0)
    entry = vol.by_path[BATDAT]
    batdat, exe = bytearray(vol.read(entry)), bytearray(iso.read_file(iso.executable))
    aplicar(lista, batdat, exe)
    iso.f.close()
    with open(salida, "r+b") as f:
        f.seek((vol.base + entry.sector) * SECTOR)
        f.write(batdat)
        f.seek(iso.files[iso.executable][0] * SECTOR)
        f.write(exe)
    activas = ", ".join(f"{k}={v}" for k, v in niveles.items() if v)
    print(f"{salida}: {len(lista)} cambios ({activas})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verificar")
    r = sub.add_parser("resumen")
    r.add_argument("perfil", nargs="?", choices=list(POR_PERFIL))
    i = sub.add_parser("iso")
    i.add_argument("perfil", choices=list(POR_PERFIL))
    i.add_argument("entrada")
    i.add_argument("salida")
    i.add_argument("ajustes", nargs="*")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.cmd == "verificar":
        verificar(Datos())
    elif a.cmd == "resumen":
        resumen(Datos(), a.perfil)
    else:
        parchear_iso(a.perfil, a.entrada, a.salida, a.ajustes)


if __name__ == "__main__":
    sys.exit(main())
