# Resultados · el stop en el sitio obvio

Pre-registro: `docs/PREREGISTRO_stop.md`, subido en `8d8804d` antes de medir.
Código: `bt/stop_obvio.py`. 20.000 repeticiones por celda, EURUSD.

## La hipótesis es falsa

| N | NIVEL | CONTROL | NIVEL − CONTROL |
|---|---|---|---|
| 10 | 32,12 % | 31,36 % | **+0,76** [−0,23, +1,75] |
| 20 | 30,86 % | 30,70 % | **+0,16** [−0,87, +1,14] |
| 50 | 28,11 % | 26,95 % | **+1,16** [+0,00, +2,29] |

Predije que NIVEL saldría entre 1 y 4 puntos **por debajo** de CONTROL. Sale
**por encima** en los tres. Dos de tres tocan el cero.

**Poner el stop en el máximo o el mínimo obvio no hace que te lo toquen más.**
No hay regla que dar.

## Lo que sí explica el efecto que creí ver

Los dos brazos caen por debajo del azar geométrico: −1,2 y −2,0 con N=10,
−5,2 y −6,4 con N=50. **Los dos igual.** Y el brazo CONTROL tiene las barreras
puestas en sitios cualesquiera, así que eso no puede ser un efecto de nivel.

Es la **convención de medida**: el horizonte de 20 horas, con el agotamiento
contado como pérdida. Cuanto más lejos están las dos barreras, más operaciones
se quedan sin resolver y más cae el acierto por debajo de su precio geométrico.
Con N=50 las barreras están a 10 y 21 pips y la caída es de 6 puntos.

## Lo que esto retira

En `docs/RESULTADOS_ema_sr.md` dejé apuntado que el exceso salía
sistemáticamente por debajo del cero (−1,0 a −1,6 en las ocho celdas) y
propuse que era por tener el stop en el extremo reciente.

**Se retira.** El brazo CONTROL de aquí produce entre −2 y −6 puntos **sin
ningún nivel de por medio**, sólo por el horizonte. Los −1,6 de la regla de la
EMA caben enteros dentro de lo que da la convención sola. No era un hallazgo.

Ya lo dejé marcado allí como «apuntado, no cobrado» por el solapamiento.
Resulta que el problema no era el solapamiento, era el horizonte.

## Balance

Tres cosas medidas, tres resultados:

1. La hipótesis del stop obvio: **falsa**.
2. Mi predicción: **fallada**, y por el signo contrario.
3. Una afirmación anterior mía: **retirada**.

Es la segunda predicción seguida que fallo (la otra,
`docs/RESULTADOS_finta_2025.md`). Las dos veces en la dirección de esperar un
efecto donde no lo había.
