# Resultados · CRT+DOL y confluencia de barrido sobre índices

Ejecución del protocolo fijado en `PREREGISTRO_indices.md`, escrito antes de
recibir los datos.

**Resultado global: negativo en las cuatro pruebas. El modelo no transfiere.**
Conforme a la sección 7 del pre-registro, esto significa que la ventaja medida
en EURUSD era ruido afortunado, y la conclusión de toda la investigación pasa a
ser negativa en firme.

---

## Verificación previa de los datos

| | NAS100 (NSXUSD) | SP500 (SPXUSD) |
|---|---|---|
| Velas M1 | 2.205.182 | 2.172.967 |
| Periodo | 2020-01-01 → 2026-07-31 | 2020-01-01 → 2026-07-31 |
| OHLC incoherente | 0 | 0 |
| Pico de volatilidad invierno → verano | 15h → 14h UTC | 15h → 14h UTC |
| Rango medio de la vela M1 | 6,89 puntos sobre 16.620 | 1,51 puntos sobre 4.825 |
| Huecos largos | 2.241 de ~106 min | 2.233 de ~106 min |

El desplazamiento de una hora del pico de volatilidad entre estaciones es la
apertura de EEUU y confirma que la conversión horaria es correcta, igual que en
los cuatro pares de divisas. Los huecos de 106 minutos son los cierres diarios
de mantenimiento, normales en un CFD de índice.

## Compromiso cumplido: cero reajuste

Los nueve parámetros llegaron congelados desde EURUSD y ninguno se tocó.
La única adaptación fue la declarada de antemano: el pip pasa a ser el punto del
índice, y el colchón del stop se expresa en esa misma unidad. Todo el conjunto
de índices es, por construcción, fuera de muestra.

---

## P1 · CRT+DOL congelado en NAS100

```
473 operaciones (72 al año)   |   riesgo medio 55,1 puntos
118 salidas por TP = 24,95 %  (equilibrio a 3R: 25,00 %)
119 operaciones con R bruta positiva = 25,16 %  (una salida por tiempo a +2,95R)
VENTAJA BRUTA  +0,0062 R/op  |  z +0,08  |  p 0,9378
mitades: 1ª −0,0680   2ª +0,0802
```

| Coste | % del riesgo | R neto | PF |
|---|---|---|---|
| 1,0 pt | 1,8 % | −11,14 | 0,969 |
| **1,5 pt (principal)** | **2,7 %** | **−18,18** | **0,951** |
| 2,0 pt | 3,6 % | −25,22 | 0,933 |
| 4,0 pt | 7,3 % | −53,39 | 0,865 |

Criterios: n ≥ 200 **sí** · ventaja bruta con p < 0,05 **no** · PF neto > 1 **no**.
**Falla.**

## P2 · CRT+DOL congelado en SP500

```
466 operaciones (71 al año)   |   riesgo medio 12,9 puntos
win rate 25,54 %              (equilibrio a 3R: 25,00 %)
VENTAJA BRUTA  +0,0279 R/op   |  z +0,34  |  p 0,7308
mitades: 1ª −0,0730   2ª +0,1287
```

| Coste | % del riesgo | R neto | PF |
|---|---|---|---|
| **0,6 pt (principal)** | **4,7 %** | **−20,25** | **0,945** |
| 1,0 pt | 7,8 % | −42,41 | 0,890 |
| 1,5 pt | 11,7 % | −70,11 | 0,828 |
| 4,0 pt | 31,1 % | −208,59 | 0,591 |

Criterios: n ≥ 200 **sí** · ventaja bruta con p < 0,05 **no** · PF neto > 1 **no**.
**Falla.**

### Réplica independiente

P1 y P2 son dos mercados distintos, con ~470 operaciones cada uno y periodos
idénticos. Los dos dan la misma respuesta: ventaja bruta estadísticamente
indistinguible de cero (p 0,94 y p 0,73). No es «no transfiere a NASDAQ». Es
«no transfiere».

### Reparto por año, que es lo que de verdad enseña la nada

