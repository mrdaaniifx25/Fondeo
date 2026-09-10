# Resultados · el pase limpio del fibo en H1

Preregistrado en `docs/PREREGISTRO_fibo_h1.md`, sellado en el commit `4c03192`
antes de correr nada. Un solo pase.

*(Incidencia: la prueba 1 se lanzó la primera vez mientras yo editaba el script
para la prueba 2 y murió con un SyntaxError sin llegar a ejecutarse. Se relanzó
sobre la reserva intacta. No se miró ningún resultado suyo antes de relanzarla.)*

## Las dos pasan

**Prueba 1 · XAUUSD, GRXEUR, SPXUSD, nunca corridos con el fibo en H1**

```
  n = 9.359   ·   acierto 34,5 %   ·   z = +2,41   ·   p = 0,008
  R bruta +0,043  (z +2,94)   ·   positiva en 3 de 3
  R NETA  -0,067
  PASA
```

| | n | acierto | R bruta | R neta | stop |
|---|---|---|---|---|---|
| XAUUSD | 1.963 | 33,5 % | +0,015 | −0,067 | 2,95 $ |
| GRXEUR | 2.253 | 34,5 % | +0,040 | −0,070 | 18,6 pt |
| SPXUSD | 5.143 | 34,9 % | +0,055 | −0,065 | 5,6 pt |

**Prueba 2 · niveles de las 3 semanas previas en vez de los 5 días**

```
  n = 4.158   ·   acierto 35,1 %   ·   z = +2,38   ·   p = 0,009
  R bruta +0,058  (z +2,63)   ·   positiva en 3 de 3
  R NETA  -0,165
  PASA
```

| | n | acierto | R bruta | R neta |
|---|---|---|---|---|
| EURUSD | 1.340 | 36,0 % | +0,084 | −0,176 |
| GBPUSD | 1.545 | 34,7 % | +0,049 | −0,157 |
| USDJPY | 1.273 | 34,6 % | +0,042 | −0,162 |

## Lo que queda establecido

**La ventaja bruta es real.** Seis instrumentos nuevos, dos familias de niveles
distintas, 13.517 operaciones que no participaron en generar la hipótesis, y las
dos predicciones firmadas se cumplen. Es **lo primero en todo el proyecto** que
supera un umbral escrito de antemano sobre datos reservados.

El tamaño es pequeño y consistente en todas las medidas: **entre +0,04 y +0,06 R
por operación**, o sea un acierto de 34-35 % contra el 33,3 % geométrico. Poco más
de un punto y medio.

Y el mecanismo se sostiene: aparece con niveles diarios y con niveles semanales,
o sea que no es una peculiaridad del día. Un precio que barre un nivel de
liquidez y cierra de vuelta tarda en volver a ese extremo.

## Lo que NO cambia

**La R neta es negativa en los seis.** De −0,065 a −0,176.

Y ya está medido por qué, en `RESULTADOS_fibo_h1.md`: la ventaja vive pegada al
stop estrecho —desaparece al ensanchar el colchón— y ese stop estrecho es
justamente el que hace que el coste pese entre el 6 % y el 21 % del riesgo.
**Una ventaja de +0,05 R no paga un coste de 0,065 R.** Está cerca. No llega.

```
  ventaja bruta medida ...........  +0,05 R
  coste más barato medido (SPXUSD)  -0,12 R  -> neta -0,065
  haría falta un coste de ......... < 0,05 R  para quedar en tablas
```

## Qué haría falta para que esto fuera operable

Una de estas dos, y ninguna está en mi mano medirla:

1. **Un coste real por debajo del 5 % del riesgo.** Con stops de 5,6 puntos en
   SPXUSD eso significa menos de 0,28 puntos ida y vuelta. Hay que mirarlo en la
   cuenta, no estimarlo.
2. **Un filtro que suba el 34,5 % al 38-40 %.** No lo tengo: el modelo sobre 17
   variables dio AUC 0,445 fuera de muestra (`RESULTADOS_por_que_no_se_mecaniza.md`).

## Reproducir

`TF=60 COLCHON=0.10 python3 bt/barrido_dia_fibo.py XAUUSD GRXEUR SPXUSD`
`TF=60 COLCHON=0.10 SEMANAS=3 python3 bt/barrido_dia_fibo.py EURUSD GBPUSD USDJPY`
