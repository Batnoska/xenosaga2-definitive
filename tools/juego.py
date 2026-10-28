"""Datos de combate de Xenosaga Episode II que toca la Definitive Edition.

Cada cambio se guarda como "archivo, sección, posición, valor original, valor nuevo":
  - En yamamoto/batdat.us la posición es relativa al inicio de la sección. La traducción corre
    esos inicios pero no el contenido numérico, así que el mismo cambio vale para la ISO en
    inglés y para la traducida.
  - En el ejecutable (sección -1) la posición es absoluta. La traducción lo modifica en el
    lugar, y los ejecutables de los dos discos tienen estas tablas en la misma posición.

Formatos: ver docs/datos.md. Lee las ISO con las herramientas del repositorio de la traducción
(por defecto la carpeta Xenosaga2-ES junto a esta; se puede cambiar con X2_TRADUCCION).
"""
import os
import struct
import sys
from typing import NamedTuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADUCCION = os.environ.get("X2_TRADUCCION", os.path.join(os.path.dirname(ROOT), "Xenosaga2-ES"))
sys.path.insert(0, os.path.join(TRADUCCION, "tools"))
from x2iso import SECTOR, Iso, Volume, iso_paths  # noqa: E402,F401
from x2text import Batdat, decode  # noqa: E402

BATDAT = "yamamoto/batdat.us"
EJECUTABLE = "ejecutable"  # el del disco que se parchea (SLUS_208.92 o SLUS_211.33)

# batdat.us
ENEMIGOS, ETER, TECNICAS_DOBLES, ESPECIALES_ES, RECOMPENSAS = 1, 2, 12, 13, 15
ENEMIGO = 0x5C          # largo del registro de enemigo (sección 1)
CANTIDAD_ENEMIGOS = 125
ETER_INICIO = 0x53C4    # 57 registros de 32 bytes en la sección 2
# ejecutable
COSTOS = 0x2CD158       # 112 registros de 6 bytes: tipo, número, costo u16, llave, 0
CANTIDAD_COSTOS = 112
DEUDA = 0x1321A4        # lui a0,0x98 ; sd ra ; ori a0,a0,0x9680 -> 10.000.000


class Cambio(NamedTuple):
    archivo: str
    seccion: int  # -1 en el ejecutable
    pos: int
    ancho: int
    original: int
    nuevo: int


def inicios(batdat):
    """Inicio de cada sección de batdat.us, y el largo del archivo al final."""
    n = struct.unpack_from("<I", batdat, 0)[0]
    return list(struct.unpack_from(f"<{n}I", batdat, 8)) + [len(batdat)]


def aplicar(cambios, batdat, exe):
    """Aplica los cambios sobre batdat.us y el ejecutable (bytearray), comprobando cada original."""
    secs = inicios(batdat)
    for c in cambios:
        datos, base = (exe, 0) if c.seccion < 0 else (batdat, secs[c.seccion])
        p = base + c.pos
        actual = int.from_bytes(datos[p:p + c.ancho], "little")
        if actual != c.original:
            raise ValueError(f"{c.archivo} sección {c.seccion} +{c.pos:#x}: se esperaba {c.original}, hay {actual}")
        datos[p:p + c.ancho] = c.nuevo.to_bytes(c.ancho, "little")


class Enemigo(NamedTuple):
    n: int
    nombre: str
    clase: str  # "común", "común E.S.", "jefe" o "sin uso"
    numero: int
    vida: int
    fuerza: int
    vitalidad: int
    ataque_eter: int
    defensa_eter: int
    brk: tuple
    experiencia: int
    puntos_habilidad: int
    puntos_clase: int
    suelta: int  # probabilidad de soltar el objeto común (%)
    rara: int  # probabilidad del objeto raro (%)


class Datos:
    """batdat.us y el ejecutable originales, para leer valores y armar cambios."""

    def __init__(self, iso_path=None):
        iso = Iso(iso_path or iso_paths()[0])
        vol = Volume(iso, 0)
        self.batdat = vol.read(vol.by_path[BATDAT])
        self.exe = iso.read_file(iso.executable)
        self.inicios = inicios(self.batdat)
        b = Batdat(self.batdat)
        self.nombres = {k: decode(b.strings[pos]) for k, pos in b.keys()}
        self.enemigos = [self._enemigo(i) for i in range(CANTIDAD_ENEMIGOS)]

    def leer(self, seccion, pos, ancho):
        datos, base = (self.exe, 0) if seccion < 0 else (self.batdat, self.inicios[seccion])
        return int.from_bytes(datos[base + pos:base + pos + ancho], "little")

    def cambio(self, seccion, pos, ancho, nuevo):
        archivo = EJECUTABLE if seccion < 0 else BATDAT
        return Cambio(archivo, seccion, pos, ancho, self.leer(seccion, pos, ancho), nuevo)

    def _enemigo(self, i):
        p = i * ENEMIGO
        r = self.batdat[self.inicios[ENEMIGOS] + p:self.inicios[ENEMIGOS] + p + ENEMIGO]
        q = self.inicios[RECOMPENSAS] + i * 16
        exp, sp, cp, suelta, rara = struct.unpack_from("<IHHBB", self.batdat, q)
        vida = struct.unpack_from("<I", r, 0x02)[0]
        fuerza, vit, eatk, edef = struct.unpack_from("<4H", r, 0x08)
        numero = struct.unpack_from("<H", r, 0x1E)[0]
        if exp == 0 or (vida, fuerza, vit) == (8000, 100, 50):
            clase = "sin uso"  # ranuras vacías y plantillas sin estadísticas propias
        elif cp > 0 or numero >= 700 or exp >= 20000 or vida >= 20000:
            clase = "jefe"
        elif sp == 0:
            # Los combates con E.S. no dan Puntos de habilidad. Los de mucha vida (Ashmed Bapuz,
            # que es un combate de la historia, O-88 Delphinus, Nova) se tratan como jefes: ante la
            # duda, la Definitive Edition no los toca.
            clase = "común E.S." if vida < 14000 else "jefe"
        else:
            clase = "común"
        return Enemigo(i, self.nombres.get(f"enemigos#{i}", ""), clase, numero, vida, fuerza, vit, eatk, edef,
                       tuple(b for b in r[0x20:0x24] if b), exp, sp, cp, suelta, rara)


def escalar(valor, factor, paso=10, maximo=None):
    """valor × factor redondeado a múltiplos de `paso` (si el valor lo era), nunca menos de 1."""
    if valor == 0:
        return 0
    paso = paso if valor % paso == 0 else 1
    nuevo = max(1, int(valor * factor / paso + 0.5) * paso)
    return min(nuevo, maximo) if maximo else nuevo
