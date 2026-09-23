# Resultados · probabilidad de pasar el reto con la estrategia mecanizada

Código en `bt/reto_fondeo.py`. Simulación con **la distribución real** de R neta
del modelo, no una aproximación.

Reglas supuestas, de un reto de dos fases sobre 10.000 €: fase 1 objetivo +10 %,
fase 2 +5 %, pérdida máxima total 10 %, pérdida máxima diaria 5 %, riesgo del 1 %
por operación, 4 operaciones al día. 20.000 simulaciones por escenario.

## La tabla

| escenario | R media | fase 1 | fase 2 | **las dos** | intentos |
|---|---|---|---|---|---|
| decil superior (pre-registrado) | −0,0644 | 33,3 % | 52,9 % | **17,6 %** | 5,7 |
| mejor corte medido (stop ≥10 p) | −0,0267 | 42,3 % | 59,5 % | **25,2 %** | 4,0 |
| si el coste bajara a 0,97 pips | −0,0020 | 48,7 % | 64,0 % | **31,1 %** | 3,2 |
| **ventaja CERO, moneda al aire** | 0,0000 | 49,2 % | 64,2 % | **31,6 %** | 3,2 |

## Lo que dice esa tabla, y es lo único importante

**La moneda al aire pasa el 31,6 %. La estrategia mecanizada, el 25,2 %.**

Mecanizar la estrategia no sube la probabilidad: la **baja seis puntos** respecto
a entrar al azar. Y es lógico, no es una paradoja: la esperanza sigue siendo
negativa, y el reto premia la varianza, no la habilidad. Un sistema con esperanza
ligeramente negativa deriva hacia el límite de pérdida más de lo que deriva hacia
el objetivo.

Ésa es exactamente la razón por la que el negocio del fondeo funciona.

Y el techo: con el coste arreglado a 0,97 pips se llega al **31,1 %**, que es la
moneda al aire. Para pasar de ahí haría falta esperanza positiva, y no la hay.

## Y lo que casi nadie calcula: qué pasa después de pasar

Con la cuenta ya fondeada y la mejor versión medida:

    llegar a +7,5 % (los 750 EUR de un mes) antes de reventar   49,6 %
    repetirlo seis meses seguidos                                1,49 %

**Pasar no es el objetivo. Mantener lo es.** Con esperanza negativa, una cuenta
fondeada es una fuga lenta: cada mes es una moneda al aire entre cobrar y saltar
el límite del 10 %, y seis caras seguidas salen una vez de cada sesenta y siete.

## En dinero

A 4 intentos de media y 55 € el intento: **220 €** para conseguir una cuenta
fondeada que luego tiene un 1,5 % de durar medio año dando 750 € al mes.

## Los avisos que hay que leer con esto

- El corte de "stop ≥10 pips" **no estaba pre-registrado** y es el escenario más
  favorable de los medidos. El pre-registrado da 17,6 %, no 25,2 %.
- Las reglas de cada firma cambian; hay que comprobar las del reto concreto.
- La simulación supone que la ventaja medida se mantiene hacia delante, que es
  ser generoso: en 2026 la neta del decil superior fue −0,205.
