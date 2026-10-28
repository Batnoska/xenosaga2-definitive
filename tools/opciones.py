"""Las opciones de la Definitive Edition, sus textos (español e inglés) y los perfiles.

Cada opción tiene uno o más niveles (nivel 0 = apagada). `cambios(datos, nivel)` devuelve la
lista de Cambio de ese nivel. Dos opciones distintas nunca tocan el mismo campo (lo comprueba
`de.py verificar`), así que se pueden combinar libremente.

Las marcadas como `probada=False` se dedujeron de los datos pero falta verlas funcionar en el
juego: no van en ningún perfil (se activan a mano) hasta que se prueben.
"""
from typing import Callable, NamedTuple

from juego import (COSTOS, CANTIDAD_COSTOS, DEUDA, ENEMIGO, ENEMIGOS, ESPECIALES_ES, ETER, ETER_INICIO,
                   RECOMPENSAS, TECNICAS_DOBLES, escalar)


class Opcion(NamedTuple):
    id: str
    grupo: str
    nombre: dict
    descripcion: dict
    niveles: tuple  # nombre corto de cada nivel ({"es", "en"}); vacío = un solo nivel
    cambios: Callable
    probada: bool = True


class Perfil(NamedTuple):
    id: str
    nombre: dict
    descripcion: dict
    niveles: dict  # id de opción -> nivel; las que no están quedan apagadas


GRUPOS = {
    "combate": {"es": "Combate", "en": "Battle"},
    "progresion": {"es": "Progresión", "en": "Progression"},
    "comodidad": {"es": "Comodidad", "en": "Quality of life"},
}


def _vida(clase, factores):
    def cambios(d, nivel):
        f = factores[nivel - 1]
        return [d.cambio(ENEMIGOS, e.n * ENEMIGO + 0x02, 4, escalar(e.vida, f))
                for e in d.enemigos if e.clase == clase]
    return cambios


def _defensa(d, nivel):
    f = (0.8, 0.65)[nivel - 1]
    out = []
    for e in d.enemigos:
        if e.clase == "común":
            out.append(d.cambio(ENEMIGOS, e.n * ENEMIGO + 0x0A, 2, escalar(e.vitalidad, f, paso=1)))
            out.append(d.cambio(ENEMIGOS, e.n * ENEMIGO + 0x0E, 2, escalar(e.defensa_eter, f, paso=1)))
    return out


def _break_corto(d, nivel):
    # El patrón son cuatro bytes terminados en 0: borrar el cuarto lo deja en tres golpes.
    return [d.cambio(ENEMIGOS, e.n * ENEMIGO + 0x23, 1, 0)
            for e in d.enemigos if e.clase != "sin uso" and len(e.brk) == 4]


def _recompensas(d, nivel):
    f = (1.5, 2)[nivel - 1]
    out = []
    for e in d.enemigos:
        if e.clase == "sin uso":
            continue
        p = e.n * 16
        out.append(d.cambio(RECOMPENSAS, p, 4, escalar(e.experiencia, f)))
        for pos, valor in ((4, e.puntos_habilidad), (6, e.puntos_clase)):
            if valor:
                out.append(d.cambio(RECOMPENSAS, p + pos, 2, escalar(valor, f, maximo=0xFFFF)))
    return out


def _objetos(d, nivel):
    out = []
    for e in d.enemigos:
        if e.clase == "sin uso":
            continue
        if 0 < e.suelta < 100:
            out.append(d.cambio(RECOMPENSAS, e.n * 16 + 8, 1, escalar(e.suelta, 1.5, paso=1, maximo=100)))
        if 0 < e.rara < 100:
            out.append(d.cambio(RECOMPENSAS, e.n * 16 + 9, 1, escalar(e.rara, 2, paso=1, maximo=100)))
    return out


def _costos(d, nivel):
    f = (0.75, 0.5)[nivel - 1]
    return [d.cambio(-1, COSTOS + k * 6 + 2, 2, escalar(d.leer(-1, COSTOS + k * 6 + 2, 2), f))
            for k in range(CANTIDAD_COSTOS)]


def _sin_llaves(d, nivel):
    return [d.cambio(-1, COSTOS + k * 6 + 4, 1, 0)
            for k in range(CANTIDAD_COSTOS) if d.leer(-1, COSTOS + k * 6 + 4, 1)]


