# Pre-registro · el timing del CRT, con la dirección dada por buena

Firmado **antes** de correr `bt/timing_crt.py`. Un solo pase.

## La afirmación, que es nueva

Vídeo de review semanal de CRT. A diferencia de los anteriores, **no afirma
nada sobre la dirección**. Afirma algo sobre *cuándo* entrar teniéndola ya:

> *«si tú estabas comprando ciegamente cada vela, esta, esta, esta, te habrías
> comido tres stops hasta tener el TP, **incluso teniendo la dirección bien**»*
> · *«de nada sirve tener el bias bien si estáis comprando en los momentos en
> los que no toca»* · *«va a haber veces que tu bias va a estar mal, pero no vas
> a tener el stop porque estás esperando, por lo tanto tu win rate está
> aumentando»*

La regla: con sesgo alcista, **no comprar mientras el rango H4 esté en contra**.
Esperar a que pase una de tres cosas —que el rango bajista se complete, que se
complete en la misma vela, o que se forme directamente un rango alcista— y
entonces comprar. Stop bajo el *turtle soup* (la mecha del barrido), objetivo en
el extremo superior del rango H4.

**Esto no está medido.** Las nueve familias del proyecto probaban si la señal
acierta el lado. Aquí el lado se da por bueno y se pregunta por el instante.

## Cómo se aísla el timing

La dirección se **fija por construcción**, en dos variantes:

- **largo siempre**: la hipótesis del vídeo sobre un activo tendencial.
- **sesgo oráculo**: la dirección real de la semana, conocida de antemano. Es
  mirar al futuro a propósito — y es la implementación *fiel* de su premisa
  («teniendo la dirección bien»). Aísla el timing perfectamente.

Con la dirección fija, cualquier diferencia entre reglas de entrada **es timing
y nada más**.

## Las cuatro reglas de entrada que se comparan

1. **Ciego** — entrar en la apertura de cada vela H4.
2. **CRT alineado** — entrar sólo cuando el rango H4 anterior ha sido barrido en
   contra del sesgo (rango alineado activado). Es la regla del vídeo.
3. **Espera al azar** — entrar en un subconjunto aleatorio de velas H4, **con el
   mismo número de operaciones que la regla 2**. ← **EL CONTROL QUE DECIDE**
4. **Espera fija** — entrar N velas después de cada señal, mismo número.

La regla 3 es la clave. En un mercado con tendencia, **esperar sin más mejora el
precio de entrada**: eso está disponible para cualquiera y no necesita CRT. Si
esperar al azar iguala a esperar el rango alineado, la regla no aporta nada.

## Contraste PRINCIPAL, declarado antes de mirar

**Acierto de cada regla menos su propio nulo geométrico** (`riesgo/(riesgo+recorrido)`).
Restar el nulo propio es obligatorio porque las reglas cambian el R:R, y el
acierto sube solo cuando el R:R baja. Agrupando los tres instrumentos, z con
error estándar agrupado por instrumento-día.

Secundario, y el que importa para su bolsillo: **esperanza por DÍA de calendario**,
no por operación. Esperar reduce el número de operaciones; una mejora por
operación a costa de operar un tercio de las veces puede no ser mejora.

## Predicción firmada

- **El acierto crudo SUBIRÁ con la regla del vídeo. Él tiene razón en eso.**
  Entrar después de que el movimiento adverso ya ha ocurrido evita stops.
- **Pero no superará su propio nulo geométrico.** Predigo exceso entre −2 y
  +2 puntos, no significativo.
- **La espera al azar capturará la mayor parte de la mejora.** Predigo que el
  exceso de la regla 2 sobre la regla 3 estará entre −1 y +1 punto.
- **La esperanza por día BAJARÁ** con la regla del vídeo, por hacer menos
  operaciones.

## Qué me refutaría

Exceso de la regla 2 sobre la regla 3 (espera al azar) mayor de +2 puntos de
acierto con z > +2, y esperanza por día no inferior a la del ciego. Eso sería
una ventaja de timing real y lo diría así.

## Limitación que declaro de antemano

El vídeo habla de **NASDAQ** y yo no tengo NASDAQ. Mido en EURUSD, oro y DAX.
El DAX es el más parecido —índice, tendencial, mismo tipo de volatilidad— pero
no es el mismo activo y lo tendré en cuenta al concluir.

Una sola pasada. Lo que salga se publica.
