# Plan técnico

Cómo encaja la Definitive Edition en lo que ya tenemos: un solo aplicador con dos casillas
("Traducción al español" y "Definitive Edition") que siempre parte de la ISO original.

## Decisiones (2026-10-28)

- **Perfiles y opciones sueltas**, como el instalador del Perfect Works de Xenogears: cuatro
  perfiles (Original, Comodidad, Definitiva, Historia) con una explicación corta cada uno, y
  cada cambio se puede activar o desactivar. Si se toca algo, el perfil pasa a "Personalizada".
- Textos en inglés y en español (el aplicador sigue el idioma de Windows).
- Sin guía ni glosario.
- Crédito a TheSparda y a cualquier herramienta que usemos; sin pedir colaboración.
- La música no se toca por ahora.
- Las imposibles quedan afuera.

## Los cambios, como datos (hecho)

`tools/opciones.py` describe cada opción: nombre y descripción en los dos idiomas, sus niveles
(por ejemplo −40 % y −60 %) y una función que arma la lista de cambios a partir del juego
original. Cada cambio es `archivo, sección, posición, original, nuevo`:

- en `batdat.us`, la posición es relativa al inicio de la sección, que se lee del propio
  archivo: el mismo cambio vale para el disco en inglés y para el traducido;
- en el ejecutable, la posición es absoluta: las tablas están en el mismo lugar en los dos
  discos (`SLUS_208.92` y `SLUS_211.33`), y la traducción no corre nada.

Ningún cambio altera tamaños, y **dos opciones distintas nunca tocan el mismo byte**
(`python tools/de.py verificar`). Por eso no hace falta guardar una variante por combinación:
el aplicador aplica los cambios de las opciones elegidas encima del archivo original o del
traducido, comprobando cada valor original antes de escribir.

## El kit y el aplicador (hecho, en el repositorio de la traducción)

1. `tools/parche.py crear` importa `opciones.py` desde esta carpeta (junto a la de la traducción,
   o la de `X2_DEFINITIVA`) y guarda en el paquete `de.tsv`: los grupos, las opciones con sus
   textos y niveles, los perfiles y los cambios de cada nivel. Sin esta carpeta, el paquete sale
   sin la Definitive Edition y el aplicador no muestra su casilla.
2. El aplicador (C#, `Aplicador.cs`, y Python, `parche.py aplicar`) aplica los cambios elegidos
   a `batdat.us` y al ejecutable después de la traducción, o sobre el original si la traducción
   está apagada, o sobre una ISO ya traducida con la versión actual. Si un valor original no
   coincide, se detiene: la ISO no es la que esperamos. La ventana (`Ventana.cs`) tiene la
   pantalla de configuración del boceto.
3. `kit.py --probar` compara el `.exe` con la versión en Python en tres casos: disco 1 con
   traducción e Historia, disco 2 solo con Definitiva, y una ISO ya traducida más Comodidad.
4. El mismo código se compila dos veces, una por repositorio (`kit.py VERSION --de VERSION_DE`). Cambian dos cosas: qué casilla
   va primero y marcada, y la marca (barra de título, botón, texto que se desliza y créditos;
   ver `boceto3_ingles.png`).
5. **Selector ES / EN** en la barra de título, junto a minimizar y cerrar, con las banderas de
   Argentina (la traducción es en español latinoamericano neutro) y de Estados Unidos, pasadas
   por el filtro de la ventana (tono azul noche y cian, líneas de barrido). Arranca en el idioma
   de Windows (español si Windows está en español, inglés en cualquier otro caso) y cambia todos
   los textos de la ventana en el momento, también los de la configuración.
   **"Más allá del bien y del mal"**: el subtítulo alemán del logo ("Jenseits von Gut und Böse")
   se dibuja aparte, en Garamond espaciada, debajo del logo (`boceto3_frase.png`). Si la
   traducción está marcada, mientras se aplica cada letra se va descifrando al español en un
   momento al azar ligado al avance (las que faltan titilan como símbolos cian). Al terminar,
   destello, un sonido y la frase queda en español con brillo y remates a los costados,
   latiendo con la gema. Sin la traducción, queda en alemán.
6. **Enlaces cruzados**: cada README apunta al otro repositorio (ya están puestos; el de la
   traducción apunta a `Batnoska/xenosaga2-definitive`, que todavía no existe).

## Probar en el juego

`python tools/de.py iso definitiva ENTRADA SALIDA` copia una ISO (original o traducida, de
cualquier disco) y le aplica un perfil, con ajustes opcionales (`deuda=0`, `vida_comunes=2`...).

Falta confirmar en el juego. Las tres están marcadas "en prueba" y no van en ningún perfil
hasta que se confirmen (`de.py verificar` lo controla); se pueden activar a mano:

- **Técnicas dobles**: que el campo A de la sección 12 sea el costo en Stock. Ice Brand pide 2
  en el original; con la opción debería pedir 1.
- **Llaves secretas**: que poner la llave en 0 libere la habilidad (por ejemplo First Combo,
  que pide la Llave secreta 16).
- **Deuda**: que la función de 0x2511A0 sea la que fija la deuda. Solo se nota en una partida en
  la que todavía no apareció.

## Fase 2 (código): cómo encararla

1. **Análisis estático primero**: desensamblar el ejecutable y los overlays (`OV01.OVL` es el
   combate) y ubicar el código por constantes y por las direcciones que ya dejó TheSparda y
   los códigos de CodeBreaker. Lo hago yo sin necesidad del emulador.
2. **ISO de prueba por cada cambio** para que lo pruebes jugando, que es lo que mejor sabe si
   algo se siente bien.
3. **Depurador de PCSX2** solo cuando lo estático no alcance (por ejemplo, para ver qué
   función lee un dato). Ahí puedo manejar el emulador desde el escritorio, con tu permiso, o
   te paso los pasos.
