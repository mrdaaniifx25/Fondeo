# Preregistro · el COT de la CFTC como predictor

**Sellado ANTES de tener los datos.** El proxy de la sesión deniega
`cftc.gov` por política (403 en el CONNECT), así que estas hipótesis se
escriben sin haber visto ni una fila. Es la versión más fuerte posible de la
disciplina: no puedo haberlas ajustado a nada.

## Qué es el dato

El *Commitments of Traders* de la CFTC. Posicionamiento **real** de los
participantes en los futuros, publicado por el regulador. No es precio: es
quién está posicionado y cómo.

    informe legacy, futuros solamente:
      Non-Commercial     grandes especuladores (fondos, CTAs)
      Commercial         coberturistas (los que usan el subyacente)
      Non-Reportable     pequeños, por debajo del umbral de declaración

Publicación: **viernes a las 15:30 ET, con datos del martes anterior.**
Tres días de retraso. Ahí es donde hacen trampa casi todos los backtests de
COT que circulan: usan el dato del martes el propio martes.

## Contratos y precios que cruzaría

    Euro FX (CME)          <-> data/eurusd_m1.parquet
    British Pound (CME)    <-> data/gbpusd_m1.parquet
    Japanese Yen (CME)     <-> data/usdjpy_m1.parquet
    Gold (COMEX)           <-> data/xauusd_m1.parquet

Cuatro instrumentos = una réplica de verdad, no una sola prueba.

## Las cuatro hipótesis, firmadas

Variable: posición **neta** de cada grupo, normalizada como z-score sobre una
ventana móvil de 156 semanas (3 años), usando SOLO datos anteriores.
Retorno a medir: 1, 4 y 12 semanas desde el **cierre del viernes de
publicación**, nunca desde el martes.

1. **El neto de los Non-Commercial predice NEGATIVAMENTE** el retorno
   posterior. Es la creencia clásica: cuando los especuladores están muy
   largos, el movimiento ya ocurrió. Predigo signo negativo.

2. **El neto de los Commercial predice POSITIVAMENTE.** Son los informados.
   Signo contrario al de los especuladores por construcción contable, así que
   esta hipótesis y la 1 son casi la misma medida con el signo cambiado; se
   publican las dos para que se vea.

3. **El CAMBIO semanal de posicionamiento predice mejor que el NIVEL.**

4. **Los extremos (decil superior e inferior del z-score) predicen más fuerte
   que el centro de la distribución.**

## El criterio de éxito

Operable solo si cumple **las cuatro**:

    1  z > 2 en la regresión predictiva agrupada de los 4 instrumentos
    2  MISMO SIGNO en al menos 3 de los 4 instrumentos por separado
    3  el signo se mantiene en los tres horizontes (1, 4 y 12 semanas)
    4  sobrevive al retraso de publicación de 3 días

Con nulo al lado: las mismas series de posicionamiento, desplazadas
aleatoriamente en el tiempo, 5 repeticiones.

## Mi predicción, dicha antes

La evidencia académica sobre el COT es **mixta**, y en divisas más débil que
en materias primas. Espero:

- que la hipótesis 1 salga con el **signo correcto pero z por debajo de 2**
- que la 3 **falle**: el nivel y el cambio darán parecido
- que la 4 **acierte**: los extremos dirán algo más que el centro

Y espero que el conjunto **no supere el criterio**, porque si el COT
funcionara de forma sencilla sobre un dato público y gratuito con 20 años de
historia, ya no funcionaría.

## Lo que hace falta para ejecutarlo

Un fichero que yo no puedo descargar. Instrucciones en el propio documento de
resultados cuando llegue.