def _curacion(d, nivel):
    # Poder de curación en pasos de 5 %: Medica 5 (25 %) pasa a 8 (40 %), Medica 2 de 10 a 15.
    # Revert (categoría 3) revive con poder 5 (25 %) y pasa a 10.
    out = []
    for i in range(57):
        r = ETER_INICIO + i * 32
        categoria, poder = d.leer(ETER, r + 3, 1), d.leer(ETER, r + 0x0A, 2)
        if categoria == 2:
            out.append(d.cambio(ETER, r + 0x0A, 2, escalar(poder, 1.5, paso=1)))
        elif categoria == 3:
            out.append(d.cambio(ETER, r + 0x0A, 2, poder * 2))
    return out


def _dobles(d, nivel):
    out = []
    for i in range(16):
        stock = d.leer(TECNICAS_DOBLES, i * 16 + 0x0A, 2)
        if stock > 1:
            out.append(d.cambio(TECNICAS_DOBLES, i * 16 + 0x0A, 2, stock - 1))
    return out


def _es_agil(d, nivel):
    out = _vida("común E.S.", (0.6,))(d, 1)
    for i in range(21):
        out.append(d.cambio(ESPECIALES_ES, i * 16 + 0x0A, 2, d.leer(ESPECIALES_ES, i * 16 + 0x0A, 2) // 2))
    return out


def _deuda(d, nivel):
    # 10.000.000 = lui a0,0x98 / ori a0,a0,0x9680; 1.000.000 = lui a0,0x0F / ori a0,a0,0x4240
    return [d.cambio(-1, DEUDA, 4, 0x3C04000F), d.cambio(-1, DEUDA + 8, 4, 0x34844240)]


OPCIONES = [
    Opcion("vida_comunes", "combate",
           {"es": "Enemigos comunes con menos vida", "en": "Less HP for regular enemies"},
           {"es": "Los combates comunes terminan antes. El Break sigue siendo la mejor forma de pelear, "
                  "pero hacen falta menos vueltas. Los jefes no cambian.",
            "en": "Regular battles end sooner. Break is still the best way to fight, it just takes fewer "
                  "rounds. Bosses are unchanged."},
           ({"es": "−40 %", "en": "−40%"}, {"es": "−60 %", "en": "−60%"}),
           _vida("común", (0.6, 0.4))),
    Opcion("defensa_comunes", "combate",
           {"es": "Golpes que valen la pena", "en": "Hits that matter"},
           {"es": "Baja la defensa física y de Éter de los enemigos comunes. Los golpes sueltos, el Éter de "
                  "ataque y los fortalecimientos hacen daño de verdad; los combos casi no cambian.",
            "en": "Lowers the physical and Ether defense of regular enemies. Single hits, attack Ether and "
                  "buffs deal real damage; combos barely change."},
           ({"es": "−20 %", "en": "−20%"}, {"es": "−35 %", "en": "−35%"}),
           _defensa),
    Opcion("break_corto", "combate",
           {"es": "Patrones de Break más cortos", "en": "Shorter Break patterns"},
           {"es": "Los enemigos que piden cuatro golpes para el Break (casi todos jefes: Albedo, Margulis, "
                  "el Patriarca...) pasan a pedir tres. Menos margen para equivocarse en medio del Boost.",
            "en": "Enemies whose Break pattern takes four hits (mostly bosses: Albedo, Margulis, the "
                  "Patriarch...) now take three. Less room for error in the middle of a Boost chain."},
           (), _break_corto),
    Opcion("vida_jefes", "combate",
           {"es": "Jefes con menos vida", "en": "Less HP for bosses"},
           {"es": "Los jefes tienen un cuarto menos de vida. Para quien quiere seguir la historia sin "
                  "trabarse.",
            "en": "Bosses have a quarter less HP. For players who want to follow the story without "
                  "getting stuck."},
           ({"es": "−25 %", "en": "−25%"},),
           _vida("jefe", (0.75,))),
    Opcion("es_agil", "combate",
           {"es": "Combates con E.S. más ágiles", "en": "Faster E.S. battles"},
           {"es": "Los enemigos comunes de los combates con E.S. tienen 40 % menos de vida y los especiales "
                  "de los E.S. cuestan la mitad de energía.",
            "en": "Regular enemies in E.S. battles have 40% less HP and E.S. special attacks cost half the "
                  "energy."},
           (), _es_agil),
    Opcion("dobles", "combate",
           {"es": "Técnicas dobles más baratas", "en": "Cheaper Double Techs"},
           {"es": "Cada Técnica doble pide un Stock menos (como mínimo, uno).",
            "en": "Each Double Tech needs one less Stock (one at the least)."},
           (), _dobles, probada=False),
    Opcion("recompensas", "progresion",
           {"es": "Más experiencia y puntos", "en": "More EXP and points"},
           {"es": "Multiplica la experiencia, los Puntos de habilidad y los Puntos de clase que da cada "
                  "combate.",
            "en": "Multiplies the EXP, Skill Points and Class Points from every battle."},
           ({"es": "×1,5", "en": "×1.5"}, {"es": "×2", "en": "×2"}),
           _recompensas),
    Opcion("costos", "progresion",
           {"es": "Habilidades más baratas", "en": "Cheaper skills"},
           {"es": "Baja el costo en Puntos de habilidad de todas las habilidades.",
            "en": "Lowers the Skill Point cost of every skill."},
           ({"es": "−25 %", "en": "−25%"}, {"es": "−50 %", "en": "−50%"}),
           _costos),
    Opcion("sin_llaves", "progresion",
           {"es": "Habilidades sin Llave secreta", "en": "No Secret Keys needed"},
           {"es": "Las 31 habilidades que pedían una Llave secreta (First Combo, Break B10, Combo Boost, "
                  "Overload...) se aprenden sin ella.",
            "en": "The 31 skills that required a Secret Key (First Combo, Break B10, Combo Boost, "
                  "Overload...) can be learned without it."},
           (), _sin_llaves, probada=False),
    Opcion("objetos", "comodidad",
           {"es": "Más objetos", "en": "More item drops"},
           {"es": "Los enemigos sueltan objetos más seguido: la probabilidad del objeto común sube a la "
                  "mitad más y la del raro se duplica.",
            "en": "Enemies drop items more often: regular drop chance ×1.5, rare drop chance ×2."},
           (), _objetos),
    Opcion("curacion", "comodidad",
           {"es": "Curación más fuerte", "en": "Stronger healing"},
           {"es": "Medica, Medica 2 y Medica All curan la mitad más, y Revert revive con 50 % de vida.",
            "en": "Medica, Medica 2 and Medica All heal 50% more, and Revert revives with 50% HP."},
           (), _curacion),
    Opcion("deuda", "comodidad",
           {"es": "Deuda de 1.000.000", "en": "Debt of 1,000,000"},
           {"es": "La deuda de la Campaña SG baja de 10.000.000 a 1.000.000, como en la versión japonesa. "
                  "Vale para partidas en las que todavía no apareció la deuda.",
            "en": "The SG Campaign debt drops from 10,000,000 to 1,000,000, as in the Japanese release. "
                  "Applies to saves where the debt has not appeared yet."},
           (), _deuda, probada=False),
]

POR_ID = {o.id: o for o in OPCIONES}

PERFILES = [
    Perfil("original", {"es": "Original", "en": "Original"},
           {"es": "El juego tal como salió.",
            "en": "The game as released."},
           {}),
    Perfil("comodidad", {"es": "Comodidad", "en": "Comfort"},
           {"es": "El combate original, con menos vueltas: más experiencia y puntos, habilidades más "
                  "baratas, más objetos y curación más fuerte.",
            "en": "Original battles with less grind: more EXP and points, cheaper skills, more item drops "
                  "and stronger healing."},
           {"recompensas": 1, "costos": 1, "objetos": 1, "curacion": 1}),
    Perfil("definitiva", {"es": "Definitiva", "en": "Definitive"},
           {"es": "La que recomendamos. Combates comunes más cortos y con más formas de ganar, progresión "
                  "más fluida y jefes con el mismo desafío, con patrones de Break de tres golpes como "
                  "máximo.",
            "en": "Our recommendation. Shorter regular battles with more ways to win, smoother "
                  "progression, and bosses just as challenging, with Break patterns of three hits at most."},
           {"vida_comunes": 1, "defensa_comunes": 1, "break_corto": 1, "es_agil": 1, "recompensas": 1,
            "costos": 1, "objetos": 1, "curacion": 1}),
    Perfil("historia", {"es": "Historia", "en": "Story"},
           {"es": "Para disfrutar la historia sin trabarse: todo lo de la Definitiva pero más marcado, y "
                  "jefes con menos vida.",
            "en": "To enjoy the story without getting stuck: everything in Definitive, turned up, plus "
                  "bosses with less HP."},
           {"vida_comunes": 2, "defensa_comunes": 2, "break_corto": 1, "vida_jefes": 1, "es_agil": 1,
            "recompensas": 2, "costos": 2, "objetos": 1, "curacion": 1}),
]

POR_PERFIL = {p.id: p for p in PERFILES}


def cambios(datos, niveles):
    """Todos los Cambio de una selección {id de opción: nivel}."""
    out = []
    for o in OPCIONES:
        if niveles.get(o.id):
            out += o.cambios(datos, niveles[o.id])
    return out
