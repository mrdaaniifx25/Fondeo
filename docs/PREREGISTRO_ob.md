# Preregistro · el order block de M5 y la vela de M1

Escrito antes de medir nada. Sale de su propia descripción, la más clara que ha
dado en cinco bloques:

> «me fijo visualmente en H4, miro el liquidity sweep de la vela que forma el
> rango, luego en M15 miro que vaya a la misma dirección, en M5 espero el OB y en
> M1 ejecuto en la vela envolvente o en la que rompe ese OB»

Cuatro piezas. **Tres están medidas y dos de ellas no separan nada** (el CRT de
H4: ninguno de ocho contrastes llega al umbral; la dirección de M15: p = 0,14).
La cuarta, el **order block de M5**, no se ha medido nunca sobre sus entradas.

Y hay un error mío peor: los 16 patrones de vela los medí **en la vela de M5**.
Él dice que ejecuta **en M1**. La envolvente que él ve puede no ser la que yo
miré.

## Lo que se mide

**Universo**: sus **223 entradas** de los cinco bloques, contra todas las velas
de M5 de esos mismos 164 días en las que tenía las manos libres y no entró.

### 1 · Order block en M5

```
OB ALCISTA en la vela i   i es bajista (cierre < apertura), y dentro de las
                          3 velas siguientes el precio CIERRA por encima de
                          su maximo. Es la ultima vela bajista antes del
                          impulso.
OB BAJISTA                lo simetrico.
ZONA                      dos definiciones, las dos se reportan:
                            completa  [minimo, maximo] de la vela
                            cuerpo    [min(o,c), max(o,c)]
VIGENTE                   hasta que el precio vuelve a entrar en la zona.
                          Solo cuentan los OB formados en las ultimas 24
                          velas de M5 (dos horas).
```

Contraste: **¿su precio de entrada cae dentro de un OB vigente de su misma
dirección, más a menudo que las velas de control?**

### 2 · La vela de M1 en el minuto exacto de la entrada

Los mismos 16 patrones del PDF de IG, más el tamaño del cuerpo y el tipo de
cierre, calculados sobre la **vela de M1 en la que entra** y las dos anteriores.
Y en concreto: **¿es una envolvente?** ¿Rompe el máximo o el mínimo de la vela
anterior?

## Predicción firmada

1. **Sus entradas caerán dentro de un OB de M5 más que los controles**, pero
   menos de lo que él cree: entre el 25 % y el 45 % de las suyas, contra un
   15-25 % de base. Diferencia real pero no enorme.
2. **El OB no separará sus ganadoras de sus perdedoras.** Es lo que ha pasado
   con todo lo demás: describe dónde mira, no qué gana.
3. **La envolvente en M1 aparecerá en menos de la mitad de sus entradas.** En M5
   salió en el 13 %; en M1 espero más, entre el 20 % y el 45 %, pero no la
   mayoría.
4. **El cuerpo grande en M1 volverá a ser malo**, en la misma dirección que el
   hallazgo de M5 (≥ 80 % del rango, acierto por debajo del 50 %).
5. Juntando OB + envolvente + dirección de M15, **cubriré menos del 25 % de sus
   223 entradas**. Su método, tal como lo describe, no describe lo que hace.

La 5 es la que de verdad se pone a prueba. Si sus cuatro piezas juntas cubren la
mayoría de sus entradas, **me he equivocado en cinco bloques** y la receta
siempre estuvo ahí.

## Umbral

Exploratorio y declarado como tal. Seis contrastes: **p < 0,008** (Bonferroni).
Y para el 5, el número se reporta tal cual: qué porcentaje de sus 223 entradas
cumple su propia descripción.

---

# Anexo · su definición, dicha por él

> «el OB es el cuerpo de la última vela antes del movimiento alcista, me marco
> esa vela de M5 y en M1 cuando la rompe con cuerpo entonces es cuando entro»

**Mi medición anterior preguntaba lo contrario de lo que él hace.** Yo medí si su
entrada cae *dentro* de la zona del OB. Su regla es entrar cuando el precio la
**rompe**, así que en el momento de entrar está fuera por definición. El −2,61
de antes no dice nada sobre su método.

## La regla, como la describe

```
OB          el CUERPO de la ultima vela de M5 cerrada
ROTURA      una vela de M1 CIERRA pasado ese cuerpo -no vale la mecha-
DIRECCION   la de la rotura
ENTRADA     al cierre de esa vela de M1
```

Esto explica algo que llevaba cinco bloques sin explicar: **por qué entra en
minutos arbitrarios** —08:32, 09:41, 10:13— y no en los cierres de M5. No espera
a que cierre la vela de M5: entra en el minuto en que M1 atraviesa el cuerpo de
la anterior.

## Dos lecturas, las dos se miden

```
A · DIRECTA    la vela de M1 cierra pasado el cuerpo de la ultima M5 cerrada.
B · CON VUELTA idem, pero exigiendo que antes el precio hubiera vuelto dentro
               de ese cuerpo (mitigacion) tras un impulso previo.
```

## Predicción firmada

1. La lectura **A cubrirá más del 50 %** de sus 223 entradas. Es la primera vez
   que predigo que una descripción suya sí describe lo que hace, y lo hago
   porque la geometría encaja: entra en minutos sueltos y eso solo tiene sentido
   si el gatillo es de M1.
2. Pero **A no será selectiva**: la misma condición se cumplirá en más del 30 %
   de los minutos de control, así que describe el gatillo, no la elección.
3. **B cubrirá menos del 20 %.**
4. La regla mecánica pura —entrar en cada rotura de A— **saldrá negativa**, con
   el stop pegado y el coste al 25-40 % del riesgo.

## Umbral

Cuatro contrastes, **p < 0,0125**. Y para la 1 y la 3, el número se reporta tal
cual: qué porcentaje de sus entradas cumple cada lectura.
