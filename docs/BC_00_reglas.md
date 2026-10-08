# Arranque limpio · el método de bctrades como algo nuevo

Decisión del usuario: tratar esto como si no hubiéramos probado nada antes.
Aceptada. Estas son las reglas, escritas antes de recibir el material.

## Qué se resetea de verdad

**1 · La especificación sale solo de su material.** Ninguna regla se elige
«porque antes funcionaba» ni se descarta «porque antes falló». Si ellos anclan
las H4 a una hora, se usa la suya. Si dicen M3, es M3. Mis conclusiones previas
no entran a decidir nada.

**2 · Motor nuevo, escrito de cero.** No se reutiliza `crt_canonico.py` ni
`estrategia_ls.py` ni ningún otro. Esos motores llevan dentro decisiones que
tomé yo y que no son suyas, y arrastrarlas sería seguir donde estábamos con otro
nombre. Todo lo nuevo vive en `bc/`.

**3 · Las ambigüedades se enumeran antes, no después.** Donde su material no
diga algo con claridad, se listan las lecturas posibles **antes de correr nada**
y se reportan **todas**. No se elige la que mejor sale.

**4 · Los criterios se escriben antes de mirar.** Qué sería funcionar, con
número, en un documento con fecha anterior a la primera corrida.

**5 · Una sola pasada.** Sin reajustes, sin «probemos con otro parámetro».

## Lo que NO puedo resetear, y hay que decirlo

**Los datos.** EURUSD y NAS100 de 2020 a 2026 los he mirado muchas veces esta
semana. Eso no se borra: aunque yo no toque nada a propósito, mis manos ya
conocen ese terreno.

Dos protecciones, y ninguna es opcional:

**a · Se reserva 2024-2026, cerrado.** Todo el desarrollo va sobre 2020-2023.
El periodo reciente no se abre hasta que la especificación esté congelada, y se
abre una vez.

**b · Datos vírgenes de verdad.** Lo anterior ayuda pero no es suficiente. Lo
único que sí es un arranque limpio del todo son instrumentos que **nunca he
mirado**. De HistData se pueden bajar gratis y no los tenemos:

```
AUDUSD    USDCAD    USDCHF    EURGBP    NZDUSD    XAUUSD    US30 (DJI)
```

Con dos o tres de esos, la confirmación es genuinamente ciega. Es la diferencia
entre «no he tocado este periodo» y «no he visto nunca este mercado».

## Qué NO significa arrancar de cero

No significa que las mediciones anteriores desaparezcan ni que dejen de ser
ciertas. Siguen en `docs/`, con sus números y sus errores documentados. Lo que
significa es que **no votan**: no deciden qué se prueba, ni cómo, ni qué se
espera. Si esto vuelve a dar lo mismo, será porque lo da otra vez, no porque yo
lo diera por hecho.

Y al revés: si sale distinto, será un resultado que se defiende solo.

## Lo que hace falta del material

Del vídeo de pantalla, por orden de valor:

1. **Publicaciones de operaciones** — instrumento, fecha, dirección. Son las
   únicas que dicen «esto lo operaría yo», que es lo que no puedo deducir.
2. **Reglas que no estén ya transcritas** — lo que haya de horarios, gestión,
   tamaño de posición, cuándo NO operan.
3. **Cualquier cosa donde den un número** — porcentaje de acierto, R:R,
   operaciones por semana. Un número es contrastable; una explicación no.

Lo que ya no hace falta: más explicaciones de qué es un order block, un FVG o
el CRT. De eso hay 32 publicaciones transcritas y no añaden nada.

## Estado

- [x] Reglas escritas
- [ ] Material recibido
- [ ] Especificación redactada solo desde su material
- [ ] Ambigüedades enumeradas
- [ ] Criterios de éxito con número
- [ ] Motor nuevo en `bc/`
- [ ] Una corrida sobre 2020-2023
- [ ] Confirmación sobre 2024-2026 y sobre instrumentos nunca vistos
