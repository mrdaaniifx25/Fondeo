# Resultados · Efectos con muestra grande

Tras cerrar en negativo reversión y tendencia, el diagnóstico fue que el problema
no era la idea sino **el tamaño de muestra**: 25-90 operaciones no distinguen nada
de nada. Estas tres pruebas buscan efectos con cientos de observaciones.

## E1 · Nocturno frente a diurno en índices — NEGATIVO

La dirección coincide con la literatura (la prima se acumula fuera de sesión),
pero **la diferencia no es significativa** y la financiación se la come.

| | nocturno 16:00→09:30 | diurno 09:30→16:00 | diferencia |
|---|---|---|---|
| NAS100 | +0,0504 %/día (p 0,082) | +0,0392 % (p 0,207) | p **0,791** |
| SP500 | +0,0418 %/día (p 0,068) | +0,0210 % (p 0,375) | p **0,523** |

Falla el criterio declarado (p<0,01). Y a 4 % de financiación anual el acumulado
nocturno cae de +96 % a +54 % en NAS100. No es operable.

## E2 · Calendario — POSITIVO, y es lo único que ha pasado un umbral serio

35 casillas probadas, umbral Bonferroni p < 0,00143. **Dos lo superan:**

| instrumento | casilla | n | media/día | z | p |
|---|---|---|---|---|---|
| SP500 | **lunes** | 343 | +0,2137 % | +4,04 | **0,00005** |
| NAS100 | **lunes** | 343 | +0,2769 % | +3,84 | **0,00012** |

Los cinco instrumentos tienen el lunes positivo. USDJPY +0,0739 (p 0,004) y
GBPUSD +0,0706 (p 0,005) se quedan cerca del umbral.

### Verificación: no es un artefacto de datos finos

Mi primera sospecha fue que el cierre del domingo (sesión de 357 velas, la más
fina de la semana) estuviera mal marcado e inflara el lunes. **Es falso.**
Localizando el retorno dentro del lunes:

| tramo (hora de Nueva York) | NAS100 | SP500 |
|---|---|---|
| 00:00→03:00 Asia | +0,0079 % (p 0,64) | +0,0067 % (p 0,64) |
| 03:00→09:30 Europa | +0,0744 % (p 0,028) | +0,0777 % (p 0,006) |
| **09:30→16:00 sesión EEUU** | **+0,2053 % (p 0,0004)** | **+0,1204 % (p 0,006)** |
| 16:00→24:00 | +0,0279 % (p 0,30) | +0,0347 % (p 0,18) |

El efecto vive en **la sesión más líquida de la semana**, no en las horas finas.
Un artefacto de marcado haría lo contrario.

### El control decisivo: sesión de EEUU por día de la semana

| | lunes | martes | miércoles | jueves | viernes | **martes-viernes** |
|---|---|---|---|---|---|---|
| NAS100 | **+0,2227 %** (p 0,0006) | −0,0044 | +0,0456 | −0,0700 | +0,0180 | **−0,0024 %** (p 0,94) |
| SP500 | **+0,1299 %** (p 0,0067) | −0,0268 | +0,0210 | −0,0378 | +0,0298 | **−0,0037 %** (p 0,89) |

Acumulado de la sesión diurna en 6,5 años: NAS100 **+85,7 % los lunes** frente a
**−11,7 % de martes a viernes**. Toda la ganancia intradía del índice ocurrió los
lunes; el resto de la semana es plano-negativo.

### Neto de costes

| | n | neto/op | aciertos | acumulado | caída máx | Sharpe | p |
|---|---|---|---|---|---|---|---|
| NAS100 | 286 | **+0,2137 %** | 61,9 % | +81,0 % | 8,4 % | **1,41** | 0,00097 |
| SP500 | 286 | +0,1175 % | 61,2 % | +38,6 % | 6,4 % | 1,05 | 0,014 |

Positivo **los siete años** en ambos. Expuesto el 3,9 % del tiempo.

### Potencia estadística: por primera vez, suficiente

Desviación por operación 1,09 %. Para detectar +0,22 % al 80 % de potencia hacen
falta **189** observaciones. Hay **286**. Es lo primero en todo el proyecto que
está adecuadamente medido.

### Las cinco reservas, que son serias

1. **Es un hallazgo dentro de muestra.** Lo encontré escaneando 35 casillas y
   después profundizando en la ganadora. **No hay reserva ciega para esto.** Es
   exactamente el pecado del que te he protegido toda la semana.
2. **La literatura clásica dice lo contrario:** el «efecto fin de semana» tenía
   el lunes NEGATIVO durante décadas. O se ha invertido, o 2020-2026 es especial.
3. **SP500 pierde la significación sin 2020** (+0,0888 %, p 0,056). Solo NAS100
   aguanta (+0,1576 %, p 0,015).
4. **Medio efecto está en los primeros 30 minutos**, que es cuando la horquilla
   es más ancha y el deslizamiento peor. De 09:30 a 16:00 da +0,2137 %; de 10:00
   a 15:30 da +0,0591 % y deja de ser significativo.
5. **Dos índices correlacionados al 0,9 son una observación, no dos.**

## E3 · Filtro lento como control de caída — PARCIALMENTE POSITIVO

No bate a comprar y mantener en rentabilidad, y no se le pedía. Se le pedía mejor
relación rentabilidad/caída:

| NAS100 | ×final | anual | caída máx | anual/caída |
|---|---|---|---|---|
| comprar y mantener | 3,226 | 15,5 % | 35,5 % | 0,44 |
| **largo solo si precio > media 150** | 2,706 | 13,0 % | **17,0 %** | **0,77** |

Mitad de caída máxima por un 16 % menos de rentabilidad. Cumple el criterio.
En SP500 el efecto existe pero es menor (0,32 → 0,45).

## Conclusión

De tres pruebas, una negativa (E1), una positiva y robusta pero **dentro de
muestra** (E2), y una parcialmente positiva (E3).

El lunes es la mejor hipótesis viva del proyecto entero, y la única con potencia
estadística suficiente. Eso **no** la convierte en una ventaja demostrada. La
convierte en la única candidata que merece un test hacia delante.
