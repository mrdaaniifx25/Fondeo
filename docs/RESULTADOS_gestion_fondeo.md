# Resultado · la gestión de riesgo del vídeo de fondeo

Pre-registro: `docs/PREREGISTRO_gestion_fondeo.md`. Código: `bt/gestion_fondeo.py`.
**200.000 carreras por celda.** Dos formatos: futuros 50k (DD 4 % desde el pico,
objetivo 6 %) y forex 10k en dos fases (DD 10 %, +8 % y +5 %). Coste 0,10 R.

---

## 1 · Su tesis es CORRECTA, y me quedé muy corto

A **igual esperanza** (+0,10 R por operación), variando sólo el reparto entre
acierto y R:R, forex 10k dos fases:

```
    R:R  acierto   riesgo 0,5 %   1,0 %    1,5 %    2,5 %
    0,5    80,0%        99,9%    96,3%    87,5%    72,4%
    1,0    60,0%        92,5%    70,7%    58,7%    49,2%
    2,0    40,0%        66,6%    48,1%    42,8%    35,4%
    3,0    30,0%        53,6%    40,4%    37,4%    30,4%
    5,0    20,0%        42,4%    34,3%    33,1%    26,9%
```

**La misma rentabilidad aprueba el 99,9 % con R:R 0,5 y el 42,4 % con R:R 5.**
Cincuenta y siete puntos de diferencia por una decisión que no cambia un euro de
la esperanza.

Yo firmé «entre 10 y 25 puntos». Son **57**. Me quedé corto por más del doble, y
su afirmación es más fuerte de lo que yo creía.

**Y con ventaja, arriesgar menos siempre gana**: 0,5 % bate a 2,5 % en las cinco
filas. Sus conclusiones 2, 3 y 4 son correctas *si hay ventaja*.

## 2 · PRINCIPAL · a esperanza cero se invierte, pero sólo en un formato

```
  futuros 50k (DD 4 %, objetivo 6 %)
    R:R  acierto    0,25 %    0,50 %    1,00 %    1,50 %    2,50 %    4,00 %
    1,0    55,0%     23,6%     24,8%     27,4%     30,5%     35,8%     30,4%
    2,0    36,7%     23,8%     24,9%     27,4%     29,5%     33,2%     36,7%
    3,0    27,5%     24,0%     25,6%     27,2%     30,1%     36,9%     27,7%

  forex 10k 2 fases (DD 10 %, 8+5 %)
    1,0    55,0%     27,3%     27,8%     28,1%     28,3%     29,5%     30,6%
    2,0    36,7%     27,3%     27,2%     27,2%     28,2%     26,2%     27,1%
    3,0    27,5%     27,1%     26,7%     26,9%     27,3%     24,4%     27,1%
```

**En futuros mi predicción se cumple: sin ventaja, arriesgar más aprueba más.**
De 23,6 % al 0,25 % a **35,8 % al 2,5 %**. Doce puntos por arriesgar diez veces
más, con esperanza cero. El motivo es el coste: se paga **por operación**, así
que menos tamaño significa más operaciones y más horquilla pagada por el mismo
recorrido.

**En forex dos fases el efecto casi desaparece** (27,3 % → 29,5 %). El colchón
del 10 % y el reinicio del saldo en la fase 2 hacen la geometría mucho más
indulgente.

Así que mi predicción sale **a medias**: el signo es correcto, la magnitud
depende del formato y en el que él recomienda es pequeña.

## 3 · Qué esperanza hace falta para aprobar la mitad de las veces

Con su regla del 1,5 % de riesgo:

```
  futuros 50k     R:R 1,0  ->  +0,129 R  (61,4 % de acierto)
                  R:R 2,0  ->  +0,277 R  (45,9 %)
                  R:R 3,0  ->  +0,391 R  (37,3 %)

  forex 10k 2 f.  R:R 1,0  ->  +0,071 R  (58,6 % de acierto)
                  R:R 2,0  ->  +0,147 R  (41,6 %)
                  R:R 3,0  ->  +0,221 R  (33,0 %)
```

**La mejor configuración medida en todo este proyecto da −0,021 R**
(`RESULTADOS_su_patron.md`). Para aprobar la mitad de las veces con R:R 2 harían
falta **+0,147**. La distancia es de **0,168 R por operación**.

## 4 · Y aquí está lo que de verdad enseña este ejercicio

Reproduciendo su propio embudo, con riesgo del 1,5 % y R:R 2:

```
      esperanza   acierto   pasan fase 1   se fondean
          -0,10     33,3%          33,6%        16,2%
          -0,05     35,0%          40,0%        21,8%
          +0,00     36,7%          46,9%        28,3%
          +0,05     38,3%          53,3%        35,1%
          +0,10     40,0%          60,2%        42,7%
  ------------------------------------------------------
  REAL (My Forex Funds)                10,0 %         2,4 %
```

**Incluso con una estrategia claramente perdedora (−0,10 R), arriesgando el
1,5 % con disciplina, se fondearía el 16,2 %. La realidad es el 2,4 %.**

Esa diferencia —de 2,4 % a 16-28 %— **no la explica la falta de ventaja. La
explica la gestión del riesgo.** Sobredimensionar, vengarse tras una pérdida,
saltarse el límite diario, doblar para recuperar.

**Es exactamente lo que el vídeo sostiene, y mi simulación lo confirma.** Si todo
el mundo siguiera sus cuatro reglas, la tasa de fondeo se multiplicaría por seis
o por diez **sin que nadie mejorara su estrategia ni un punto**.

## 5 · Pero fondearse no es cobrar

El embudo tiene un último escalón que la simulación de arriba no modela:

```
  de 2.400 fondeados  ->  72 retiran  =  3,0 %
```

**Pasar un examen es un problema de varianza. Retirar todos los meses es un
problema de esperanza.** Y son dos cosas distintas:

- Para **pasar** no hace falta ventaja: basta con no reventar antes de que el
  azar te ponga por delante. El 28,3 % de la tabla con esperanza cero lo dice.
- Para **retirar** hace falta ventaja, porque hay que repetirlo mes tras mes y
  la varianza deja de ayudar.

**Ahí está el error de su frase fundacional.** *«Al beneficio vas a terminar
llegando sí o sí»* es verdad para un examen —es una barrera, y las barreras se
tocan— y es falso para cobrar todos los meses.

## 6 · Mis predicciones firmadas

| firmé | salió | |
|---|---|---|
| su tesis correcta, diferencia de 10-25 pp | correcta, **57 pp** | ✔ y corto |
| a esperanza cero gana el riesgo grande | **sí en futuros** (+12 pp), apenas en forex | ✔/✘ |
| esperanza necesaria entre 0,05 y 0,15 R | +0,071 a **+0,391** según R:R | ✘ |

## Veredicto

**El vídeo es correcto en casi todo y su consejo es bueno.** Es el único material
que ha llegado a este proyecto del que puedo decir eso.

Lo que le falta es separar dos preguntas que mezcla:

1. **«¿Por qué sólo se fondean 2.400 de 100.000?»** → Su respuesta (gestión de
   riesgo) es **correcta**, y mi simulación la respalda: con disciplina sería el
   16-28 % incluso sin ventaja.
2. **«¿Por qué sólo retiran 72?»** → Aquí su respuesta no vale. Retirar exige
   esperanza positiva sostenida, y eso no lo arregla ningún tamaño de posición.

Él usa el primer número para vender la solución del segundo problema.
