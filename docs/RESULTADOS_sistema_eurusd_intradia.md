# Resultado · el sistema de day trading EUR/USD pedido, y el error que casi lo vende

Encargo del usuario: *«diseña una estrategia de day trading para EUR/USD, perfil
moderado, ventana de 4 horas, 100 % mecánica»*, con win rate y profit factor
esperados. **No se estiman: se miden.** Cinco años de EUR/USD M1 (2021-2026),
940 días hábiles. Código: `bt/sistema_eurusd_intradia.py` y
`bt/sistema_eurusd_placebos.py`.

---

## 0 · Primero el error, porque es lo más útil de este documento

La primera pasada dio esto:

```
  Londres 08-12 · R:R 1,5 · sin trailing
  4.133 operaciones · acierto 69,3 % · PROFIT FACTOR NETO 2,61
  a 1 % de riesgo sobre 10.000 EUR:  +4.523 EUR/mes
```

**Es mentira, y la causa es un error de signo de un carácter.**

En el motor de resolución escribí la salida por stop dos veces, una para cada
lado, con los operandos espejados **y conservando el factor `*lado`**:

```python
  if lado > 0:
      if lo <= sl: return (sl-ent)/r*lado      # (-r)/r * (+1) = -1   correcto
  else:
      if hi >= sl: return (ent-sl)/r*lado      # (-r)/r * (-1) = +1   MAL
```

En los cortos, **cada stop se contabilizaba como una ganancia de +1R**. El 53 %
de las operaciones eran cortas. Eso solo produjo:

| | con el error | corregido |
|---|---|---|
| acierto | **69,3 %** | **40,9 %** |
| profit factor neto | **2,61** | **0,87** |
| €/mes sobre 10.000 € | **+4.523** | **−736** |

Lo correcto es una sola expresión para los dos lados: `(sl-ent)*lado/r`.

**Esos son exactamente los números que anuncian los cursos.** Acierto del 70 %,
profit factor por encima de 2, cuatro mil euros al mes. No hace falta mala fe
para producirlos: hace falta un signo mal y no correr los placebos.

Y lo que lo detectó en treinta segundos:

```
  real (dirección del sistema)        R -0,0096   acierto 40,9 %
  placebo · dirección al azar         R +0,0018 / +0,0121 / -0,0085
  placebo · dirección INVERTIDA       R +0,0158
  placebo · entradas en minutos al azar  R +0,0117
```

Con el error, el placebo invertido también daba profit factor 2,6 — imposible
que dos direcciones opuestas ganen las dos. **Un placebo que gana igual que la
señal no significa «no hay ventaja»: puede significar «hay un bug».** Esa
distinción no estaba escrita en ningún documento del proyecto hasta hoy.

## 1 · La especificación medida

| | |
|---|---|
| dirección | D1: largo si el cierre de ayer > EMA(20) de cierres diarios; corto si < |
| contexto | H1: posición del cierre de la hora anterior en el rango de las últimas 6 horas |
| gatillo | M15 dentro de la ventana: retroceso (posición H1 < 1/3 para largos, > 2/3 para cortos) **y** vela M15 a favor (cierre > apertura para largos) |
| entrada | a mercado en la apertura del minuto siguiente al cierre de esa M15 |
| riesgo | **1,5 × ATR(14) de M15** → mediana **10,6 pips** en Londres |
| objetivo | R:R fijo, probado a 1,0 / 1,5 / 2,0 |
| cierre forzoso | 4 horas |
| coste | 0,70 pips (ECN real, ver `RESULTADOS_potencia_operaciones.md`) |

## 2 · Las dieciocho celdas, honestas

```
  sesión                  R:R  trail     n  riesgo  coste  acierto   geom  PF bru PF neto   R neta      z
  Londres 08-12           1,0     no  4133    10,6   7,0%    50,3%  50,0%    1,01    0,87  -0,0667  -2,75
  Londres 08-12           1,5     no  4133    10,6   7,0%    40,9%  40,0%    0,98    0,87  -0,0797  -2,59
  Londres 08-12           1,5     sí  4133    10,6   7,0%    37,5%  40,0%    1,01    0,84  -0,0650  -3,01
  Londres 08-12           2,0     no  4133    10,6   7,0%    36,4%  33,3%    0,96    0,86  -0,0942  -2,70
  NuevaYork 08-12         1,5     no  3941    13,3   5,6%    42,8%  40,0%    0,96    0,86  -0,0759  -2,80
  NuevaYork 09:30-13:30   1,5     no  3901    14,7   5,0%    45,5%  40,0%    0,94    0,83  -0,0759  -2,99
```

**Las dieciocho celdas tienen profit factor neto por debajo de 1.** Ninguna
excepción. Y el profit factor **bruto** está entre 0,93 y 1,02: el sistema es
exactamente justo antes de costes.

El exceso de acierto sobre el nulo geométrico va de **+0,3 a +12,2 puntos**
según la celda, pero eso es el artefacto de contar como «acierto» las
operaciones cerradas a mercado a mitad de camino. Lo que no engaña es la R
media, y es negativa en las dieciocho.

## 3 · Lo que sí se aprende de la tabla

**El diseño es bueno por el criterio del coste y aun así pierde.** El coste es
el **5-7 % del riesgo**, no el 67 % del CRT, porque el stop son 10-15 pips y no
3. Es decir: esta estrategia está bien construida. Pierde porque el bruto es
cero, no porque la horquilla se la coma.

**El trailing stop empeora el acierto y no arregla el neto.** Baja el acierto de
40,9 % a 37,5 % y el neto mejora un poco (−0,065 contra −0,080) sólo porque corta
antes a los perdedores. No crea ventaja; recorta la distribución por los dos
lados.

**Londres contra Nueva York: empate.** PF bruto 0,98 contra 0,96, dentro del
ruido. El riesgo mediano sí cambia (10,6 contra 13,3 pips): Nueva York tiene más
ATR, así que el coste relativo baja. Es la única diferencia real entre sesiones
y favorece a Nueva York por una razón que no tiene nada que ver con la
estrategia.

## 4 · El veredicto

```
  LA CELDA PEDIDA · Londres 08-12 · R:R 1,5 · sin trailing
  4.133 operaciones en 940 días  =  4,40 por día
  acierto 40,9 %  (nulo geométrico 40,0 %)
  profit factor bruto 0,98  ·  NETO 0,87
  a 1 % de riesgo sobre 10.000 EUR:  -7,97 EUR por operación,  -736 EUR/mes
```

No es que rinda poco: **cuesta 736 € al mes operarla.**

Y es, honestamente, el mejor sistema intradía que sé construir para EUR/USD con
tres meses de mediciones detrás. Está hecho con las tres únicas cosas que han
medido positivo en este proyecto —dirección del horizonte largo, entrada en
retroceso, objetivo cercano— y la respuesta sigue siendo la de siempre.
