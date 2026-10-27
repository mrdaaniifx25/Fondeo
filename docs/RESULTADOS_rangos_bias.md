# Resultado · rangos por temporalidad y bias diario

Pre-registro: `docs/PREREGISTRO_rangos_bias.md`, escrito **antes** de medir.
Código: `bt/rangos_bias.py`. Indicador: `pine/rangos_bias.pine`.
EUR/USD, 2021-2026, 2.055.684 velas de un minuto.

---

## 1 · El tamaño real de cada rango

```
  tf          n      p25   MEDIANA      p75      p95    media
  D1       1492     49,3      67,0     90,4    144,8     74,6
  H4       9088     14,5      22,3     34,2     64,8     27,4
  H1      34460      7,1      10,9     17,1     32,5     13,8
  M15    137806      3,4       5,3      8,3     15,9      6,7
```

**La vela de M15 mide 5,3 pips de mediana.** Esto no es un dato de adorno: es
la explicación de por qué el CRT clásico en M15 no puede funcionar. Si la
referencia es una vela de 5 pips y el stop va «detrás del extremo», tu stop
son 6-9 pips, y con un diferencial de 0,7 el peaje es el **8-12 % del riesgo**.
Es el mismo muro de `RESULTADOS_scalping.md`, aquí visto desde el otro lado.

Para operar con un stop de 15 pips —el de `MEAN_REVERSION_REGLAS.md`— la
referencia mínima razonable es **H1 (10,9 de mediana) o H4 (22,3)**. En M15 el
stop es tres veces el rango entero de la vela.

## 2 · Qué hace la vela siguiente con el rango de la anterior

```
  tf         n  solo alto  solo bajo   los dos  interior
  D1      1491      35,9%      38,0%     11,4%     14,7%
  H4      9087      33,2%      34,0%     15,3%     17,5%
  H1     34459      36,7%      36,8%     11,1%     15,4%
  M15   137805      37,7%      37,2%     10,0%     15,2%
```

Lo primero que salta: **las cuatro filas son casi idénticas.** D1, H4, H1 y M15
—temporalidades que van de 15 minutos a un día— se comportan igual. Eso es la
firma de la geometría, no la de un comportamiento del mercado.

### El montaje del CRT, con su frecuencia exacta

```
  tf     barre alto   y cierra dentro   barre bajo   y cierra dentro
  D1          47,3%             50,5%        49,4%             48,6%
  H4          48,5%             49,5%        49,3%             51,0%
  H1          47,8%             51,0%        47,9%             49,2%
  M15         47,6%             47,5%        47,2%             47,2%
```

**Barrer el extremo de la vela anterior pasa el 47-49 % de las veces. Y cerrar
otra vez dentro, el 50 %.** En las cuatro temporalidades, con las mismas dos
cifras.

Un barrido con vuelta ocurre, por tanto, en **uno de cada cuatro casos** por
lado. No es un evento raro que haya que cazar: es la mitad de la mitad, que es
lo que da una moneda.

### Y lo que pasa después

```
  (movimiento de la vela siguiente, en la dirección que predice el CRT)
  tf         n  media pips       t   acierto    ciego
  D1       713       0.197    0.11     51,6%    49,7%
  H4      4467       0.444    1.42     50,9%    50,0%
  H1     16516      -0.121   -1.47     49,5%    49,6%
  M15     61870     -0.031   -1.45     48,9%    49,3%
```

Nada. El mejor es **H4 con t +1,42** sobre 4.467 casos, y no llega a 2. H1 y
M15 van en contra. La columna `ciego` es el control: el acierto de no mirar
nada. **El barrido con vuelta aporta entre −0,7 y +0,9 puntos sobre no mirar.**

## 3 · El bias diario

Cinco definiciones, todas calculadas sólo con velas cerradas, contrastadas
contra el movimiento del día en unidades de ATR(14):

```
  bias                                            n  media ATR       t   acierto
  A · dirección de la vela de ayer             1231     0,0087    0,46     50,4%
  B · apertura de hoy vs rango de ayer           38    -0,1465   -1,29     47,4%
  C · cierre de ayer vs punto medio            1229    -0,0174   -0,92     48,7%
  D · barrido CRT de ayer                       516     0,0133    0,47     52,7%
  E · cierre de ayer vs EMA20 diaria           1232    -0,0063   -0,33     48,0%
  (control) comprar siempre                    1232     0,0112    0,59     50,1%
```

**Las cinco por debajo de |t| = 1,3.** La mejor en valor absoluto es B, con
−1,29, y tiene **38 casos**. La que más acierto direccional da es D con 52,7 %,
que sobre 516 casos es ruido puro.

Y el dato que lo cierra: **el control «comprar siempre» da t +0,59**, más que
tres de las cinco definiciones. Ninguna aporta sobre no tener bias.

```
  error estándar con n=1232: 0,0190 ATR -> detectaría +0,0379 a t=2
  mejor medido: -0,0174
```

Combinarlos tampoco:

```
  A y E de acuerdo        n 761  media +0,0018  t +0,07
  A y E en desacuerdo     n 470  media +0,0200  t +0,69
```

Cuando los dos bias coinciden, el resultado es **más plano** que cuando se
contradicen. Es decir: justo al revés de lo que dice la idea de «confluencia».

## 4 · Mis predicciones

Declaré cuatro cosas antes de medir:

1. Los rangos son descriptivos, no señal. **Confirmado.**
2. Las cinco definiciones de bias darían cero. **Confirmado.**
3. Ninguna pasaría |t| = 2,33. **Confirmado**: el máximo es 1,29.
4. La tasa de «barre y cierra dentro» sería alta (20-35 %) y no significaría
   nada. **Acerté en lo segundo y me quedé corto en lo primero**: no es el
   20-35 %, es el **47-49 % de barrido con un 50 % de vuelta**, o sea un 24 %
   por lado, y es idéntica en las cuatro temporalidades.

## 5 · Para qué sirve entonces el indicador

Para saber **dónde** estás, no hacia dónde vas.

Los niveles de D1 y H4 son los que más gente mira, y por eso son donde se
acumulan las órdenes. Eso los hace útiles como **referencia de dónde poner un
stop o un objetivo**, que es un problema de geometría y no de predicción. Dos
usos concretos y honestos:

- **No pongas el stop justo detrás de un extremo de D1 o H4.** Lo barren el
  47-49 % de las veces.
- **Un objetivo puesto en el extremo opuesto de un rango de H1 o H4 es
  alcanzable**: son 10,9 y 22,3 pips de mediana, y un objetivo de 30 pips como
  el de la estrategia de reversión cae dentro del rango típico de H4.

Lo que el indicador **no** hace es decirte si comprar o vender. Está medido y
no lo sabe.
