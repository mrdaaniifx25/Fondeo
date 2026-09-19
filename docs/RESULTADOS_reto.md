# El reto de FundingPips con su perfil real

Monte Carlo, 20.000 simulaciones, remuestreando **sesiones enteras** con
reemplazo —no operaciones sueltas— porque dentro de un día están correlacionadas.

**Parámetros usados** (los estándar de un reto de dos fases; él tiene que
confirmarlos): cuenta 10.000, objetivo 8 % en fase 1 y 5 % en fase 2, pérdida
máxima diaria 5 %, pérdida máxima total 10 %, ambas sobre el saldo inicial, tope
de 60 días por fase.

## Con su perfil medido

| riesgo | pasa fase 1 | revienta | días (mediana) | pasa las dos |
|---|---|---|---|---|
| 0,50 % | 99,9 % | 0,0 % | 17 | 99,9 % |
| **1,00 %** | **99,9 %** | **0,1 %** | **8** | **99,8 %** |
| 1,50 % | 99,1 % | 0,9 % | 6 | 98,3 % |
| **2,00 %** | 83,6 % | **16,4 %** | 4 | 71,7 % |

Con solo los bloques 1 y 2 —quitando el 81 % del tercero— al 1 % sale 97,5 % de
paso y 1,6 % de reventón.

**Estos números son demasiado buenos, y eso es una advertencia, no una buena
noticia.** Salen así porque la entrada es su rendimiento en el simulador. Toda
la simulación es aritmética sobre ese supuesto.

## La tabla que de verdad importa

Misma forma de sesión y mismos stops; lo único que cambia es el acierto que
tendría **en directo**. Riesgo del 1 %.

| acierto en directo | R neta / op | pasa fase 1 | revienta | pasa las dos | al mes |
|---|---|---|---|---|---|
| **65,4 % (lo medido)** | +0,694 | 99,5 % | 0,5 % | 99,1 % | **+1.958 €** |
| 60 % | +0,546 | 99,2 % | 0,7 % | 98,7 % | +1.542 € |
| 55 % | +0,356 | 95,1 % | 3,7 % | 91,5 % | +1.006 € |
| 50 % | +0,178 | 79,2 % | 13,9 % | 67,2 % | +503 € |
| 45 % | +0,106 | 66,9 % | 23,4 % | 51,8 % | +299 € |
| **41,3 % · equilibrio** | ≈ 0 | ≈ 49 % | ≈ 38 % | ≈ 31 % | ≈ 0 € |
| 40 % | −0,042 | 38,8 % | 49,4 % | 20,7 % | −118 € |
| 35 % | −0,202 | 14,1 % | 78,8 % | 3,5 % | −569 € |

**Su punto de equilibrio es el 41,3 %** con su stop mediano de 6 pips. Por
encima gana; por debajo revienta la cuenta más veces de las que la pasa.

## Las dos conclusiones operativas

**1 · Arriesgar el 1 %, no más.** Del 1 % al 2 % la probabilidad de reventar
salta del 0,1 % al 16,4 % y la de pasar las dos fases cae del 99,8 % al 71,7 %.
Es el peor cambio posible: se dobla la velocidad y se multiplica por ciento
sesenta el riesgo de ruina. Al 1 % o menos, el límite diario del 5 % casi nunca
llega a tocarse, porque su peor sesión ronda las cuatro pérdidas seguidas.

**2 · El registro hacia delante ya tiene un objetivo único y concreto: medir su
acierto en directo.** No hace falta contestar nada más. Esa sola cifra, metida en
la tabla de arriba, da todo lo demás.

```
por encima del 50 %  ->  esto es viable
entre 45 y 50 %      ->  gana poco y con sustos
por debajo del 41 %  ->  no
```

## Lo que esta simulación no sabe

- **Los parámetros del reto son los estándar**, no los de FundingPips
  confirmados. Si el drawdown es *trailing* en vez de fijo sobre el inicial, los
  reventones suben.
- **La entrada viene del simulador.** Sin deslizamiento, sin requotes, sin la
  presión de que sea dinero.
- **No modela la pérdida flotante** de una posición abierta contra el límite
  diario, solo el resultado cerrado.
- Supone **21 sesiones al mes** y que sus sesiones son intercambiables: sin
  rachas de mercado, sin aprender, sin cansarse.

## Reproducir

`python3 bt/reto_fundingpips.py`
