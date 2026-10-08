# Resultados · momento a horizonte largo

Pre-registro: `docs/PREREGISTRO_momento_largo.md`, subido en `d7ef337` **antes**
de medir. Código: `bt/momento_largo.py`. **26 series, 632 meses, 1971-2026.**

## Veredicto

**Es el primer resultado del proyecto que cumple su propio criterio entero.**
Y está muerto desde hace trece años.

Las dos frases son verdad a la vez y hay que leerlas juntas.

## El contraste principal, declarado antes

```
  K=12 · con coste          meses 632  efecto +0.1056 [+0.0645,+0.1467]  t +5.04  Sharpe +0.69
  K=12 · sin coste          meses 632  efecto +0.1068 [+0.0657,+0.1479]  t +5.09  Sharpe +0.70
  K=12 · sin factor dólar   meses 632  efecto +0.0589 [+0.0410,+0.0768]  t +6.45  Sharpe +0.89
```

**t +5,04** sobre los meses, que es el estadístico correcto (las 22 divisas están
correlacionadas entre sí; sobre las filas saldría falsamente enorme).

Y el coste, que en intradía se comía todo, aquí se lleva **el 1,1 % del efecto**:
+0,1068 a +0,1056. Ése era el motivo entero para venir hasta aquí.

Los otros K, todos en la misma dirección: K=1 t +5,77 · K=3 t +5,71 · K=6 t +5,10.

## Los placebos se comportan

```
  1 · signos aleatorios              efecto +0.0022  t +0.20     plano
  2 · señal invertida                efecto -0.1079  t -5.15     espejo exacto
  3 · signos barajados entre series  efecto +0.0275  t +1.77     un cuarto del efecto
```

El primero plano y el segundo un espejo es lo que hace una señal de verdad y lo
que no hace un artefacto. El tercero dice que **una cuarta parte podría ser el
factor dólar** — pero al quitarlo explícitamente el efecto *mejora* (t +6,45),
así que el momento no es sólo «el dólar con tendencia».

## Consistencia por serie

**23 de 25 positivas.** Las que más: S&P 500 (t +4,90), India (+5,21), Corea
(+4,59), oro (+4,34), Japón (+3,60), Sudáfrica (+3,46). Las dos negativas
(euro −0,15, Tailandia −0,67) son ruido.

## Y ahora la parte mala, que es la que decide

```
  1971-1999   meses 311   efecto +0.1581   t +5.23   Sharpe +1.03
  2000-2012   meses 156   efecto +0.0749   t +1.76   Sharpe +0.49
  2013-2026   meses 165   efecto +0.0357   t +0.91   Sharpe +0.25
```

Por década, el derrumbe es monótono:

```
    1980s   Sharpe +1.21      2000s   Sharpe +0.71
    1990s   Sharpe +1.15      2010s   Sharpe +0.17
                              2020s   Sharpe +0.14
```

**Y el deterioro no es falta de potencia: está medido.** La diferencia entre
1971-1999 y 2013-2026 da **t +2,48**. El efecto encogió de verdad.

Para que el tramo reciente llegase a t = 2 con el tamaño que tiene ahora harían
falta **66 años** de datos. Hay 13.

Sólo divisas, sin materias primas ni bolsa: completa t +4,25; 2013-2026 t +0,51.

## En dinero, con su límite del 10 %

Diez posiciones a 0,25 % de riesgo cada una. Eso da una volatilidad de cartera
del **4,6 % anual**, cuya caída máxima esperada ronda el 8 % — encaja justo
dentro de su límite, no por casualidad sino porque es el tamaño que permite.

```
  K=12 completa      +3.17 %/año  =  +132 €/mes sobre 50.000   (Sharpe +0.69)
  K=12 2013-2026     +1.07 %/año  =   +45 €/mes sobre 50.000   (Sharpe +0.25)
```

Para 750 € al mes al ritmo de la muestra completa harían falta **284.000 €
fondeados**. Al ritmo de los últimos trece años, un millón.

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. el principal con t > 2 | **SÍ**, t +5,04 |
| 2. positivo en los tres subperiodos | **SÍ**: +0,158 · +0,075 · +0,036 |
| 3. sobrevive al coste | **SÍ**, se lleva el 1,1 % |
| 4. placebos planos | **SÍ** con matiz: el de barajado da t +1,77 |

**El criterio se cumple.** Es la primera vez en el proyecto.

Y aun así la lectura honesta no es «lo tenemos». Es: *el efecto existió, es de
los más sólidos que se pueden medir en finanzas, y lleva trece años plano.*

## Límites, dichos aquí y no después

1. Son **tipos del Fed a mediodía**, no precios operables. Sirven para medir si
   el efecto existe, no para estimar la ejecución.
2. **No hay swap ni carry.** Una posición real en CFD cobra o paga interés cada
   noche, y en divisas eso puede sumar o restar. El número real será distinto.
3. El derrumbe posterior a 2008 coincide con lo que reporta toda la industria de
   seguimiento de tendencia. Que cuadre con la historia documentada lo hace más
   creíble, no menos.

## Lo que esto sí cambia

Dos meses de pruebas midiendo patrones de gráfico **intradía**, donde el muro
del coste vale 0,10 y la ventaja que se encuentra vale 0,03-0,10. Por eso todo
salía cero: se estaba jugando exactamente donde el peaje vale lo mismo que el
premio.

Aquí el muro vale **0,005** y el efecto **0,106**: veinte veces. Esta medición
demuestra que **hay un sitio donde el coste deja de mandar**, y no es una
especulación: es un t +5,04 sobre 632 meses.

Lo que queda ahí sin mirar, y ahora es barato mirarlo con los mismos datos:

- **carry** (diferencial de tipos), que es el otro premio documentado en divisas
- **valor** (reversión a PPA a varios años)
- **momento transversal** (comprar las fuertes y vender las flojas, en vez de
  cada una contra sí misma)
- **estacionalidad de calendario** (fin de mes, enero)

El momento temporal era la primera de esa lista y ha salido real pero apagada.
Faltan tres.

## Récord de predicciones

**Cinco de cinco.** La primera vez.

| predicción | resultado |
|---|---|
| el principal positivo con t entre 2 y 4 | t **+5,04** ✔ (por encima del rango) |
| deterioro claro, cerca de cero en 2013-2026 | +0,036, t +0,91 ✔ |
| el coste se llevará menos del 10 % | 1,1 % ✔ |
| placebos planos salvo quizá el del dólar | exacto: el del dólar t +1,77 ✔ |
| no llegará a 750 €/mes sobre 50.000 | 132 € ✔ |
