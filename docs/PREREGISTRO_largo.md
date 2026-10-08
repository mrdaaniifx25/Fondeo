# Pre-registro · horizonte largo, muchos mercados

Escrito y subido ANTES de medir. 20/09/2026.

## Por qué aquí

`docs/RESULTADOS_muro_horizonte.md`: el coste es fijo por operación y el ruido
crece con la raíz del tiempo, así que la ventaja mínima para empatar cae de
0,1076 del ruido (EURUSD, 1 hora) a 0,0007 (DAX, 1 mes). **Es la primera vía
del proyecto que no está derrotada por el coste antes de empezar.**

## Qué se mide

El efecto más replicado que hay en la literatura: **momento en series
temporales**. Si lo que ha subido los últimos K periodos sigue subiendo el
siguiente.

- Barras **semanales** y **mensuales**, construidas desde M1.
- Señal: `signo(cierre[t] − cierre[t−K])`, con K = 1, 3, 6, 12 barras.
- Se mantiene **una barra**.
- Medida: `media(señal × rendimiento siguiente) / σ(rendimiento)`.
  En unidades de ruido, para poder comparar con el coste y entre instrumentos.
- Se juntan los tres instrumentos, que es donde está la poca potencia que hay.

**Nulo**: signos barajados.

## La potencia, declarada antes que nada

Éste es el problema y va por delante del resultado:

| | barras disponibles |
|---|---|
| EURUSD (2021-2026, faltan 2020 y 2025) | ~230 semanas · ~54 meses |
| oro (2023-2026) | ~180 semanas · ~42 meses |
| DAX (2023-2026) | ~180 semanas · ~42 meses |

Juntando: ~590 semanas y ~138 meses. Los efectos de momento que se publican
andan por 0,04-0,07 de ruido por semana. Con 590 semanas, el efecto más pequeño
que se puede distinguir del cero ronda **0,08**. O sea: **esta muestra está por
debajo de lo que haría falta.** El resultado más probable no es «sí» ni «no»,
es **«no se puede saber»**, y eso hay que decirlo como resultado y no
disfrazarlo.

## Criterio

1. efecto > coste/ruido de ese horizonte, con el IC95 sin tocar el cero, **y**
2. mismo signo en al menos 2 de los 3 instrumentos, **y**
3. el nulo en cero.

Si el IC contiene el cero y además contiene el tamaño típico del efecto
publicado, la conclusión es **«hacen falta más datos»**, no «no hay efecto».
Esa distinción es el punto entero de este pre-registro.

## Predicción

- El signo del efecto: **positivo**, porque es de las cosas más replicadas que
  existen. Pero el IC lo bastante ancho como para no cumplir el criterio 1.
- Conclusión esperada: «no se puede saber con estos datos», y una cuenta de
  cuántos años de histórico harían falta para saberlo.
