# Resultados · una cuenta de 10.000 y la pérdida limitada a la cuota

Pregunta del usuario: *«tiene que existir algo para una cuenta de 10k, algo que
SÍ funcione y no me genere 50 €/mes»*. Código: `bt/diez_mil.py`.
Rendimientos por remuestreo de los **632 meses medidos**
(`RESULTADOS_momento_largo.md` + `RESULTADOS_carry.md`). 30.000 carreras de 3 años.

## Primero, por qué 300 €/mes «conservando» la cuenta es imposible

```
  rentabilidad bruta necesaria ....... 45 % al año
  límite de caída .................... 10 %
  cociente rentabilidad/caída ........ 4,5
```

Para una estrategia con Sharpe S, la caída máxima esperada en un año ronda 1,75
veces la volatilidad anual, y rentabilidad = S × volatilidad. Así que
rentabilidad/caída ≈ S/1,75, y hacen falta:

```
   Sharpe    rentabilidad   €/mes sobre 10k
      1,0           5,7 %           38 €
      2,0          11,4 %           76 €
      3,0          17,1 %          114 €
      7,9          45,1 %          301 €
```

**Sharpe 7,9.** Medallion, el mejor fondo de la historia, opera en 2-3. No es que
no lo hayamos encontrado: no existe.

## La corrección: en una fondeada no se conserva la cuenta

Ése era el error de `RESULTADOS_carrera_fondeo.md`, que concluyó «hacen falta
100.000 €». Asumía conservar la cuenta.

**En una cuenta fondeada la pérdida está limitada a la cuota.** Revientas, pagas
89 € y compras otra. Eso hace racional un apalancamiento que con dinero propio
sería una locura.

```
  CUENTA DE 10.000 € · reto 89 € · 3 años · MUESTRA COMPLETA

  escala  caída hist.   %/año   retos   % gana   mediana €/mes   media   p75    p90
     1x        10 %      4,7 %    1,0    56,7 %          +3 €     +7€   +13€   +24€
     2x        20 %      9,3 %    1,3    87,1 %         +32 €    +35€   +54€   +74€
     4x        40 %     18,7 %    2,3    96,8 %         +89 €    +94€  +132€  +173€
     6x        60 %     28,0 %    4,8    95,3 %        +100 €   +111€  +160€  +218€
     8x        80 %     37,3 %   15,1    36,9 %         -17 €     -2€   +19€   +63€
    12x       120 %     56,0 %   36,0     0,0 %         -89 €    -89€   -89€   -89€
```

**El óptimo está en 4-6×**: mediana de 89-100 €/mes con el 95-97 % de las
carreras en positivo, comprando de 2 a 5 retos en tres años.

Por encima de 8× se cae por el precipicio: se revienta más rápido de lo que se
cobra, y a 12× no sobrevive ni una carrera de 30.000.

## El caso malo · sólo con los meses de 2013-2026

```
  escala   %/año   retos   % gana   mediana €/mes   media    p90
     2x     3,9 %    1,5    53,8 %          +2 €    +10€    +38€
     4x     7,8 %    2,7    79,6 %         +31 €    +40€   +101€
     6x    11,7 %    4,7    82,1 %         +44 €    +57€   +140€
     8x    15,6 %   12,6    36,1 %         -16 €     -1€    +56€
```

El óptimo sigue en 4-6×, y la mediana baja a **31-44 €/mes** por cada 10.000.

## La respuesta a su pregunta

```
                          para 300 €/mes hacen falta
  régimen completo   ->   ~ 35.000 € fondeados   (3-4 cuentas de 10k a 4-6×)
  régimen flojo      ->   ~ 90.000 € fondeados
```

Tres o cuatro cuentas de 10.000 corriendo el mismo sistema, que son unos
**300 € de cuotas** para arrancar y unas 8-20 recompras en tres años.

No son 50 €/mes, y no hacen falta 100.000 €. Pero tampoco sale de una sola
cuenta de 10k: ahí el techo son **89-100 €/mes**, y sólo estirando el
apalancamiento hasta cuadruplicar el límite de caída, contando con reventar la
cuenta unas dos veces cada tres años.

## Lo que no cambia

Varias cuentas con el mismo sistema están **perfectamente correlacionadas**: son
una sola cuenta grande partida en trozos. No hay diversificación en repartirla,
sólo el efecto de que cada trozo tiene su propia cuota y su propio límite —que
es justamente de donde sale la ventaja.
