# Pre-registro · búsqueda masiva: 20.000 estrategias mecánicas

Firmado **antes** de correr `bt/busqueda_masiva.py`. Un solo pase.

## El reto del usuario, textual

> *«Tienes los datos, un sistema de backtest, no me creo que no puedas encontrar
> nada ni scalping, ni day trading ni nada de estrategia»*

Es justo. Y la respuesta no es repetir conclusiones: es **dejar de elegir yo** y
generar el espacio entero por fuerza bruta.

## El montaje

**Primitivas** (~40 condiciones booleanas por barra), de todas las familias:

| familia | primitivas |
|---|---|
| osciladores | RSI(7/14/21) sobre/bajo 30-50-70 · estocástico |
| tendencia | MM 10/20/50/100/200 cruzadas · MACD 12/26/9 · pendiente |
| volatilidad | posición en canal ATR · percentil de ATR · rango de la barra |
| ruptura | Donchian 10/20/55 · máximo/mínimo del día anterior |
| liquidez / CRT | barrido del rango de la barra anterior · cierre de vuelta dentro |
| velas | envolvente · martillo · cuerpo grande · racha de N barras |
| calendario | tramo horario (6) · día de la semana (5) |

**Estrategias**: combinaciones aleatorias de **2 o 3 primitivas con AND**, más
una dirección (largo / corto) y una salida.

**Salidas**: stop = k × ATR(14) con k ∈ {1, 2, 3}, objetivo R:R ∈ {1, 2}.
*(El espacio de salidas se exploró aparte con 220 celdas en
`RESULTADOS_punto_optimo.md`; aquí el peso está en la entrada.)*

**Temporalidades**: M5 (scalping), M15 (day trading), H1. **Instrumentos**:
EUR/USD, oro, DAX. Coste ECN.

**20.000 estrategias**, mínimo 200 operaciones dentro de muestra.

## La partición, declarada antes

- **Dentro de muestra**: hasta el 31-12-2024.
- **FUERA de muestra**: 2025-2026. **No se mira hasta haber elegido.**

## Los tres contrastes, declarados antes de mirar

1. **Distribución de t dentro de muestra** contra lo que daría el puro ruido.
2. **Las 200 mejores dentro de muestra → su resultado FUERA.** Si en este espacio
   hay algo real, seleccionar por lo de dentro tiene que dar positivo fuera.
3. **PRINCIPAL · correlación entre t dentro y t fuera** sobre las 20.000.
   Es el número que contesta su reto: mide si **buscar sirve de algo**.
   - correlación claramente positiva → buscar sirve, y él tiene razón.
   - correlación ≈ 0 → el espacio es ruido y ninguna búsqueda lo arregla.

## Predicción firmada

- La distribución de t dentro de muestra estará **desplazada a negativo** por el
  coste y será **más ancha que N(0,1)** por el agrupamiento temporal.
- Habrá **cientos de estrategias con t > +3 dentro de muestra**. Eso es lo
  esperable y no significa nada.
- **Las 200 mejores dentro darán FUERA una media de R neta entre −0,05 y +0,02**,
  es decir indistinguible de cero o negativa.
- **PRINCIPAL: correlación entre t dentro y t fuera entre −0,10 y +0,10.**

## Qué me refutaría

Correlación dentro-fuera **por encima de +0,20**, o las 200 mejores dando fuera
una R neta media positiva con t > +2. Cualquiera de las dos cosas significa que
buscar en este espacio encuentra ventaja real, y lo diría así, con las reglas
exactas de las que sobrevivan.

Una sola pasada. Lo que salga se publica, con la distribución completa.
