# Resultado · lo más simple que se puede defender

Pre-registro: `docs/PREREGISTRO_lo_simple.md`, escrito **antes** de simular.
Código: `bt/lo_simple.py`. 20.000 cuentas por celda, tope 300 días hábiles.

**Esto no es un backtest de una entrada.** Supone que la entrada no tiene
ventaja —lo único que tres meses de medición han establecido— y optimiza lo
otro: sobrevivir el examen. Es un problema de varianza y de límites, y ése sí
se puede resolver.

---

## Veredicto en tres líneas

1. **Pasar las dos fases con ventaja cero: 35,8 %.** La cuenta fue gratis, así
   que intentarlo tiene valor esperado positivo. Hazlo.
2. **Una cuenta fondeada de 10.000 € con ventaja cero paga 859 € EN TOTAL,
   para siempre, y luego revienta.** No depende del tamaño de posición ni de
   la política de retiro. Está medido en seis configuraciones y coincide con
   el teorema.
3. **Para sacar 300 €/mes de esos 10.000 hace falta una ventaja de +0,149 R
   por operación** (41,6 % de acierto a 1:2). Lo mejor que he medido en tres
   meses es 0,00.

---

## 1 · El motor es correcto

Antes de creerme nada, el control: con ventaja cero la probabilidad de hacer
+8 % antes de −10 % debe ser, por el teorema de la barrera, 10/(8+10) =
**55,6 %**.

```
  simulado   55,1 %
  teórico    55,6 %
```

Y desactivar el límite diario del 3 % no cambia nada (35,8 % → 35,8 %), lo que
dice algo importante que viene ahora.

## 2 · La rejilla es PLANA, y sólo hay una regla

```
  % que pasa LAS DOS fases · ventaja cero
   ops/día     0,25%     0,50%     0,75%     1,00%     1,50%     2,00%
         1      3,3%     26,2%     34,8%     35,2%     34,4%     32,8%
         2     12,5%     34,1%     35,0%     33,9%      3,7%         —
         3     20,8%     35,5%     34,8%      4,4%         —         —
         4     25,4%     35,2%      5,3%         —         —         —
```

Desde 0,50 % hasta 2,00 % **da todo lo mismo: 33-35 %.** No hay nada que
afinar. Lo que sí hay es un acantilado: cuando `ops/día × riesgo` llega al 3 %
del límite diario, se cae a **3,7 %**. Y arriesgar de menos (0,25 %) también
mata, porque el coste en R es fijo y hacen falta cuatro veces más operaciones
para llegar al objetivo: **3,3 %** con una al día.

> **La única regla de tamaño que importa: `ops/día × riesgo` nunca por encima
> del 2 %.** Todo lo demás dentro de ese margen es indiferente.

## 3 · Me equivoqué en lo que había predicho

Declaré antes de simular que «parar tras la primera pérdida» sería la mejor
regla de cierre de día, por varios puntos. **Es la peor.**

```
  riesgo 0,50 % x 3 ops/día      fase1   LAS DOS  días med  mu.diaria  mu.total
    sin regla                    54,5%     35,5%        74       0,0%     64,0%
    parar tras 1ª pérdida        51,5%     30,4%       123       0,0%     59,6%
    parar tras 1ª ganancia       55,1%     35,2%       102       0,0%     61,3%
    parar al tocar ±2R           53,9%     34,8%        85       0,0%     63,7%
```

El motivo está en la columna `mu.diaria`: **0,0 %.** En la celda buena el
límite diario del 3 % **no mata a nadie**. El que mata es el −10 % total, que
se lleva al 64 %. Así que recortar la varianza del día no te salva de nada —
sólo alarga la carrera (74 días → 123) y te hace pagar más coste total.

**La gestión del día no es gratis.** Cada día extra son más operaciones y más
diferencial pagado.

## 4 · La sensibilidad a la ventaja es brutal

Misma celda, cambiando sólo la ventaja por operación:

