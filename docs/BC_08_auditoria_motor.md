# BC · Auditoría del motor de backtest

Tras encontrar dos fallos en un solo día (`BC_07`), la pregunta razonable es si
el aparato de medida vale para algo. Esto es el intento de contestarla con
pruebas, no con confianza.

Se ejecuta entero con:

```
python3 bc/pruebas.py              # 35 pruebas con velas hechas a mano
python3 bc/prueba_ruido.py         # el motor contra datos sin señal
python3 bc/prueba_independencia.py # cuánto mienten los intervalos de confianza
python3 bc/prueba_ejecucion.py     # cuánto optimismo hay en suponer llenado exacto
```

---

# 1 · Treinta y cinco pruebas con la respuesta conocida

Velas construidas a mano donde se sabe cuál tiene que ser el resultado. Cubren
la activación en las tres lecturas, los cinco estados del rango, la rejilla de
bloques con su anclaje, la resolución de la operación en M1 y la aritmética del
coste. **Pasan las treinta y cinco.**

Tres «fallaron» en la primera ejecución y las tres eran mías, no del motor:

- con anclaje 6, el primer bloque empieza a las **18:00 del día anterior** —
  correcto, yo esperaba que empezara a las 06:00;
- un bloque con **exactamente** la mitad de los minutos pasa el filtro del 50 %;
- 30 horas de datos dan tres bloques de 12H, no dos.

Las expectativas corregidas, el código intacto.

## 1.1 · Contraste contra una segunda implementación

`vida_ingenua()` reescribe la máquina de estados de la forma más obvia posible,
sin optimizar nada. Sobre **60 series aleatorias de 100 velas** las dos
implementaciones coinciden en número de rangos, dirección, tomas y causa de
muerte. Un fallo tendría que estar en las dos a la vez y escrito de dos maneras
distintas.

# 2 · La prueba que decide: ruido puro

Un paseo aleatorio sin deriva es una martingala. Con stop y objetivo fijos, el
teorema del muestreo opcional dice que la esperanza en unidades de R es **cero**,
valga lo que valga el R:R. Si el motor encuentra ventaja ahí, la está fabricando.

4,5 millones de minutos sintéticos, tres réplicas, sin coste:

| réplica | n | %TP | R:R mediano | R bruta | IC95 | z |
|---|---|---|---|---|---|---|
| 0 | 798 | 14,3 % | 5,35 | −0,061 | [−0,228, +0,107] | −0,71 |
| 1 | 805 | 14,8 % | 5,54 | −0,038 | [−0,202, +0,126] | −0,45 |
| 2 | 791 | 15,3 % | 5,15 | −0,002 | [−0,177, +0,173] | −0,02 |
| **juntas** | **2.394** | **14,8 %** | **5,31** | **−0,034** | **[−0,131, +0,064]** | **−0,68** |

Con R:R mediano 5,31 la teoría predice 15,8 % de aciertos; se observa 14,8 %. La
diferencia sale de las salidas por tiempo (1,0 %) y del troceado en velas.

**El motor no fabrica ventaja donde no la hay.** Es lo más fuerte que se puede
decir de un backtester, y no depende de ninguna teoría sobre el mercado.

# 3 · Los intervalos de confianza sí mienten, un poco

Una operación puede estar abierta hasta 60 horas y la separación mediana entre
entradas es de 15 a 25 horas: **se solapan**. Comparten recorrido de precio, así
que no son independientes, y el error estándar de siempre —desviación partido
raíz de n— se queda corto.

Autocorrelación de la serie de R dentro de cada instrumento: **r₁ entre +0,02 y
+0,21**, y se desvanece a partir de r₂.

Bootstrap por bloques móviles contra el error estándar ingenuo:

| celda | ingenuo | bloques de 20 | factor | z ingenuo → z honesto |
|---|---|---|---|---|
| UTC · B | 0,0556 | 0,0637 | ×1,15 | −0,34 → −0,30 |
| Madrid · B | 0,0504 | 0,0546 | ×1,08 | −2,38 → −2,20 |
| NY · B | 0,0583 | 0,0640 | ×1,10 | −0,27 → −0,25 |

**Todos los z del proyecto están inflados entre un 8 y un 15 %.** El umbral de
Bonferroni con doce contrastes deja de ser 2,87 y pasa a ser del orden de **3,3**.
Nada de lo medido se acercaba a ninguno de los dos, así que ninguna conclusión
cambia — pero conviene tenerlo escrito para cualquier hallazgo futuro.

