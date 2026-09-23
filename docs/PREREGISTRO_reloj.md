# Pre-registro · el reloj, sin patrón ninguno

Escrito y subido ANTES de medir. 22/09/2026.

## El hueco

Hay **34 scripts de sesiones** en este proyecto. Todos preguntan lo mismo:
*«cuando el precio barre un nivel Y cierra dentro Y está en tal sesión…»*. Son
condicionales, y todos han salido planos.

**Nunca se ha hecho la pregunta incondicional**: ¿qué hace el precio, de media,
en cada hora del día? Sin patrón, sin nivel, sin barrido. Sólo la hora.

Importa porque es **el mismo tipo de efecto** que el momento y el carry —
sistemático, incondicional, sin nada que ajustar — que es el único tipo que ha
funcionado en todo el proyecto. Los patrones condicionales tienen mil formas de
sobreajustarse. «Compra a las 9, vende a las 17» no tiene ninguna.

## Qué se mide

Datos: **EURUSD** (2.055.684 minutos, 2021-2026), **DAX** y **oro** (2023-2026).
Hora de Madrid.

**1 · El reloj hora a hora.** Rendimiento medio de cada una de las 24 horas, en
unidades del ruido de esa hora. Con ~1.400 observaciones por hora en EURUSD.

**2 · Las sesiones enteras.** Asia 00-08, Londres 08-14, Nueva York 14-23.
Comprar al abrir la sesión y vender al cerrarla, todos los días.

**3 · La noche contra el día.** Comprar al cierre y vender a la apertura, contra
lo contrario. En índices de bolsa esto es un efecto grande y documentado; en el
DAX se puede mirar.

**4 · El día de la semana**, que es el mismo tipo de pregunta.

**El contraste PRINCIPAL, declarado ahora: la sesión de Londres completa
(08:00-14:00) en EURUSD, comprada todos los días.** Es la que él opera y la que
tiene la historia más larga. Los demás son secundarios.

## El muro, calculado antes

De `RESULTADOS_muro_horizonte.md`, la ventaja mínima para cubrir el coste:

```
  horizonte   EURUSD     oro      DAX
  1 hora      0,1076   0,0353   0,0156
  4 horas     0,0539   0,0181   0,0078
  1 día       0,0226   0,0070   0,0032
```

Una sesión de 6 horas está entre las dos primeras filas: el muro en EURUSD es de
**unos 0,044** en unidades de ruido. Para una hora suelta es **0,108**.

**Cualquier efecto por debajo de eso es cierto y no sirve.** Se publicará el
bruto y el neto, y lo que manda es el neto.

## El sesgo de selección, calculado antes

24 horas × 3 instrumentos = **72 celdas** en la prueba 1. El mejor de 72 sale
**2,42 errores estándar** por encima de la verdad sólo por azar. Con ~1.400
observaciones por hora, eso son **+0,065** en unidades de ruido — más que el
muro de una hora entera.

**Por eso el principal es una sesión concreta declarada arriba, y las 24 horas
son exploratorias.** Ninguna hora suelta contará como hallazgo, por buena que
salga, a menos que supere el muro Y el sesgo Y se repita en los dos periodos.

## Criterio

1. El principal (Londres en EURUSD) con rendimiento **neto > 0** y el IC95 sin
   tocar el cero, **y**
2. el mismo signo **partido por años**, no concentrado en uno, **y**
3. el mismo signo en **oro y DAX** para la misma sesión.

## Predicción

- **El principal saldrá plano.** La estacionalidad intradía en divisas está
  documentada sobre todo en **volatilidad**, no en dirección.
- **Habrá horas que parezcan buenas** —siempre las hay con 24 celdas— y ninguna
  pasará el muro de 0,108 después del sesgo de selección.
- **Lo único que puede salir de verdad es la noche contra el día en el DAX.**
  Es el efecto más robusto documentado en índices de bolsa. Le doy la
  probabilidad más alta de las cuatro, y aun así por debajo del 50 %.
- El día de la semana saldrá plano.
- Conclusión probable: **el reloj no tiene dirección, sólo tiene volumen**, y
  eso cierra la familia de sesiones del todo, esta vez por la puerta buena —
  habiendo hecho la pregunta simple y no sólo las complicadas.

Van dieciséis predicciones con errores. Ésta también puede fallar.