| Año | NAS100 n / R bruta media | SP500 n / R bruta media |
|---|---|---|
| 2020 | 66 · −0,091 | 58 · −0,172 |
| 2021 | 72 · −0,167 | 68 · 0,000 |
| 2022 | 71 · −0,099 | 69 · +0,159 |
| 2023 | 57 · +0,192 | 71 · +0,127 |
| 2024 | 96 · 0,000 | 95 · −0,074 |
| 2025 | 70 · +0,257 | 70 · +0,029 |
| 2026 | 41 · −0,024 | 35 · +0,228 |

El signo cambia sin patrón y los dos índices no coinciden ni en los años buenos.
Así se ve un cero con ruido alrededor.

---

## P3 y P4 · confluencia frente a divergencia

Sobre los 506 setups de NAS100, 499 tienen datos simultáneos de SP500.
El reparto es complementario exacto: o SP500 barrió su extremo H4 a la vez, o no.

| Reparto | n | bruto/op | p | PF a 1,5 pt |
|---|---|---|---|---|
| **P3** SP500 **también** barrió (confluencia) | 377 | **+0,0078** | 0,9304 | 0,954 |
| **P4** SP500 **no** barrió (divergencia SMT) | 102 | **+0,0588** | 0,7376 | 1,014 |

```
diferencia  −0,0510 R/op  |  z −0,26  |  p 0,7958
```

Criterios: mismo signo que en EURUSD **no** (se invierte) · p < 0,05 **no**.
**No se replica.**

### Esto cierra H3a, que era la única hipótesis que seguía viva

En EURUSD el mismo reparto daba confluencia **+0,3521** frente a divergencia
**−0,1364**, una diferencia de +0,4885 con p 0,040. Era el hallazgo más llamativo
de toda la investigación, y quedó registrado como «hipótesis viva pero no
confirmada» precisamente porque no superaba Bonferroni y porque el tamaño
muestral se quedaba en 142.

Aquí tenía n = 377, holgura de sobra, y datos que nunca se habían tocado.
La diferencia no solo no se replica: **cambia de signo**.

Y conviene leerlo bien: esto **no** es evidencia a favor del SMT clásico. Los dos
grupos están pegados a cero (p 0,93 y p 0,74) y la diferencia entre ellos es
p 0,80. Un efecto real no se invierte al cambiar de mercado. Un efecto de ruido
sí, y eso es exactamente lo que se observa. El +0,4885 de EURUSD fue el mejor de
once contrastes sobre 243 setups; con once intentos, encontrar algo así es lo
esperable aunque no haya nada debajo.

---

## La hipótesis del coste: acertada a medias y, en cualquier caso, irrelevante

Predije en la sección 7 que el coste relativo caería del 6,5 % del riesgo en
EURUSD a un 2 % aproximado en índices, y que por eso la cifra neta mejoraría.

- En NAS100 acerté: **2,7 %** del riesgo con 1,5 puntos de spread.
- En SP500 me equivoqué, y en la dirección contraria: el riesgo medio es de solo
  **12,9 puntos**, así que 1,5 puntos de spread son el **11,7 %** del riesgo,
  casi el doble que en EURUSD. Un índice con menos puntos de rango no es un
  instrumento más barato en términos de riesgo.

Da igual. Aun con el coste más favorable de los cinco probados, el profit factor
se queda en 0,969 en NAS100, porque **no hay ventaja bruta que proteger**. El
coste nunca fue el problema. Era la explicación cómoda.

---

## Decisión, conforme a la sección 6 del pre-registro

Se reportan las cuatro pruebas, todas negativas. **Se cierra la línea de
investigación del CRT.**

Lo que queda establecido, sumando esto a lo anterior:

1. Las tres estrategias de la familia CRT tienen ventaja bruta cero en EURUSD,
   con tres tipos de control independientes cada una.
2. Tampoco tienen ventaja en NAS100 ni en SP500, con los parámetros congelados
   y sin reajustar nada.
3. La confluencia de barrido, que parecía el único resto de señal, no se replica
   y se invierte.
4. La divergencia SMT, enseñada como confirmación central en las nueve
   transcripciones, no aparece por ningún lado: es el peor filtro en EURUSD y en
   índices no se distingue de su contrario.

Ninguna de estas cuatro conclusiones se podía saber sin medirla. Ese es el valor
de haberlo hecho.
