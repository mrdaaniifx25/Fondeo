# La estrategia, escrita sin ambigüedad

Esto es lo que se va a operar en la cuenta de FundingPips 10k. Está escrito así
para que el Pine se pueda comprobar línea a línea contra él, y para que dentro de
tres meses se pueda verificar que se operó lo que se dijo.

Todo lo que hay aquí sale de `docs/RESULTADOS_su_patron.md` (1.281 operaciones
medidas) y `docs/PLAN_fundingpips_10k.md` (40.000 carreras simuladas).

---

## 1 · Qué se mira

```
  INSTRUMENTO   EUR/USD, y sólo EUR/USD
  GRÁFICO       M15
  HUSO          Europe/Madrid
```

## 2 · El rango de referencia

```
  RANGO DE ASIA   desde las 00:00 hasta las 08:00 de Madrid, del MISMO día
      asiaH  =  el máximo más alto de esas 32 velas M15
      asiaL  =  el mínimo más bajo
```

Se cierra a las 08:00 y **no se vuelve a tocar en todo el día**.

## 3 · Cuándo se puede operar

```
  VENTANA   de 08:00 a 11:00 de Madrid, y nada más
```

Nueva York no se opera. Medido: bruta **+0,0835** (z +2,12) en Londres contra
**−0,0464** (z −2,60) en Nueva York.

## 4 · La señal

Se evalúa **al cierre de cada vela M15** dentro de la ventana.

```
  CORTO si las TRES a la vez:
      máximo de la vela   >=  asiaH          (barre el máximo de Asia)
      cierre de la vela    <  asiaH          (y vuelve DENTRO)
      mínimo de la vela    >  asiaL          (sin haberse llevado el otro lado)

  LARGO si las TRES a la vez:
      mínimo de la vela   <=  asiaL
      cierre de la vela    >  asiaL
      máximo de la vela    <  asiaH
```

**Una sola señal de cada lado por día.** La primera que aparezca; las demás se
ignoran aunque sean mejores.

## 5 · La entrada

```
  A MERCADO en la APERTURA de la vela M15 SIGUIENTE al cierre de la señal.
```

Nunca dentro de la vela de la señal. Nunca con orden limitada esperando mejor
precio: medido, exigir un retroceso **empeora** de forma monótona
(`RESULTADOS_punto_optimo.md`), por selección adversa en el relleno.

## 6 · Stop y objetivo

```
  RIESGO  =  1,5 x ATR(14) de M15, leída en la vela ANTERIOR a la entrada
  STOP    =  entrada − riesgo   (largo)      entrada + riesgo   (corto)
  OBJETIVO=  entrada + 2 x riesgo (largo)    entrada − 2 x riesgo (corto)
  SIN TRAILING
  CIERRE FORZOSO a las 6 horas de la entrada, a mercado
```

El stop de 1,5×ATR en vez de la mecha del barrido es el cambio que más vale:
el neto pasa de **−0,124 a −0,021**. Seis veces mejor sin acertar una más.

Sin trailing porque medido baja el acierto de 40,9 % a 37,5 % sin arreglar el
neto.

## 7 · El tamaño

```
  RIESGO POR OPERACIÓN   0,50 % del saldo  =  50 $ en una cuenta de 10.000

  lotes  =  50 / (riesgo_en_precio x 100.000)

  ejemplo:  riesgo 0,00071 (7,1 pips)  ->  50 / 71 = 0,70 lotes
```

## 8 · Las paradas del día

```
  1  TRES operaciones al día como máximo. La cuarta no se toma nunca.
  2  DOS pérdidas seguidas en el día -> se cierra la plataforma hasta mañana.
  3  -1,5 % en el día -> se cierra la plataforma hasta mañana.
```

La regla 1 es la que importa: 3 × 0,50 % = **1,50 %**, la mitad del límite
diario del 3 %. Tocar el 3 % hunde la probabilidad de aprobar del 35 % al 5 %.

## 9 · El registro

Una fila **al abrir la operación**, nunca después:

```
  fecha · hora · lado · entrada · stop · objetivo · lotes
  motivo en una frase
  resultado en R
  ¿vi señal y NO entré?  sí/no y por qué
```

## 10 · Los números esperados, dichos antes

```
  acierto esperado          ~36 %  (el umbral de equilibrio con R:R 2 y coste 0,10 R)
  esperanza medida          -0,021 R por operación
  prob. de pasar las 2 fases 35,2 %  con esperanza CERO
  tiempo mediano             70 días hábiles
```

**No se espera ventaja.** Se espera no reventar mientras la varianza decide. Si
tras 100 operaciones registradas el acierto está por encima del 36,7 %, entonces
habrá algo que mirar. Por debajo, no.
