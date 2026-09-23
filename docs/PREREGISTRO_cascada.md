# Preregistro · la cascada de sesiones

Escrito el 28 de agosto de 2026, antes de ejecutar. Una sola pasada.
Con el arreglo de `docs/CORRECCION_mirada_al_futuro.md` dentro.

## La idea, en sus palabras

> «la sesión de Asia tiene que marcar la sesión de Londres, Londres la de NY y
> así… también hay liquidación en sesiones anteriores y el precio iría a
> buscarlo»

Dos cosas nuevas respecto a todo lo anterior:

1. **Los niveles se acumulan.** No sólo el alto y el mínimo de Asia de hoy: cada
   sesión cerrada deja los suyos, y siguen vivos hasta que el precio los toca.
2. **La escala.** Todo el proyecto se ha hecho en M5, donde un barrido deja
   mechas de 4 pips y el coste de 1,43 se lleva el 30 % del riesgo. En M15 esas
   mechas son tres veces mayores por pura escala.

## Sesiones

Las del indicador del usuario, en hora de Madrid, sin solaparse:

- **Asia**: 00:00 → 08:00
- **Londres**: 08:00 → 14:00
- **Nueva York**: 14:00 → 23:00

De lunes a viernes.

## Los niveles

Al cerrar cada sesión deja **dos niveles pendientes**: su máximo y su mínimo.
Se conservan los de las **10 últimas sesiones cerradas**. Un nivel deja de estar
pendiente en cuanto el precio lo toca — mitigado, y fuera.

## El disparo

Vela de 15 minutos que **barre** un nivel pendiente:

- su mecha atraviesa el nivel, y
- su cierre vuelve al lado de origen (por debajo si era un máximo, por encima si
  era un mínimo).

Entrada **a la contra** al cierre de esa vela: venta si barrió un máximo, compra
si barrió un mínimo.

- **Stop**: 1 pip más allá del extremo de la mecha.
- **Objetivo**: 2 veces el riesgo.
- **Una por día**: la primera. **Horizonte**: hasta las 23:00. **Coste**: 1,43 pips.

## El contraste, uno solo

Suma neta por día en **M15**, 2020-2025.

**Predicción firmada: será positiva.** Un solo contraste con dirección firmada,
umbral |z| >= 1,96.

**Muestra secundaria**: enero-julio de 2026.

## Declarados de antemano como secundarios, para que no sean pesca

1. Lo mismo en **M30**.
2. Objetivo en el **siguiente nivel pendiente** en la dirección de la entrada, en
   vez de a 2R. Es lo que dice su tesis: el precio va a buscar la liquidez.
3. Una por sesión en vez de una por día.
4. Reparto por sesión (Asia, Londres, NY) y por antigüedad del nivel barrido.

## Lo que espero

En M15 el stop pasa de 4-5 pips a 10-14 por escala, así que el coste baja del
30 % al 12 % del riesgo. Si la ventaja bruta que hemos visto una y otra vez
(+0,08 R por operación) se mantiene, el neto debería cruzar el cero. Si no se
mantiene, es que era un efecto de microestructura de M5 y no una propiedad de
los niveles.
