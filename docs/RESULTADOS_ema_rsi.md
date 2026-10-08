# Resultados · EMA 50 + RSI 14 · H4 tendencia / M15 ejecución

Estrategia implementada literalmente según las reglas dadas: tendencia por EMA50
en H4 con filtro de rango, retroceso que toca la EMA50 en M15, RSI14 tocando 30
(o 70), gatillo por vela envolvente o martillo/estrella, y horario 08:00-17:00
hora de Europa central con cambio de hora real.

Lo único no especificado y que declaro yo: stop bajo el mínimo del retroceso más
un 10 % de su rango, y objetivo en múltiplo fijo de R, probado a 1R, 1,5R, 2R y 3R.

**Resultado: no es rentable en ninguno de los cinco instrumentos.**
Y en EUR/USD, que es el par para el que se propone, es de los peores.

---

## Los cinco instrumentos, los cuatro objetivos

Ventaja **bruta** en R por operación (antes de costes) y **profit factor neto**:

| | 1R | 1,5R | 2R | 3R | PF neto a 2R |
|---|---|---|---|---|---|
| **EURUSD** | −0,0380 | −0,0297 | −0,0210 | −0,0055 | **0,842** |
| **GBPUSD** | +0,0031 | −0,0262 | −0,0632 | −0,0391 | **0,791** |
| USDJPY | +0,0361 | +0,0566 | +0,0790 | +0,0385 | 1,007 |
| NAS100 | +0,0463 | +0,0721 | +0,1211 | +0,0125 | 1,131 |
| SP500 | +0,1011 | +0,1067 | +0,1235 | +0,2315 | 1,087 |
| **LOS CINCO** | +0,0246 | +0,0300 | +0,0400 | +0,0367 | **0,951** |

Agregado: 2.521 operaciones a 2R, ventaja bruta +0,0400 con **p 0,156**. No es
distinguible de cero. Y el profit factor neto se queda en **0,951**: pierde.

**EUR/USD es negativo en bruto a los cuatro objetivos.** Es el único instrumento
junto a GBPUSD del que se puede decir eso.

La casilla más vistosa es SP500 a 3R (+0,2315, p 0,0123). Con 20 casillas
probadas el umbral de Bonferroni es p < 0,0025. No lo alcanza.

## Los dos controles, que es donde se cierra el asunto

| | n | bruto/op | z |
|---|---|---|---|
| **La estrategia** (2R) | 2.521 | **+0,0400** | +1,42 |
| **Espejo** · misma señal, dirección contraria | 2.040 | **+0,0208** | +0,70 |
| **Entrada al azar** · mismas horas, mismo stop y objetivo | 16.075 | **+0,0349** | +3,15 |

Los tres números son el mismo número.

Si tomar la operación **al revés** de lo que dice la estrategia rinde igual, y
entrar en **momentos aleatorios** rinde igual, entonces la EMA, el RSI, la vela
envolvente y el filtro de sesión no están aportando información. El pequeño
positivo que se ve es una propiedad del motor de stop y objetivo, no de las
reglas de entrada.

## Qué regla aporta algo: ninguna

Agregado de los cinco instrumentos a 2R, quitando reglas de una en una:

| variante | n | bruto/op | p | PF neto |
|---|---|---|---|---|
| completa, las cuatro reglas | 2.523 | +0,0408 | 0,148 | 0,951 |
| **sin tocar la EMA de M15** | 2.569 | **+0,0490** | 0,079 | **0,964** |
| sin el patrón de vela | 10.435 | +0,0189 | 0,172 | 0,831 |
| sin el RSI | 9.611 | −0,0142 | 0,321 | 0,856 |
| sin filtro horario | 4.354 | +0,0042 | 0,842 | 0,892 |
| solo tendencia H4 + patrón | 11.731 | +0,0037 | 0,776 | 0,894 |
| solo el patrón de vela | 14.551 | +0,0171 | 0,137 | 0,921 |

**Ninguna combinación llega a un profit factor de 1.** La mejor es 0,964, y se
consigue **quitando** el requisito de tocar la EMA50 en M15, que es una de las
cuatro reglas centrales. Es decir: esa regla resta.

El filtro horario sí aporta algo (sin él la ventaja cae de +0,0408 a +0,0042),
pero no lo suficiente para hacer rentable nada.

## El embudo, para ver de dónde salen las 500 operaciones

En EURUSD, sobre 51.965 velas M15 que pasan el filtro de tendencia:

```
tendencia H4 válida    51.965
  toca la EMA50 M15    28.771
    RSI toca 30/70      7.282
      patrón de vela       785   <- el patrón es lo que hace la selección
```

El patrón de vela descarta el 89 % de los candidatos. Y esa selección no mejora
el resultado: sin ella, la ventaja es +0,0189 con 10.435 operaciones; con ella,
+0,0408 con 2.523. La diferencia entre ambas no es significativa.

## Conclusión

Es la cuarta estrategia de la familia «confluencia de indicadores» que se prueba
en este proyecto y da el mismo resultado que las tres anteriores: cero bruto,
negativo neto, e indistinguible de entrar al azar.

Que esté bien explicada, tenga reglas claras y suene razonable no la hace
distinta. La única forma de saberlo era medirla.