```
     ventaja R  acierto   fase1   LAS DOS  días med
         -0,05    35,0%   33,8%     16,3%        88
         -0,02    36,0%   46,4%     27,2%        91
         +0,00    36,7%   55,1%     35,8%        92
         +0,02    37,3%   64,2%     46,3%        93
         +0,05    38,3%   75,9%     60,8%        89
         +0,10    40,0%   89,2%     81,1%        77
```

**Dos céntimos de R por operación valen once puntos de aprobación.** Esto es lo
que hace que merezca la pena seguir buscando ventaja y no merezca la pena
seguir afinando parámetros de tamaño.

## 5 · El teorema: cuánto paga en total una cuenta fondeada

Con ventaja cero el saldo es una martingala. El teorema del muestreo opcional
dice que lo que se retira **en total** antes de reventar es el colchón —10 % de
10.000 = 1.000 €— por el reparto del 80 % = **800 €**. Y que **no depende** del
tamaño de posición ni de la política de retiro.

```
    riesgo  ops/día   retiro   total EUR   revienta
     0,25%        4     100%         826     100,0%
     0,50%        4     100%         859     100,0%
     1,00%        2     100%         877     100,0%
     2,00%        1     100%         886     100,0%
     0,50%        4      50%         847     100,0%
     0,50%        4       0%           0      89,0%
```

Seis configuraciones, seis veces el mismo número. (Queda por encima de 800
porque la cuenta se pasa un poco del −10 % al morir; cuanto mayor el tamaño,
mayor el exceso: 826 → 886, monótono. El teorema acierta incluso en la
dirección del error.)

**Una cuenta fondeada sin ventaja no es un sueldo. Es un billete de 850 €
pagado a plazos.**

## 6 · La cuenta de la servilleta

10.000 € · riesgo 0,50 % · reparto 80 % → **40 € por cada R**. Con ~50
operaciones al mes:

```
    para 300 EUR/mes hace falta una ventaja de +0,149 R   (acierto 41,6 % a 1:2)
    para 500 EUR/mes                          +0,248 R    (acierto 44,9 %)
    para 750 EUR/mes                          +0,372 R    (acierto 49,1 %)
```

Y lo que de verdad se cobra, simulado con la mortalidad incluida:

```
     ventaja R   EUR/mes  P(mes>=300)  revienta 12m
         -0,02        56         8,0%         98,0%
         +0,00        70        10,0%         96,4%
         +0,05       117        17,1%         87,8%
         +0,15       261        38,7%         48,8%
```

**Su objetivo de 300-750 €/mes no es imposible. Es imposible sobre 10.000 €.**
La ventaja necesaria escala con 1/capital: los mismos 300 €/mes sobre una
cuenta fondeada de 100.000 necesitan **+0,015 R**, diez veces menos. El camino
realista a esa cifra es cuenta más grande, no estrategia mejor.

## 7 · Y entonces, ¿el vídeo de ayer tenía razón?

Sí, y aquí está medido. Misma celda, cambiando sólo cuánto del beneficio se
retira cada mes:

```
     ventaja R  retiro 100%  retiro 50%  retiro 25%
         +0,00         859         847         823
         +0,02        1066        1443        2061
         +0,05        1487        4899        6127
         +0,09        2314       18116       11876
```

Con ventaja cero las tres columnas son **el mismo número**. Con ventaja, dejar
crecer el colchón en vez de vaciarlo multiplica el total por tres o por cuatro.
(En la última fila el tope de 240 meses de la simulación recorta la columna del
25 %; a esa altura ya no es una medición limpia.)

> **La gestión de riesgo multiplica una ventaja. No la crea.** Es un factor, no
> un sumando. Por eso el vídeo es correcto y a la vez no resuelve su problema.

---

## 8 · Lo que sí tiene que hacer, entonces

Está en `docs/LO_SIMPLE.md`, en una página y sin alternativas.
