# Pre-registro · el barrido de Asia en la apertura de Londres

**Escrito antes de correr nada.** Fecha: 2026-08-27.

## De dónde sale

No de ningún vídeo ni de bctrades: **lo encontró el usuario mirando el gráfico**
con el indicador de sesiones puesto. Revisó julio y agosto de 2026 a ojo y el
patrón se cumplía. Es la primera hipótesis del proyecto que nace de una
observación suya.

Y no es CRT. Es otra familia: **liquidez de sesión**. El rango de Asia deja dos
niveles, y Londres los ataca al abrir.

## La regla, tal y como la describe

```
SESIÓN       Londres, 08:00 – 14:00 hora de España
REFERENCIA   el máximo y el mínimo que dejó Asia (00:00 – 08:00)
TEMPORALIDAD todo en M5

ROTURA       una vela de M5 CIERRA más allá del nivel
GATILLO      una vela ENVOLVENTE, la siguiente a la que rompe o la de después.
             Si no aparece en esas dos, no hay operación.
ENTRADA      al cierre de la envolvente
STOP         al otro lado de la vela ANTERIOR a la envolvente

si rompe el MÍNIMO  ->  COMPRA, objetivo el MÁXIMO de Asia
si rompe el MÁXIMO  ->  VENTA,  objetivo 1:2
```

Sobre la asimetría del objetivo, sus palabras: *«entro en ventas buscando el 1:2
porque hasta dónde llega es incierto y no siempre llega al mínimo, pero sí al
1:2»*. Se implementa tal cual: no se corrige ni se simetriza.

## Lo que hay que decidir, y se decide ahora

| | decisión | por qué |
|---|---|---|
| Qué es envolvente | **el cuerpo** de la envolvente cubre entero el cuerpo de la anterior, y va en dirección contraria | es la definición estándar. La variante que envuelve el rango completo se reporta como secundaria |
| Cuántas al día | **una**, la primera válida | es como se opera de verdad y evita contar dos veces el mismo día |
| Salida por tiempo | a mercado **al cerrar Londres**, las 14:00 | «solo operando Londres» |
| Coste | 1,2 pips ida y vuelta en EURUSD | el mismo de todo el proyecto. Se reporta bruta y neta por separado |
| Empate stop/objetivo en el mismo minuto | cuenta **stop** | conservador, como siempre |

## Los datos

```
DESCUBRIMIENTO   julio y agosto de 2026   ·  lo que él miró
PRUEBA PRINCIPAL 2020-01-01 a 2025-12-31  ·  seis años que nunca ha visto así
SECUNDARIO       enero a junio de 2026     ·  se reporta aparte
```

Agosto de 2026 no está en los datos y **no se pide**: ya lo ha mirado él, así que
no seria ciego.

## Lo que predigo

Escrito antes, y con la lección de la última vez: la anterior predicción mía
—que su filtro de H1 no aportaría nada— **falló en la dirección**. Puede volver a
pasar.

1. **El patrón existe en bruto.** Ventaja bruta positiva, entre **+0,05 y +0,25 R**.
2. **El coste pesará entre el 8 y el 20 %** del riesgo. El stop de M5 es pequeño.
3. **La neta saldrá entre −0,10 y +0,05.** Es decir: predigo que no llega, pero
   por poco.
4. **La rama del mínimo rendirá mejor que la del máximo**, porque su objetivo es
   estructural —el otro extremo de Asia— y no un múltiplo fijo.
5. **Aparecerá en menos de la mitad de los días.** La exigencia de envolvente en
   dos velas se lleva muchos.

## Qué cuenta como éxito

Sobre **2020-2025**, con el error estándar del bootstrap por bloques
(`BC_08` §3), no el ingenuo:

```
la R neta, agrupando las dos ramas, con el IC del 95 % excluyendo el cero
por arriba
```

Se reportan las dos ramas por separado y las dos definiciones de envolvente, o
sea cuatro celdas. Umbral de Bonferroni con cuatro contrastes: **|z| > 2,50**.
La celda principal —las dos ramas juntas, envolvente por cuerpo— se juzga por su
intervalo, declarado aquí.

## Qué cuenta como fracaso

Que el intervalo incluya el cero. En ese caso **no se busca una variante que sí
funcione**: se reporta y se para. Ya sabemos cómo acaba eso.
