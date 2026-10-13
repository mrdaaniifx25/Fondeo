# El plan bajo las reglas de FundingPips

`bt/reglas.py`. No se pueden verificar sus reglas desde aquí (la política de red
sólo deja pasar GitHub; `fundingpips.com` da 000). Así que en vez de fiarme de
mi memoria, se calcula el plan bajo **tres juegos de reglas**, del más blando al
más duro, y se busca la escala óptima bajo cada uno.

```
  A · lo que simulé          +8 % / +4 %   caída 10 %   diaria 5 %
  B · FundingPips 2 fases    +8 % / +5 %   caída  8 %   diaria 4 %
  C · más duro aún          +10 % / +5 %   caída  6 %   diaria 4 %
```

## El resultado

Cuatro cuentas de 10.000 €, 48 meses, 6.000 carreras por celda.

```
  MUESTRA COMPLETA                escala óptima   llega a 300 €   renta mediana
  A · lo que simulé                     4×              98,7 %          484 €
  B · FundingPips 2 fases               4×              94,9 %          410 €
  C · más duro aún                      4×              87,8 %          336 €

  SOLO 2013-2026 (el tramo flojo)
  A · lo que simulé                     5×              78,6 %          250 €
  B · FundingPips 2 fases               4×              53,4 %          150 €
  C · más duro aún                      4×              34,6 %           69 €
```

## Lo que esto dice

1. **La escala óptima es 4× bajo los tres juegos de reglas.** Endurecer el límite
   no mueve el óptimo; sólo baja lo que se saca de él. Eso hace que el plan sea
   robusto a que yo no conozca sus reglas exactas.
2. **Las reglas más duras cuestan 4 puntos de probabilidad y 74 €/mes**, no el
   plan: 94,9 % y 410 € frente a 98,7 % y 484 €.
3. **Lo que sí lo puede tumbar es el régimen**, no la fondeadora. En el tramo
   flojo la probabilidad cae del 94,9 % al 53,4 % y la renta de 410 a 150 €.
4. Por debajo de 3× y por encima de 5× se cae a plomo en todos los casos. **El
   apalancamiento correcto es estrecho y hay que respetarlo.**

## La condición que sigue sin verificar

`RESULTADOS_plan.md` y `RESULTADOS_carrera_fondeo.md` lo repiten: con un 18,7 %
anual, llegar a +8 % tarda unos cinco meses. **Si el reto tiene plazo máximo de
30, 60 o 90 días, este sistema no lo pasa nunca**, y ninguna de las tablas de
arriba sirve.

Él tiene cuenta en FundingPips. Lo puede mirar en dos minutos.
