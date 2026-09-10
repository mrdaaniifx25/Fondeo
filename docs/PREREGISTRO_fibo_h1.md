# Preregistro · el pase limpio del fibo en H1

Escrito y sellado **antes** de correr nada de lo que hay aquí dentro.
`RESULTADOS_fibo_h1.md` es exploratorio: barrí 4 temporalidades × 4 fibos × 2
objetivos × 4 instrumentos, más cuatro colchones. Con ese número de celdas
aparecen cosas por azar. Esto es el pase que decide si aquello era real.

## La especificación, congelada

Ni un parámetro se toca después de leer los resultados.

```
  NIVELES   altos y bajos de los 5 días previos
  SWEEP     una vela de H1 se sale del nivel y CIERRA de vuelta dentro
            un solo sweep por nivel y día
  PIERNA    se sigue en H1 desde el cierre del sweep, extremo vivo
            se ARMA cuando la pierna vale 1,0 × el rango de la vela de sweep
  FIBO      F = 0,790 del retroceso, calculado solo con velas ya cerradas
  ENTRADA   limitada en ese nivel, hasta 8 horas después del cierre del sweep
  STOP      0,10 de la pierna pasado el extremo barrido
  OBJETIVO  1:2 fijo
  VIDA      24 horas · empate dentro del minuto = STOP
```

## Lo que este pase NO puede contestar

**No puede volverlo rentable.** La R neta salió negativa en las 128 celdas
exploratorias y la aritmética no cambia: la ventaja bruta medida es de +0,05 R y
el coste vale entre el 6 % y el 21 % del riesgo según el instrumento. Este pase
solo decide **si la ventaja bruta es real o fue el barrido**.

## Prueba 1 · tres instrumentos nunca corridos en H1

XAUUSD, GRXEUR y SPXUSD. Los tres se corrieron con el fibo en M5, nunca en H1.

**Predicción firmada:** R bruta **positiva en los tres**, y en el conjunto el
acierto por encima del 33,3 % geométrico con **z > +1,64**.

## Prueba 2 · otra familia de niveles

Lo mismo pero con **altos y bajos de las 3 semanas previas** en vez de los 5 días,
sobre EURUSD, GBPUSD, USDJPY. Si el efecto es el mecanismo que digo —un precio
que barre un nivel y cierra de vuelta tarda en volver a ese extremo— tiene que
aparecer con cualquier nivel que junte liquidez, no solo con el diario.

**Predicción firmada:** R bruta **positiva en los tres**, con **z > +1,64**.

## El veredicto

- **Las dos pasan** → la ventaja bruta es real. Sigue sin ser rentable, pero es
  lo primero medible del proyecto y merece una tercera prueba con dinero de
  mentira antes que ninguna otra idea.
- **Una sí y otra no** → sospechoso. Se reporta como no concluyente y se cierra.
- **Ninguna** → era el barrido. Se cierra y se escribe que se cerró.

Un solo pase. Se reporta salga lo que salga.

## Lo que ya sé y no cuenta como resultado

Los cuatro instrumentos del barrido (EURUSD +0,055 · GBPUSD +0,100 ·
USDJPY +0,043 · NSXUSD +0,047) y el corte por épocas (+0,075 y +0,053, z +5,04 y
+4,04). Eso es de donde salió la hipótesis; no puede volver a usarse para
confirmarla.
