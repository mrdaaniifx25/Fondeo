# El CRT, exactamente como se probó

Índice de todo lo medido sobre candle range theory en este repositorio, con las
reglas escritas sin ambigüedad para que se pueda comprobar que se probó lo que
se cree que se probó.

## 1 · La estrategia base, sin adornos

    RANGO          la vela ANTERIOR ya cerrada define el rango: su máximo y su mínimo

    MANIPULACIÓN   la vela actual se lleva uno de los dos extremos
                   Y CIERRA de vuelta dentro del rango
                     · barre el máximo y cierra debajo  ->  VENTA
                     · barre el mínimo y cierra encima  ->  COMPRA
                     · si se lleva los dos, no hay señal

    ENTRADA        al cierre de la vela de manipulación, a mercado
    STOP           el extremo del barrido (el máximo o mínimo de esa vela)
    OBJETIVO       el extremo opuesto del rango
    HORIZONTE      3 velas; si no toca ni stop ni objetivo, se cierra a mercado

Detalles de la ejecución, que son los que hacen que el número sea creíble:

- La resolución es **minuto a minuto** sobre datos M1, no vela a vela.
- Si el stop y el objetivo se tocan dentro del mismo minuto, **cuenta el stop**.
- El coste real medido se resta de cada operación como `coste / riesgo`
  (EURUSD 1,43 pips · GBPUSD 1,60 · USDJPY 1,50 · SPX500 0,60 · NAS100 1,50).
- Nada se filtra a posteriori: entran **todas** las señales del periodo.

Datos: EURUSD, GBPUSD, USDJPY, NAS100, SPX500, GER40 y XAUUSD, M1, 2020-2026.

## 2 · El resultado base, por temporalidad

`RESULTADOS_crt_temporalidad.md` · cinco instrumentos

    TF        n   acierto   riesgo   coste %R   R BRUTA           IC 95 %    R NETA
    H1   47.408    49,4 %      8,1     14,3 %   +0,087   [+0,073, +0,100]   -0,141
    H2   23.180    48,5 %     11,7      9,9 %   +0,132   [+0,057, +0,208]   -0,024
    H4   11.392    47,7 %     17,2      6,7 %   +0,075   [+0,046, +0,103]   -0,030
    H6    6.973    47,5 %     21,1      5,4 %   +0,065   [+0,030, +0,100]   -0,017
    H8    4.930    46,6 %     25,3      4,6 %   +0,064   [+0,022, +0,106]   -0,006
    H12   3.108    46,1 %     32,5      3,4 %   +0,125   [+0,064, +0,185]   +0,072
    D1    1.952    47,2 %     47,7      2,3 %   +0,042   [-0,017, +0,101]   +0,009

**Hay ventaja bruta real y es la misma en todas las temporalidades**
(prueba de heterogeneidad Q = 7,75 con 6 grados de libertad; media ponderada
**+0,082 R**). Lo que cambia es el coste, que sólo baja del 4 % del riesgo en
H12 y D1.

Ése es el mejor número del proyecto y el punto de partida de todo lo demás.

## 3 · Todas las variantes probadas

| variante | qué se cambió | resultado |
|---|---|---|
| `crt_canonico` | rejilla anclada, entrada en la Vela 3, orden stop | negativo |
| `crt_invertido` | la señal **al revés** | también pierde (−0,020 contra −0,075) |
| `crt_fib` | entrada en retroceso en vez de al cierre | mejora y no basta: 13 de 14 celdas siguen sin ganar |
| `crt_confluencias` | confluencia con marcos superiores | el producto se queda en cero |
| `crt_semanal` | filtro de dirección semanal | **empeora** en los tres instrumentos |
| `crt_cascada` | objetivo semanal, cascada D1→H4→H1→M15 | objetivo tocado 1,92 % contra 3,19 % de azar |
| `crt_sesion` | rango dinámico por sesión (SmartRisk) | el control de detección **gana al modelo** |
| `crt_9am` | ancla horaria fija 08:00 H1 + 09:00 M15 | acierto 37,3 % contra 37,4 % geométrico |
| `crt_m15_m1` | ejecución M15/M1, sesión de Londres | ruido |
| `crt_anatomia` | 4 propiedades del propio rango | ninguna discrimina |
| `crt_objetivo_pendiente` | objetivo superior sin cumplir | la mejor idea, y aun así p = 0,20 |
| `crt_solucion` | la anterior, **fuera de muestra**, 12 variantes | las 12 pierden |
| `crt_tf_partido` | corte temporal por temporalidad | sólo H12 aguanta, débilmente |
| `crt_final` | todo lo que sobrevivió, 24 celdas, fuera de muestra | **las 24 negativas** |
| `crt_que_diferencia` | FVG, order block, patrón de vela: 30 variables y un modelo | no las separa |

## 4 · Las tres razones por las que muere

**1 · El coste.** La ventaja bruta es +0,082 R. El coste en R es
`coste_fijo / riesgo`. Para que empate hace falta un stop de **17,4 pips como
mínimo** en EURUSD. Por debajo de eso, la aritmética la mata sin importar el
patrón.

**2 · Se está apagando.** Partiendo 2020-2023 contra 2024-2026, **21 de 24
celdas bajan** (prueba de signos p ≈ 0,0002). El +0,082 de 2020-2023 no sigue
vigente.

**3 · Nada distingue al ganador.** 19.553 setups, 30 variables —incluyendo FVG,
order block y patrón de vela— y un modelo con validación hacia delante: el
mejor quintil que sabe elegir **sigue perdiendo** 0,0676 R.

## 5 · Y por qué se ve un ganador cada día

`crt_cuantos_al_dia.py` · EURUSD

    marco   señales   al día   ganan   pierden   días con ≥1 ganador   suma neta
      M15     38460     19,3   48,6 %   51,4 %         95,8 %          -14.165 R
       H1     13397      6,9   42,9 %   57,1 %         93,7 %           -3.582 R
       H4      3448      2,0   42,4 %   57,6 %         65,0 %             -418 R
      H12      1260      1,2   42,5 %   57,5 %         48,3 %              -20 R

**El 96 % de los días tiene al menos un CRT ganador y el 87 % tiene tres o
más.** Eso es cierto y no contradice nada: ese mismo día hubo 19 setups y
perdieron 10. El ganador deja una vela grande que salta a la vista; los diez
perdedores no dejan ninguna huella visual.

## 6 · Lo que NO se ha probado

Para que el índice sea honesto:

- **Marcos por encima de D1** (semanal, mensual) como temporalidad de ejecución:
  no hay muestra suficiente en 6,5 años.
- **Criterio discrecional**: elegir a mano cuál de los 19 setups del día tomar.
  Eso no es medible desde un backtest — está el modo a ciegas del simulador
  (`simulador_crt.html`) para que lo mida quien opera.
- **Instrumentos fuera de los siete**: acciones, cripto, bonos.
- **Costes distintos de los medidos**: con un coste sustancialmente menor al de
  un CFD retail, H1 y H2 volverían a estar en juego.
