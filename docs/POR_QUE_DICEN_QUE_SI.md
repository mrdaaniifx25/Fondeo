# Por qué dicen que el CRT funciona si no funciona

Pregunta del usuario, y es la que cierra el proyecto. No es una pregunta sobre el
mercado: es sobre **cómo se producen las afirmaciones**. Se contesta con material
de este repositorio.

---

## 1 · El patrón es real. La ventaja no. Nadie separa las dos cosas.

El precio **sí** barre niveles y **sí** se da la vuelta. No es una ilusión
óptica. Ocurre entre el 30 % y el 50 % de las veces según el objetivo que pongas.

El problema es que **ésa es exactamente la probabilidad de la barrera**:

```
  P(objetivo primero) = riesgo / (riesgo + recorrido)
```

Con 20.000 configuraciones de CRT medidas, el objetivo se alcanza el 33,7 % de
las veces contra un 33,3 % geométrico. **El patrón existe y está en su precio.**

«Funciona» y «tiene ventaja» son afirmaciones distintas. La primera es verdad.

## 2 · El gráfico lo confirma hacia atrás y no lo puede refutar hacia delante

Mirando atrás, los barridos que funcionaron **se ven**. Los que no, no parecen
configuraciones fallidas: parecen «el precio siguió», y uno no los cuenta como
CRT. No es mala fe, es que el ojo no etiqueta lo que no pasó.

Por eso 34 guiones de sesiones de este proyecto salieron planos y la impresión
visual seguía siendo que ahí había algo (`RESULTADOS_reloj.md`).

## 3 · Las adaptaciones lo vuelven irrefutable

Del vídeo del curso, textual:

> *«lo que tenemos que hacer en esta situación es **adaptarnos**... el rango de 4
> horas deja de ser este, ya se ha invalidado, y pasa a ser el siguiente»*

Si no sale, se mueve el rango al siguiente y se espera. **Una regla que se puede
reanclar después del hecho no puede equivocarse nunca.** Eso no es una
estrategia, es un relato que se ajusta al gráfico.

Medir obliga a congelar la regla antes. Es lo único que hace un pre-registro.

## 4 · Alguien siempre gana, y publica

`RESULTADOS_concurso.md`: 400 participantes, 20 días, mercado plano, **ventaja
exactamente cero**, apalancamiento 3×.

```
       1º     +154,0 %
       2º     +128,9 %
      10º      +83,0 %
  mediana       -5,2 %
```

Lo anunciado en el vídeo era 1º +186,3 % y 2ª +61,5 %. **Cabe de sobra dentro
del azar.** Y la mediana —el participante típico— pierde el 5,2 %. Ésa es la
columna que no se publica.

Y «siete de los diez primeros usaban mis estrategias» es **exactamente la media
esperada** si sus alumnos eran el 70 % de los 400. El vídeo no dice qué fracción
eran.

## 5 · Los meses buenos son reales y no prueban nada

Con R:R 1:2 y 33 % de acierto, un mes en positivo ocurre por azar
constantemente. Tres meses seguidos en verde es **la experiencia esperada** de
alguien sin ninguna ventaja.

Por eso «llevo tres meses ganando» se siente como prueba y no lo es. Para
distinguir habilidad de suerte hacen falta cientos de operaciones publicadas
**antes** de conocerse el resultado. Es lo único que vale, y es lo que nadie
muestra.

## 6 · El dinero no sale de operar

Formación, mentorías, Telegram, enlaces de afiliado a brókers y a cuentas de
fondeo. El negocio funciona **sin que la afirmación sea cierta**.

Y el detalle importante: el incentivo no es mentir. **El incentivo es no
comprobar.** Son cosas distintas y la segunda explica mucho más.

Nota de justicia: el autor del curso de CRT dice él mismo *«no soy experto en
CRT»*, *«tengo mi track récord auditado con **esas mismas** estrategias»* —no con
ésta— y *«los que ganan la Robbins Cup no utilizan ninguno de estos métodos»*.
**Ese vídeo es honesto.** Lo que le falta es el número.

## 7 · Y la razón que puedo afirmar con más autoridad: comprobarlo es dificilísimo

En **una sola semana** de este proyecto, intentándolo en serio, produje tres
resultados espectaculares y falsos:

| qué medí | qué salió | la causa |
|---|---|---|
| sistema EUR/USD intradía | acierto **69,3 %**, PF **2,61**, **+4.523 €/mes** | un signo mal: cada stop de un corto contaba como +1R |
| carry en divisas | **t +2,95** con recargo de bróker | el recargo entraba como ingreso en las cortas |
| punto óptimo de entrada | **z +4,98** sobre un umbral de 3,00 | el camino se medía desde antes de la entrada |

**Tres de tres eran errores míos.** Cero resultados espectaculares han
sobrevivido a la revisión.

Y fíjese en los números de la primera fila: acierto del 70 %, profit factor 2,6,
cuatro mil euros al mes. **Son exactamente los números que se anuncian.**

Conclusión que no es cínica sino la más generosa posible: **la mayoría no miente.
Tiene un fallo que no puede ver, y ningún mecanismo que se lo diga.** Si yo, con
pre-registro, placebos y sesenta documentos de disciplina, me equivoqué tres
veces en una semana, alguien con una plantilla de TradingView y ningún control se
equivoca permanentemente y se lo cree.

Lo que separa un caso del otro no es la inteligencia ni la honestidad. Es tener
un procedimiento que pueda decirte que no.

## Qué cerraría esta discusión, por si alguien la trae

Una sola cosa, y vale para cualquier estrategia:

**Un historial auditado, publicado operación a operación, anunciado antes de
conocerse el resultado, de varios cientos de operaciones.** Sin selección de
periodo y sin reanclar reglas.

Para el CRT no existe ninguno. No es que esté escondido: es que **nadie lo ha
publicado**, y el propio autor del curso dice que el suyo es de otras
estrategias.

## Lo que este proyecto cierra, y lo que no

**Cierra**: CRT en M15, H1, H4 y D1, en EUR/USD, oro y DAX, a coste minorista y
ECN, en todas las combinaciones razonables de entrada, stop y objetivo
(`RESULTADOS_punto_optimo.md`: 0 de 220 celdas positivas). Veinte documentos.

**No cierra**: horizontes de días o semanas, instrumentos distintos a estos tres,
ni la posibilidad de que alguien tenga información que no está en el gráfico.

Lo que sí puede decir con los números en la mano: **lo que se enseña en los
vídeos, operado como se enseña, en estos instrumentos, no tiene ventaja.** Y la
razón por la que se dice lo contrario no requiere mala fe — sólo requiere no
tener un mecanismo que pueda refutarte.
