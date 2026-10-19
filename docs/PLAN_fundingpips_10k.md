# Su plan · FundingPips 10k, dos fases

Cuenta real del usuario, ganada en un sorteo. **Coste de intentarlo: cero euros.**
Reglas: fase 1 **+8 %**, fase 2 **+5 %**, pérdida diaria máxima **3 %**,
drawdown total **10 %**.

Simulado en `bt/fundingpips_rejilla.py`, 40.000 carreras por celda, con el coste
de 0,10 R medido en su propio patrón de Londres.

---

## 1 · El número, y por qué cambia mi consejo

```
  R:R 2 · esperanza CERO · % que pasa LAS DOS fases
   ops/día     0,50 %    0,75 %    1,00 %    1,50 %    2,00 %
         1      26,5%     34,7%     35,1%     34,5%     33,1%
         2      33,8%     35,2%     34,6%      4,2%         —
         3      35,2%     34,8%      4,6%         —         —
         4      35,0%      5,4%         —         —         —
```

**Dos cosas que no le había dicho:**

**a · El 0,50 % solo con UNA operación al día es malo: 26,5 %.** Porque el coste
es fijo en R y hacen falta cuatro veces más operaciones para recorrer el 8 %. Ir
despacio *y* pequeño es la peor combinación.

**b · El acantilado.** Mire qué pasa cuando `ops × riesgo` **toca** el 3 %:

```
  1,50 % x 2 = 3,0 %   ->   4,2 %     (desde 34,6 %)
  1,00 % x 3 = 3,0 %   ->   4,6 %
  0,75 % x 4 = 3,0 %   ->   5,4 %
```

**De 35 % a 5 %.** Rozar el límite diario no es «ir justo»: es morir.

## 2 · LA CONFIGURACIÓN

```
  RIESGO POR OPERACIÓN      0,50 %  =  50 $
  MÁXIMO POR DÍA            3 operaciones
  PEOR DÍA POSIBLE          1,50 %  =  la MITAD del límite
  PROBABILIDAD DE PASAR     35,2 %  (la mejor de toda la rejilla)
```

Tres al día, no cuatro. Su demo venía haciendo 4,4. **Baje a 3 y tendrá el doble
de colchón con la misma probabilidad.**

## 3 · Tamaño de posición, ya calculado

`lotes = 50 $ / (stop en pips × 10)` para EUR/USD:

| stop | lotes | | stop | lotes |
|---|---|---|---|---|
| 5 p | 1,00 | | 10 p | 0,50 |
| 6 p | 0,83 | | 12 p | 0,42 |
| **7 p** | **0,71** | | 15 p | 0,33 |
| 8 p | 0,62 | | 20 p | 0,25 |

Su stop mediano medido con 1,5×ATR es **7,1 pips** → unos **0,70 lotes**.

## 4 · La operativa

| | |
|---|---|
| **instrumento** | EUR/USD, solo |
| **ventana** | **Londres 08:00-11:00** hora española. **Nada en Nueva York** |
| **gráfico** | M15 para la señal, rango de Asia 00:00-08:00 como referencia |
| **entrada** | barrido del extremo de Asia + **cierre de vuelta dentro**. Entra en la vela SIGUIENTE, nunca dentro de la vela del barrido |
| **stop** | **1,5 × ATR(14) de M15** — no la mecha |
| **objetivo** | **R:R 2** fijo |
| **sin trailing** | medido: baja el acierto de 40,9 % a 37,5 % |

**Por qué el stop de 1,5×ATR y no la mecha**: medido sobre 1.281 operaciones
suyas, el neto pasa de **−0,124 a −0,021**. Seis veces mejor sin acertar una
operación más.

**Por qué Londres y no NY**: bruta **+0,0835** (z +2,12) contra **−0,0464**
(z −2,60).

## 5 · Las tres reglas de parada

```
  1  TRES operaciones al día. Se acabó. Aunque vea la cuarta perfecta.
  2  DOS pérdidas seguidas en un día -> cierra la plataforma hasta mañana.
  3  -1,5 % en el día -> cierra la plataforma hasta mañana.
```

La 3 nunca debería dispararse si cumple la 1. Está por si acaso.

## 6 · El registro, que es obligatorio

Una fila por operación, **escrita al abrirla**, nunca después:

```
  fecha · hora · lado · entrada · stop · objetivo · lotes
  motivo en una frase
  resultado en R
  ¿vi una señal y NO entré?  (sí/no y por qué)
```

Tres cosas lo hacen válido: **todas** las operaciones, **antes** del resultado, y
**también las que no tomó**. Sin eso está midiendo su memoria.

Con **100 filas** se puede separar su timing de la dirección de la semana. Con 6
no puede nadie.

## 7 · Cuándo subir el tamaño

**No toque el 0,50 % hasta tener 100 operaciones registradas.** Entonces:

```
  acierto medido < 36,7 %  ->  no tiene ventaja con R:R 2. No suba nada.
  acierto 36,7 - 45 %      ->  suba a 0,60 %. Un 20 %, no más.
  acierto > 45 %           ->  hablamos, porque sería un resultado real
```

El 36,7 % es su umbral de equilibrio con R:R 2 y coste 0,10 R. Por debajo de
ahí, subir el tamaño sólo acelera la pérdida.

## 8 · Qué esperar, con honestidad

```
  probabilidad de pasar las DOS fases, con esperanza CERO:   35,2 %
  si la pasa, probabilidad de retirar con regularidad:        depende de la ventaja
  ventaja medida en su patrón:                               -0,021 R
```

**Puede pasar este examen sin tener ninguna ventaja.** Una de cada tres. No sería
suerte tonta: sería el resultado esperado de no reventar.

Y si lo pasa, **ahí empieza el problema de verdad**, porque retirar todos los
meses sí exige ventaja y mantener una cuenta fondeada sin ella acaba en cero.

Pero esta cuenta le salió gratis. **El peor caso es que se quede como está.**
Así que la decisión correcta es intentarlo — bien dimensionado, con el registro,
y sabiendo qué parte del camino cubre esto.