# 4 · Los datos de partida están limpios

| fichero | filas | duplicados | desordenados | high<low | cierre fuera del rango | precios ≤ 0 |
|---|---|---|---|---|---|---|
| EURUSD | 2.397.463 | 0 | 0 | 0 | 0 | 0 |
| GBPUSD | 2.396.898 | 0 | 0 | 0 | 0 | 0 |
| USDJPY | 2.396.718 | 0 | 0 | 0 | 0 | 0 |
| NAS100 | 2.205.182 | 0 | 0 | 0 | 0 | 0 |
| SPX500 | 2.172.967 | 0 | 0 | 0 | 0 | 0 |

Los 345-348 huecos de más de un día son los fines de semana de seis años y medio.
Saltos de más de 50 pips entre minutos consecutivos: 0,0007 % en EURUSD, 0,018 %
en NASDAQ.

# 5 · Lo que sigue sin estar bien, y en qué dirección falla

## 5.1 · El llenado exacto es optimista

El motor supone que el stop se llena en su precio. Si el precio llega por un
salto —la vela de un minuto ya abre al otro lado— la ejecución real es peor.

Sobre las 2.608 perdedoras de la celda Madrid·B:

| instrumento | perdedoras | por salto | % | exceso medio (R) | peor caso |
|---|---|---|---|---|---|
| EURUSD | 610 | 11 | 1,8 % | +0,0084 | +1,359 |
| GBPUSD | 595 | 10 | 1,7 % | +0,0016 | +0,673 |
| USDJPY | 504 | 12 | 2,4 % | +0,0227 | +3,460 |
| NAS100 | 480 | 6 | 1,2 % | +0,0146 | +3,415 |
| SPX500 | 419 | 27 | 6,4 % | +0,0344 | +4,817 |
| **todos** | **2.608** | **66** | **2,5 %** | **+0,0149** | **+4,817** |

Con un 85 % de perdedoras, el sesgo sobre la R media es de **+0,013 R por
operación**: el motor es optimista en esa cantidad. Los resultados negativos son,
por tanto, **un poco peores** de lo publicado, no mejores.

Y hay una cola que el motor esconde del todo: una sola operación de SPX500 perdió
**4,8 R** en vez de 1. Con un stop saltado por un hueco no se pierde lo que dice
el plan.

## 5.2 · Velas construidas a medias

El filtro deja pasar cualquier bloque con al menos la mitad de los minutos
esperados. En EURUSD:

| marco | velas | completas | con <80 % | con <60 % |
|---|---|---|---|---|
| 1D | 1.706 | 64,4 % | 6,7 % | 0,0 % |
| 12H | 3.338 | 73,8 % | 1,9 % | 1,2 % |
| 4H | 10.161 | 80,6 % | 7,1 % | 2,5 % |
| 1H | 40.157 | 90,0 % | 0,3 % | 0,0 % |

Cuarenta velas de 12H están hechas con seis horas de datos, y su máximo y su
mínimo son los de media ventana. Afecta a los barridos y por tanto a los rangos.
Pendiente: bajar el umbral al 80 % y ver si cambia algo.

## 5.3 · Dos desviaciones de la especificación

- **`BC_02` §9 dice «5 velas de la temporalidad del objetivo»** y el código usa
  siempre 5 velas de 12H, sea cual sea el marco del objetivo.
- **El tope cuenta filas de M1, no horas.** Sobre un fin de semana las filas que
  faltan no se cuentan, así que la ventana real en horas se alarga.

Las dos son menores y afectan solo al 1 % de operaciones que salen por tiempo.

# 6 · Qué se puede afirmar después de esto

**Se puede.** Que el motor implementa la máquina de estados que dice implementar,
comprobado con velas a mano y contra una segunda implementación. Que no inventa
ventaja sobre datos sin señal. Que los datos de partida están limpios.

**No se puede.** Que los z publicados sean exactos: hay que dividirlos por ~1,1.
Que las pérdidas simuladas sean las reales: falta 0,013 R por operación y la cola
de los huecos. Que el Pine haga lo mismo que esto — es otra implementación y
nadie la ha comprobado todavía; para eso está `data/referencia_indicador.csv`.

**Y una cosa que ya no se puede decir nunca más.** Estas pruebas se escribieron
después de dos semanas de mediciones. Tenían que haber ido antes.
