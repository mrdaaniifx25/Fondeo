# Pre-registro · segunda baraja ciega, marzo a julio de 2026

**Escrito antes de que el usuario vea un solo corte.** Fecha: 2026-08-28.

## Por qué esta baraja y no capturas

El usuario propuso ir al gráfico y hacer capturas de marzo a julio de 2026,
porque TradingView no le deja repetición intradía. Eso reintroduce exactamente
el problema que él mismo diagnosticó dos mensajes antes: con todas las velas a
la vista, lo que marca es confirmación, no hallazgo. Los datos de EURUSD M1
llegan hasta el 31 de julio de 2026, así que ese periodo se puede cortar bien.

## Qué cambia respecto a la primera baraja

| | v1 | **v2** |
|---|---|---|
| periodo | 2020-2025 | **marzo-julio 2026** |
| cortes | 60 (10 por año, al azar) | **90 — todos los días con setup** |
| qué barrido | el **primero** del día, y si no trae envolvente ese día no hay nada | el **primero que trae envolvente**, aunque no sea el primer barrido |

El segundo cambio es el importante. La v1 pre-seleccionaba con la lectura
estricta, que ya hacía parte del filtrado por él. La v2 usa la lectura laxa
—218 operaciones al año, neta −0,252 en 2020-2025—, es decir, **la población que
peor rinde**. Si su criterio sabe sacar de ahí un subconjunto que no pierde, eso
sí es información.

Un corte por día, nunca dos, para que ninguno enseñe el futuro de otro.
90 cortes: 40 barridos del mínimo, 50 del alto, repartidos 15/20/17/17/21 de
marzo a julio. Los 90 validados uno a uno: 0 incoherencias.

## Lo que ya sé, y que no le digo hasta que responda

**Ya he resuelto la regla mecánica sobre estos 90 cortes.** El resultado está
escrito abajo y comprometido en este mismo commit, para que después pueda
comprobar que no lo he movido.

Contárselo antes cambiaría cuánto pasa —si sabe que el periodo fue malo, pasará
más, y la medición de su criterio se contamina—. Así que se lo digo cuando haya
respondido, no antes.

```
regla mecánica sobre los 90 cortes de la v2:
  n 90 · riesgo mediano 4,7 p · R:R mediano 2,00
  %TP 20,0 %   frente a geometría pura 33,3 %
  bruta −0,089 · neta −0,374 · IC95 [−0,711, −0,037] · z −2,17
```

Esto significa que la v2 **no es una prueba limpia del patrón** —ya lo he
mirado— sino una prueba de **su criterio**, medida como diferencia sobre los
mismos cortes. Esa parte sigue siendo ciega: él no ha visto ninguno.

## La prueba principal: ¿se repite su perfil?

De la v1 salió que elige **barrido corto y vuelta fuerte**, con tres variables a
|z| > 3. Eso fue un hallazgo sobre 60 casos y hay que replicarlo. Es lo que esta
baraja puede medir con potencia de verdad, porque no depende de resultados sino
de sus decisiones, y son 90.

| variable | dirección esperada | umbral |
|---|---|---|
| el barrido cierra pasado el nivel | **menor** en los que opera | |
| mecha pasada el nivel | **menor** en los que opera | z ≥ 2,39 |
| cuerpo de la envolvente | **mayor** en los que opera | (Bonferroni por 3) |

**Se considera replicado** si al menos **2 de las 3** salen con el mismo signo y
z ≥ 2,39. Si no, el perfil de la v1 era ruido y se dice así.

## Las medidas de resultado, y su potencia

1. **Sus entradas** contra cero, en R neta.
2. **Selección**: la regla mecánica sobre los que opera menos la regla sobre los
   que pasa.
3. **Colocación**: sus entradas menos la regla mecánica, emparejado.

Con ~45 operadas y desviación de 1,3 R, el error típico de (2) ronda **±0,28 R**:
sólo detecta efectos de **+0,55 R** para arriba. Igual que en la v1, estas tres
no van a cerrar nada por sí solas. La que decide es la replicación del perfil.

## Umbrales, fijados ahora

- **Perfil replicado** → merece construir el filtro en serio y probarlo en los
  instrumentos sin abrir de `reservado/`.
- **Perfil no replicado** → la familia del barrido de Asia se cierra entera, y
  se cierra bien cerrada: dos barajas, 150 cortes, sin efecto.
- Las medidas 1 a 3 se reportan siempre, con sus intervalos, y **no cambian la
  decisión** salvo que alguna dé z ≥ 2,39 en positivo.

## Lo que espero, dicho antes

Que el perfil **sí** se replique —fue |z| > 3 en tres variables, no es fácil que
sea casualidad— y que las tres medidas de resultado **sigan planas o negativas**,
porque el riesgo mediano de estos cortes es 4,7 pips y 1,2 de spread son el 26 %
del riesgo: haría falta un bruto por encima de +0,26 R sólo para empatar.

Llevo varias predicciones falladas en este proyecto y ésta no vale más que las
otras.

## Ficheros

```
bt/etiquetado_asia.py v2                construye la baraja
docs/etiquetado_asia2.html              la página que ve el usuario
data/etiquetado_asia2_setups.json       lo que se enseña
data/etiquetado_asia2_verdad.csv        fechas y regla mecánica
data/etiquetado_asia2_mecanica.csv      la regla ya resuelta sobre los 90
data/etiquetado_asia2_camino.parquet    el M1 posterior, 19.754 minutos
```
