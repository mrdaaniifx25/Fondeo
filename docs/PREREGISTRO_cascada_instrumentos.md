# Preregistro · la cascada en otros instrumentos

Escrito el 29 de agosto de 2026, antes de ejecutar. Una sola pasada.

## La pregunta

La cascada de sesiones tiene ventaja bruta medida en EURUSD (+0,096 R por
operación, z +2,53 sobre 1.421 operaciones) y no llega a neto porque el stop
natural del barrido son 5,2 pips y operar cuesta 1,43.

**La ventaja está en R, que no tiene unidades. El coste está en pips, que sí.**
Así que la misma ventaja en un instrumento cuyo barrido deje stops mucho mayores
respecto a su spread sí cabría.

## Especificación

Exactamente el mismo código de `bt/cascada.py`, sin tocar nada: sesiones de
Asia, Londres y NY en hora de Madrid, niveles acumulados de las 10 últimas
sesiones, barrido en M15, entrada a la contra, stop a 1 punto de la mecha,
objetivo 2R, una por día, horizonte hasta las 23:00.

**Instrumentos**: GBPUSD, USDJPY, XAUUSD, GRXEUR (DAX), NSXUSD (Nasdaq),
SPXUSD (S&P 500). EURUSD ya está hecho y sirve de referencia.

## Qué se informa

Para cada instrumento, en **bruto** y sin suponer ningún coste:

- número de operaciones, acierto, R bruta por operación y su z por día
- **stop mediano en las unidades del propio instrumento**
- **el coste de equilibrio en esas unidades**: cuánto puede costar operar antes
  de que la ventaja se agote

El coste real de cada instrumento lo tiene que poner él, con su bróker. Yo no
me lo invento.

## Contraste

Uno por instrumento sobre la R bruta por día, dirección firmada positiva.
Seis instrumentos, Bonferroni pide |z| >= 2,64.

## Lo que espero

Que el acierto ronde el mismo 34-36 % en todos, porque el efecto parece
estructural. Y que el coste de equilibrio sea mucho mayor en los índices, donde
un barrido deja decenas de puntos y el spread es de uno o dos.
