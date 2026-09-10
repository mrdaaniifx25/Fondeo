# Preregistro · el mix de CRT y sesiones

Escrito el 29 de agosto de 2026, antes de ejecutar. Una sola pasada.

## Qué se coge de cada uno, y por qué

**Del CRT: la escala y el patrón.** Sus operaciones dejaban stops de 19,3 pips y
el coste sólo se llevaba el 7,8 % del riesgo — el mejor ratio del proyecto. Su
patrón es una vela que barre y cierra de vuelta dentro.

**De las sesiones: los niveles.** El alto y el mínimo de cada sesión cerrada,
acumulados y vivos hasta que el precio los toca.

**La mezcla**: el barrido, pero sobre **velas de H4** y **sólo cuando lo barrido
es un nivel de sesión**.

Esto cae en el único régimen que la aritmética deja abierto:

```
      stop    coste/riesgo   hay que batir al azar en
        5p          28,6 %        9,5 puntos   <- las sesiones en M5, imposible
       20p           7,2 %        2,4 puntos   <- aquí
       50p           2,9 %        1,0 puntos   <- diario, pero sin frecuencia
```

## Especificación

- **Sesiones** (hora de Madrid, sin solaparse): Asia 00:00-08:00, Londres
  08:00-14:00, NY 14:00-23:00. Lunes a viernes.
- **Niveles**: al cerrar cada sesión, su máximo y su mínimo quedan pendientes.
  Se guardan los de las **10 últimas sesiones**. Un nivel muere al ser tocado.
- **Disparo**: vela de **H4** cuya mecha atraviesa un nivel pendiente y cuyo
  cierre vuelve al lado de origen.
- **Entrada** a la contra, al cierre de esa vela de H4.
- **Stop**: 1 punto más allá del extremo de la mecha. **Objetivo**: 2R.
- **Una por día**, la primera. **Horizonte**: 3 días naturales.
- **Coste**: se informa todo en bruto; el neto sólo para EURUSD, con 1,43 pips.

## El contraste, uno solo

**Suma bruta por día agrupando los siete instrumentos**, 2020-2025 (2023-2025 en
oro y DAX, que es lo que hay).

**Predicción firmada: será positiva.**

Agrupar es legítimo porque R no tiene unidades, y evita el problema que nos
comimos en la cascada: encontrar algo en EURUSD y que no replicara. Si el efecto
es estructural, tiene que verse en el conjunto.

Umbral: un solo contraste firmado, |z| >= 1,96.

## Declarados de antemano como secundarios

1. Lo mismo en **H1**.
2. Reparto por instrumento.
3. Reparto por sesión operada y por antigüedad del nivel.
4. Stop mediano y coste de equilibrio de cada instrumento.

## Lo que espero

El stop debería subir de los 5 pips de M5 a la zona de 15-25, que es donde el
coste deja de mandar. Si el barrido de niveles de sesión tiene algo, es aquí
donde tiene que aparecer. Si aquí tampoco, la familia entera está cerrada y lo
diré así.
