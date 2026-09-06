# Resultados · la regla escrita, corrida sobre seis años

Pre-registro: `PREREGISTRO_asia_nivel.md`, commit `9f77f29`, escrito antes de
correr nada. Ejecutado una vez. Fecha: 2026-08-28.

## Veredicto: la regla escrita no funciona

Prueba principal, **2020-2025**, 2.080 disparos en 1.441 días:

| | valor |
|---|---|
| disparos | 347 al año · 1,44 por día |
| riesgo mediano | 7,0 p — el spread es el **17 %** del riesgo |
| acierto | **30,8 %** frente a 33,3 % de geometría pura |
| por operación | bruta −0,057 · neta −0,356 |
| **por día** | bruta +0,024 (z +0,72) · **neta −0,282 (z −7,55)** |

El umbral pedía neta diaria > 0 con z ≥ 2,0. Sale **−0,282 con z −7,55**.

En 2026 enero-julio, lo mismo: bruta +0,079 por día, neta −0,321 (z −2,01).

Reparto en 2020-2025, por si servía de algo:

| | n | %TP | bruta | neta |
|---|---|---|---|---|
| gatillo A | 293 | 35,2 % | +0,055 | −0,902 |
| gatillo B | 1.787 | 30,1 % | −0,076 | −0,266 |
| nivel alto | 1.051 | 32,0 % | −0,022 | −0,322 |
| nivel mínimo | 1.029 | 29,6 % | −0,093 | −0,389 |
| compras | 1.032 | 32,5 % | −0,006 | −0,294 |
| ventas | 1.048 | 29,2 % | −0,107 | −0,416 |

Nada por encima de la geometría en ninguna partición.

## Pero esto NO desmiente su agosto, y hay una razón concreta

Sobre **sus mismos días de agosto**, la regla dispara 17 veces y da **−0,300 R
por día en bruto**. Él hizo **+0,979 en neto**. Así que la regla y él no están
haciendo lo mismo.

Cuánto no lo están haciendo:

> De sus 16 operaciones de agosto, la regla dispara la misma —misma dirección y
> entrada a menos de 3 pips— en **4**.

**Doce de dieciséis no las toca.** Y mirando el detalle día a día se ve por qué:

| | la regla | él |
|---|---|---|
| hora del disparo | **08h en 10 de los 15 días** | de 08:20 a 11:20, mediana 09:30 |

La condición de armado que escribí —«dispara en el primer toque del nivel y se
desarma»— coge sistemáticamente **el toque de la apertura de Londres**. Él no
opera ése. Espera.

Eso es un fallo de la regla que yo escribí, no de lo que él hace. Su gatillo está
verificado en 16 de 16; lo que no está capturado es **qué le hace esperar**.

## Lo que queda en pie y lo que no

- **La regla escrita: archivada.** Neta −0,282 por día con z −7,55 sobre 1.441
  días. No hay ambigüedad.
- **El gatillo: sigue verificado.** A o B se cumplen en sus 16 de 16.
- **Su agosto: intacto.** No lo toca este resultado. 18 TP y 6 SL, y las 16 con
  datos verificadas al minuto una a una.
- **Lo que falta, ahora nombrado con precisión:** no es la dirección —eso está
  resuelto, la da la vela— sino **cuál de los disparos toma**. La regla ofrece
  1,4 al día y él toma 1,6, pero sólo coinciden en 4 de 16.

En el pre-registro quedó escrito, antes de correr: *«un resultado plano aquí no
desmiente su agosto, y uno bueno no lo confirma: son dos cosas distintas»*. Se
cumplió, y por el motivo previsto — él no toma todos los disparos.

## Lo siguiente

La pregunta ya no es cuál es su regla. Es **por qué se salta el primer toque**.
Y hay un sitio donde la respuesta se ve sola: los 12 disparos de agosto que la
regla tomó y él no.

## Ficheros

```
bt/asia_nivel.py      la pasada, ejecutada una vez
data/asia_nivel.csv   2.262 operaciones resueltas, 2020-2026
```
