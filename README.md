# Xenosaga Episode II: Definitive Edition

*[Español más abajo](#español)*

> Looking for the **Spanish translation**? It lives at
> [Batnoska/xenosaga2-es](https://github.com/Batnoska/xenosaga2-es). Both projects share the
> same patcher, so you can install either one or both at once.

A fan patch for **Xenosaga Episode II: Jenseits von Gut und Böse** (PS2, NTSC-U) that tackles
what players have criticized the most since 2004: regular battles that drag on forever, slow
progression, skills locked behind Secret Keys and Double Techs that are not worth their cost.
It does not redesign the game: every change is an option, and the original game is always
one click away.

**Status: in development.** Nothing is released yet.

## Profiles and options

The patcher offers four profiles. You can start from any of them and tick or untick each
change on its own.

| Profile | What it does |
|---|---|
| **Original** | The game as released. |
| **Comfort** | Original battles with less grind: more EXP and points, cheaper skills, more item drops and stronger healing. |
| **Definitive** (recommended) | Shorter regular battles with more ways to win, smoother progression, and bosses just as challenging, with Break patterns of three hits at most. |
| **Story** | Everything in Definitive, turned up, plus bosses with less HP. |

| Option | Original | Comfort | Definitive | Story |
|---|---|---|---|---|
| Less HP for regular enemies | | | −40% | −60% |
| Hits that matter (lower regular enemy defense) | | | −20% | −35% |
| Shorter Break patterns (four hits become three) | | | ✓ | ✓ |
| Less HP for bosses | | | | −25% |
| Faster E.S. battles | | | ✓ | ✓ |
| More EXP and points | | ×1.5 | ×1.5 | ×2 |
| Cheaper skills | | −25% | −25% | −50% |
| More item drops | | ✓ | ✓ | ✓ |
| Stronger healing | | ✓ | ✓ | ✓ |

Three more options are still being tested in the game, so no profile includes them; you can
turn them on yourself: **cheaper Double Techs** (one less Stock), **no Secret Keys needed** and a
**debt of 1,000,000**, as in the Japanese release.

The patch works on its own (English) or together with the
[Spanish translation](https://github.com/Batnoska/xenosaga2-es): both come in the same
patcher, and it always starts from your original ISO.

## How it works

Every change is a field edit in the game's battle data (`yamamoto/batdat.us`) or in the
executable, described by section, record and field. Sizes never change, and the same change
fits the English and the Spanish disc. `tools/opciones.py` lists the options and profiles;
`tools/de.py` checks them and builds test ISOs. See `docs/` for the data formats and the
technical plan (in Spanish).

The patcher itself lives in the translation repository (`tools/aplicador`): with both
repositories cloned side by side, its kit reads the options from here and builds both releases.

## Credits

- Patch: Batnoska, with help from Claude.
- Battle data research: [TheSparda/Xenosaga-2-Editor](https://github.com/TheSparda/Xenosaga-2-Editor)
  (MIT): enemy, reward, skill cost and Secret Key tables, and the damage formula.
- ISO and text tools: from the [Spanish translation](https://github.com/Batnoska/xenosaga2-es).

## License

The code and documentation are released under the MIT license ([LICENSE](LICENSE)). The license
does not cover the game or its data; this repository contains none of it.

Xenosaga is a trademark of Bandai Namco Entertainment. This project is not affiliated with
Bandai Namco or Monolith Soft. The patcher window uses the game's logo, promotional art and music
as a tribute; they belong to their owners and are not in this repository.

---

## Español

> ¿Buscas la **traducción al español**? Está en
> [Batnoska/xenosaga2-es](https://github.com/Batnoska/xenosaga2-es). Los dos proyectos usan el
> mismo aplicador, así que puedes instalar uno, el otro o los dos a la vez.

Un parche hecho por fans para **Xenosaga Episode II: Jenseits von Gut und Böse** (PS2,
NTSC-U) que ataca lo que más se le criticó desde 2004: combates comunes eternos, progresión
lenta, habilidades encerradas detrás de Llaves secretas y Técnicas dobles que no valen lo que
cuestan. No rediseña el juego: cada cambio es una opción, y el juego original siempre queda a
un clic.

**Estado: en desarrollo.** Todavía no hay nada publicado.

## Perfiles y opciones

El aplicador ofrece cuatro perfiles. Puedes partir de cualquiera y activar o desactivar cada
cambio por separado.

| Perfil | Qué hace |
|---|---|
| **Original** | El juego tal como salió. |
| **Comodidad** | El combate original, con menos vueltas: más experiencia y puntos, habilidades más baratas, más objetos y curación más fuerte. |
| **Definitiva** (recomendado) | Combates comunes más cortos y con más formas de ganar, progresión más fluida y jefes con el mismo desafío, con patrones de Break de tres golpes como máximo. |
| **Historia** | Todo lo de la Definitiva pero más marcado, y jefes con menos vida. |

| Opción | Original | Comodidad | Definitiva | Historia |
|---|---|---|---|---|
| Enemigos comunes con menos vida | | | −40 % | −60 % |
| Golpes que valen la pena (menos defensa en los comunes) | | | −20 % | −35 % |
| Patrones de Break más cortos (de cuatro golpes a tres) | | | ✓ | ✓ |
| Jefes con menos vida | | | | −25 % |
| Combates con E.S. más ágiles | | | ✓ | ✓ |
| Más experiencia y puntos | | ×1,5 | ×1,5 | ×2 |
| Habilidades más baratas | | −25 % | −25 % | −50 % |
| Más objetos | | ✓ | ✓ | ✓ |
| Curación más fuerte | | ✓ | ✓ | ✓ |

Otras tres opciones todavía se están probando en el juego, así que no vienen en ningún perfil;
puedes activarlas a mano: **Técnicas dobles más baratas** (un Stock menos), **habilidades sin
Llave secreta** y una **deuda de 1.000.000**, como en la versión japonesa.

El parche funciona solo (en inglés) o junto con la
[traducción al español](https://github.com/Batnoska/xenosaga2-es): los dos vienen en el mismo
aplicador, que siempre parte de tu ISO original.

## Cómo funciona

Cada cambio es un campo de los datos de combate del juego (`yamamoto/batdat.us`) o del
ejecutable, descrito por sección, registro y campo. Los tamaños nunca cambian, y el mismo
cambio sirve para el disco en inglés y para el traducido. `tools/opciones.py` tiene las
opciones y los perfiles; `tools/de.py` los comprueba y arma ISO de prueba. En `docs/` están los
formatos de los datos y el plan técnico.

El aplicador está en el repositorio de la traducción (`tools/aplicador`): con los dos
repositorios clonados uno al lado del otro, su kit lee las opciones de acá y arma las dos
versiones.

## Créditos

- Parche: Batnoska, con la ayuda de Claude.
- Investigación de los datos de combate:
  [TheSparda/Xenosaga-2-Editor](https://github.com/TheSparda/Xenosaga-2-Editor) (MIT): tablas de
  enemigos, recompensas, costos de habilidades y Llaves secretas, y la fórmula de daño.
- Herramientas de ISO y textos: de la [traducción al español](https://github.com/Batnoska/xenosaga2-es).

## Licencia

El código y la documentación se publican con la licencia MIT ([LICENSE](LICENSE)). La licencia
no cubre el juego ni sus datos, que no están en este repositorio.

Xenosaga es una marca de Bandai Namco Entertainment. Este proyecto no está afiliado a Bandai
Namco ni a Monolith Soft. La ventana del aplicador usa el logo, imágenes promocionales y música
del juego como homenaje; pertenecen a sus dueños y no están en este repositorio.
