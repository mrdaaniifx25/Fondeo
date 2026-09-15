# Pre-registro · la regla del usuario, escrita por él y verificada

**Escrito antes de correr una sola línea sobre el histórico.** Fecha: 2026-08-28.

## De dónde sale

No de un backtest ni de un vídeo: de **sus dieciséis explicaciones escritas caso
por caso** en agosto de 2026, más la verificación mecánica de que el gatillo se
cumple en las 16 de 16 (`docs/REGLA_asia_nivel.md`).

Es la primera vez en el proyecto que la hipótesis viene de su operativa real y no
al revés.

## La regla, cerrada

```
INSTRUMENTO  EURUSD, velas de M5 en hora de Madrid
NIVELES      el alto y el mínimo de Asia (00:00 - 08:00)
VENTANA      08:00 - 11:30

ARMADO       cada nivel empieza armado.
             Dispara como mucho una vez por visita: tras disparar se desarma,
             y se rearma cuando el precio se aleja más de 10 pips del nivel.

DISPARO      una vela de M5 que TOCA el nivel (su rango lo contiene) y además
             cumple A o B:
  A   su CUERPO entero queda a un lado del nivel y la vela va en ese sentido
  B   cierra más allá del CUERPO de la última vela contraria (hasta 10 atrás),
      yendo en ese sentido

DIRECCIÓN    la que marca esa vela. No se elige nunca.
ENTRADA      al cierre de esa vela
STOP         el extremo de la vela ANTERIOR a la de entrada
OBJETIVO     1:2 fijo desde la entrada
SALIDA       corre hasta objetivo o stop, sin cerrar a las 14:00.
             Horizonte máximo: cierre de NY, 22:00
```

Sin reentradas. La reentrada que él describe —si a las dos velas el precio se da
la vuelta, entra al contrario— se reporta **como variante secundaria**, no como
prueba principal.

## Dónde se prueba

| conjunto | qué es |
|---|---|
| **2020-2025** | prueba principal. Seis años. La regla no se ha corrido nunca |
| 2026 ene-jul | secundaria |
| agosto 2026 | **excluido**: es de donde sale la regla |

Coste: **1,2 pips** de diferencial sobre el riesgo, como en todo el proyecto.

## Qué se mide y qué decide

Unidad de análisis: **el día**, no la operación. Salen 1,1 disparos por mañana y
las del mismo día no son independientes.

- **Principal:** R neta media por día, contra cero.
- Acierto observado contra la geometría de un 1:2, que es **33,3 %**.
- Coste de equilibrio `c* = media(R) / media(1/riesgo)`, para que cada uno lo
  compare con su spread.

**Se considera que la regla funciona** si la R neta por día es **> 0 con z ≥ 2,0**
en 2020-2025. Cualquier otra cosa es que no.

Se reporta siempre, funcione o no: el número de disparos al año, el riesgo
mediano, el reparto por dirección y el resultado con y sin reentradas.

## Lo que NO va a pasar, y conviene decirlo antes

**Esto no va a reproducir su agosto.** Tres motivos, los tres conocidos de
antemano:

1. El ajuste de 16 de 16 usó una tolerancia de ±1 vela, porque unas veces da la
   hora de apertura y otras la de cierre. En el backtest no hay tolerancia.
2. Sus stops reales van ~1 pip por dentro del extremo de la vela anterior. Los de
   la regla irán en el extremo: algo más anchos.
3. Él **no toma todos los disparos**. La regla dará 1,1 por mañana y él tomó 1,6,
   pero no son los mismos: ha dicho que a veces llega tarde y a veces duda. Esa
   discreción no está en la regla y puede ser justo donde está su ventaja.

Así que un resultado plano aquí **no desmiente su agosto**, y un resultado bueno
**no lo confirma**: son dos cosas distintas. Lo que esta prueba contesta es si la
regla escrita, sola y sin él, tiene ventaja.

## Lo que espero, dicho antes

Bruta ligeramente positiva y **neta alrededor de cero o por debajo**. El riesgo
mediano de sus operaciones es de 3,7 pips y 1,2 de diferencial son un tercio de
eso; haría falta un bruto por encima de +0,32 R sólo para empatar. Es la misma
aritmética que ha matado todo lo demás en este proyecto.

Llevo varias predicciones falladas —el filtro de H1, la potencia del ciego de
H12, las cinco del barrido de Asia, y la conclusión de que su estrategia era de
otra familia—. Ésta vale lo mismo que las otras.

## Ficheros

```
bt/asia_nivel.py         la pasada, se ejecuta una vez
data/asia_nivel.csv      las operaciones resueltas
```
