# Datos del juego: qué está dónde (verificado)

Notas técnicas para armar la Definitive Edition. Todo verificado contra las ISO del undub
(NTSC-U) con las herramientas del repositorio de la traducción (`tools/x2iso.py`,
`tools/x2text.py`). Las direcciones de la comunidad
([TheSparda/Xenosaga-2-Editor](https://github.com/TheSparda/Xenosaga-2-Editor), MIT) son de la
ISO americana sin undub; acá están traducidas a archivos y secciones, que es lo que no cambia
entre versiones.

## `yamamoto/batdat.us` (volumen 0)

Archivo de 19 secciones: `u32 cantidad | u32 tamaño total | u32 inicio de cada sección`. La
traducción reescribe los textos de varias secciones y por eso **se corren los inicios de las
secciones 2 a 18**, pero el contenido numérico de cada sección queda igual. Los cambios de la
Definitive Edition se escriben como "sección, registro, campo" y valen para inglés y español.

En la ISO americana, `batdat.us` empieza en 0x1FFF000: una dirección de TheSparda `X` es
`X - 0x1FFF000` dentro del archivo. Sus registros de personajes y enemigos empiezan 0x34 bytes
antes que los nuestros (incluyen la cola del registro anterior): su campo `+N` es nuestro
`+(N - 0x34)`.

### Sección 0: personajes y E.S. (registros de 0x5C)

Orden: chaos, KOS-MOS, Shion, Jin, Ziggy, MOMO, Jr., tres de reserva, E.S. Dinah, Zebulun,
Asher, dos de reserva. Mismo formato que los enemigos.

### Sección 1: enemigos (125 registros de 0x5C, después los nombres)

| Campo | Tipo | Qué es |
|---|---|---|
| +0x00 | u16 | puntero al nombre (relativo a la sección) |
| +0x02 | u32 | vida |
| +0x06 | u16 | 99 en casi todos (11 excepciones) |
| +0x08 | u16 ×4 | fuerza, vitalidad, ataque de Éter, defensa de Éter |
| +0x10 | u8 ×3 | destreza, evasión, agilidad |
| +0x18 | u8 | zonas que se pueden golpear (A 1, B 2, C 4) |
| +0x1C | u8 | tipo (bits 0-1: 0 biológico, 1 Gnosis, 2 máquina) |
| +0x1D | u8 | bit 3: no se puede romper |
| +0x1E | u16 | número de enemigo |
| +0x20 | u8 ×4 | patrón de Break (1 = A, 2 = B, 4 = C; 0 termina) |
| +0x24 | u8 ×8 | afinidades de daño (s8 en pasos de 5 %: 20 = normal, 0 = inmune, negativo = absorbe) |
| +0x38 | u8 ×11 | resistencias a estados (Lentitud +0, Ceguera +2, Pesadez +3, Debilidad +4, ... ) |

Verificado: los nombres, la vida y los patrones coinciden con lo que muestra el juego (Deion
6.560 CB; Patriarca 21.600 BCBB).

Resumen (enemigos con recompensa): 64 comunes a pie (vida mediana 2.400, máx. 14.400), 15
comunes de E.S. (mediana 9.600), 34 jefes (mediana 22.400, máx. 200.000). Patrones: 53 de dos
golpes, 11 de tres, 14 de cuatro (todos jefes: Albedo, Margulis, Patriarca, Dark Erde Kaiser,
Nepos Rigas, Phobos Rigas...), 35 sin Break.

### Sección 2: técnicas, Éter y Éter dobles (registros de 32 bytes)

- Técnicas de cada personaje y de los E.S. desde +0x04 (orden: chaos, KOS-MOS, Shion, Jin,
  Ziggy, MOMO, Jr., Dinah, Zebulun, Asher, especiales de KOS-MOS).
- **Éter**: 57 registros desde **+0x53C4**, en el orden de `eteres#0..56`.
- **Éter dobles**: 29 registros desde **+0x5B24**.

| Campo | Qué es |
|---|---|
| +0x03 | categoría (1 ataque, 2 curación, 4 apoyo, 0 propio) |
| +0x06 | costo de EP |
| +0x08 | u16 elemento (rayo 1, aura 2, trueno 4, fuego 8, hielo 0x10) |
| +0x0A | u16 poder (en curación, cada punto es 5 %: Medica 5 = 25 %, Medica 2 10 = 50 %) |
| +0x12 | probabilidad del efecto |
| +0x13 | tipo de efecto (1 causa, 2 bloquea, 3 fortalece, 4 reduce daño) |

Verificado: Stock 1 cuesta 4 EP y Boost 1, 8; Medica 2 EP, Medica 2 4 EP.

**Sin decodificar**: el bloque de +0x3EC4 (TheSparda lo llama "combos de dos personajes"); no
coincide a simple vista con las 16 Técnicas dobles. Su costo en Stock hay que ubicarlo con el
emulador.

### Sección 12: Técnicas dobles (16 registros de 16 bytes)

`u16 nombre | u16 descripción | 0 0 0 0 | u16 acción (81 a 96) | u16 A | u16 B | u16 C`

- **A vale 2 o 3 (1 en Burst Veil): candidato fuerte a costo en Stock.** Confirmar mirando en el
  juego cuánto Stock pide, por ejemplo, Ice Brand (A = 2) y Power Strike (A = 3).
- B (2 a 7) y C (1 a 7): sin identificar (¿personajes, animación?).
- El poder de cada Técnica doble no está en el bloque de Éter dobles (+0x5B24 de la sección 2):
  los números de acción se repiten entre bloques. Sigue sin ubicar; probablemente en el bloque
  de +0x3EC4 o en las técnicas por personaje.

### Sección 13: especiales de E.S. (registros de 16 bytes)

`u16 nombre | u16 descripción | 0 0 0 0 | u16 acción | u16 costo de energía (100, 200, 300) | u8 0 | u8 elemento`

Sirve para abaratar los especiales de los E.S. (combates con E.S. más ágiles).

### Sección 7: habilidades pasivas (registros de 12 bytes)

| Campo | Qué es |
|---|---|
| +0x00 / +0x02 | punteros a nombre y descripción |
| +0x04 | u32 marcas |
| +0x09 | tipo de efecto (0x08 porcentaje sobre una estadística, 0x02 recuperación, ...) |
| +0x0A | magnitud (Break B10 = 10, Break B15 = 15, HP Mind 10 = 10) |
| +0x0B | máscara de estadística |

**First Combo** (Stock +1 al empezar el combate, #49) y **Combo Boost** (#43) tienen magnitud 0:
su efecto está en el código. Se puede abaratar o desbloquear por datos, no cambiar su valor.

### Sección 15: recompensas (125 filas de 16 bytes, una por enemigo)

| Campo | Qué es |
|---|---|
| +0x00 | u32 experiencia |
| +0x04 | u16 Puntos de habilidad |
| +0x06 | u16 Puntos de clase |
| +0x08 | objetos que suelta (en parte decodificado por TheSparda) |

Solo los jefes dan Puntos de clase (25 de 34). Los comunes de E.S. no dan Puntos de habilidad.
Suma de todos los enemigos una vez: 69.065 Puntos de habilidad y 67.254 de clase.

## Ejecutable (`SLUS_208.92`)

Conversión: código `archivo = va - 0x120000 + 0x1000`; datos `archivo = va - 0x2B5D80 + 0x196D80`.
La traducción modifica el ejecutable en el lugar (textos y algún parche de código), sin correr
nada: las direcciones valen para inglés y español.

### Costos de las habilidades: archivo 0x2CD158 (va 0x3EC158)

112 registros de 6 bytes: `tipo u8 | número u8 | costo u16 | llave u8 | 0`.

- tipo: 2 Éter (50), 1 habilidad equipable (34), 0 automática (28). **El número NO es el índice
  de `batdat.us`**: es el orden dentro de cada tipo según el catálogo de habilidades (ver
  `skill_cost_catalog_index` en el editor de TheSparda). Un cruce ingenuo con los índices de
  `batdat.us` da nombres equivocados.
- llave: **número de Llave secreta** (1 a 31 en 31 habilidades, 0 en el resto). TheSparda lo
  verificó 31 de 31 contra la guía con su correspondencia de números. Lo que falta es ver en el
  juego que ponerlo en 0 quite el requisito.
- **Todo suma 132.950 por personaje.** (TheSparda da 0x35E958 en su ISO; acá está 0x2000 antes.)
- **El orden de la tabla es el del árbol de clases**: cuatro registros por clase, clases A a H,
  niveles 1 a 4 (registros 0-31 nivel 1, 32-63 nivel 2, 64-95 nivel 3, 96-111 nivel 4, que solo
  tiene las clases A a D). Lo confirman las 31 Llaves secretas: cada descripción dice en qué
  nivel y clase está su habilidad ("Lv 3 Class E skill, First Combo") y las 31 caen en la
  posición que da esa cuenta. Si el menú arma el árbol recorriendo la tabla (hay 15 lugares en
  el código que la leen desde el principio), cambiar de lugar dos registros cambia de clase a
  esas dos habilidades, y el precio queda con el lugar. Falta verlo en el juego.

| Llave | Habilidad | Nivel y clase | Costo |
|---|---|---|---|
| 1-4 | Psycho Pocket, Break B10, Focus 1, EP Regen | 1 H | 300, 400, 600, 600 |
| 5-6 | Stock 1, Rare+10 | 2 D | 500, 600 |
| 7 | Junk Beam | 2 F | 500 |
| 8-11 | Boost 1, Expansion Pack, Inner Peace, ST Resist 20 | 2 H | 1200, 1000, 1500, 1200 |
| 12-13 | Safety Level, Limiter Up | 3 A | 1200, 1500 |
| 14-15 | Rapid Refresh, Last Revenge | 3 C | 1000, 1200 |
| 16 | First Combo | 3 E | 1000 |
| 17-18 | Break B15, Rare+30 | 3 F | 1500, 1800 |
| 19 | Ether Burst | 3 G | 1800 |
| 20-23 | Skill Up 10, Experience Up 10, Combo Boost, EP Half | 3 H | 3600 cada una |
| 24 | Curse | 4 A | 4000 |
| 25 | Focus 2 | 4 B | 4800 |
| 26-27 | Overload, ST Double | 4 C | 3600, 2800 |
| 28-31 | Best Ally, Skill Up 15, Experience Up 15, Rebound | 4 D | 9600, 7200, 7200, 8000 |

### Deuda de 10.000.000

Función en va 0x2511A0: `a0 = 10.000.000` (lui 0x98 / ori 0x9680 en 0x2511A4 y 0x2511AC) y salta
a 0x251148. Casi seguro es "fijar la deuda". Cambiarla son dos medias palabras. En la versión
japonesa la deuda era de 1.000.000. Confirmar con el emulador antes de tocar.

(El otro 10.000.000 del ejecutable, en va 0x1F7ADC, es un divisor de otra cuenta.)

## Música y sonido (volumen 0, `sound/`)

- **Música de zonas** (Shinji Hosoe): 31 temas secuenciados en `sound/smf/`, cada uno con
  `.mid` (secuencia), `.vsf` (banco de instrumentos) y `.prj`. Nombres: `001_milchia`
  (Segunda Miltia), `002_milchia2nd`, `003_deepzone`... `101_elsa`, `102_durandal`,
  `103_kukai`, `104_robo_lab`, `105_vector_2nd`, `106_milchia2nd`, `107_home`, `108_UMN_center`,
  `110_cf_quest`, `111_moby-dick`, `201_menu`, `202_UMN`, `203_game_over`. Cambiar el tema de
  una zona = reemplazar estos archivos (el armador de ISO ya maneja cambios de tamaño). La voz
  "a-oh" de Segunda Miltia se podría silenciar editando el `.mid`.
- **Combate**: `sound/adx/battle01.adx`, `battle02.adx`, `boss01.adx`, `boss02.adx`,
  `bosslast.adx`, `fanfale01.adx` (ADX estéreo a 48 kHz, unos 100 s). Intercambiables entre sí;
  uno nuevo requiere codificar ADX (formato simple, se puede programar).
- **Voces de combate**: clips ADX por personaje (`jr_bst1`, `kos_eth1`, `sio_dead`...) y de jefes
  (`bos005_atk1`...). El volumen está grabado en cada clip; en el undub son otros archivos que en
  la versión en inglés, así que normalizarlos pediría un parche por versión.
- **Escenas con el motor**: `sound/adx/cfevent/S-xx-xx-xx/*.adx` en el volumen de cada disco, un
  stream por escena (107 a 267 s). Probablemente con música y voces mezcladas: en esas escenas no
  se puede elegir otro tema.
- Efectos de sonido: `sound/vsf/` (2.086 bancos). Sin investigar.

### Otras pistas

- Generador de números al azar del juego: va 0x2AA130 (TheSparda).
- Fórmula de daño en el overlay de combate (OV01, cargado en 0xA8xxxx): ver
  [DAMAGE.md](https://github.com/TheSparda/Xenosaga-2-Editor/blob/main/Research/DAMAGE.md).
  Break ×1,5 (paso 1), Elevación o Derribo ×2 (paso 2), cadena +10 % por golpe, tope 9.999.
- Textos que hablan de tiendas: solo "Deuda restante" y "Nada para vender" (la pantalla de
  vender de la deuda). **No hay menú de compra sin usar.**
- Códigos de CodeBreaker cifrados (almarsguides) para "los enemigos no te persiguen",
  experiencia y puntos tras el combate: descifrados darían las direcciones del código de
  persecución y del reparto de experiencia.
