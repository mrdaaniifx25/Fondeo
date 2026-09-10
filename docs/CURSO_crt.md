# Curso de CRT · índice

Ocho lecciones. Las que tienen artefacto son páginas interactivas; el resto se
dieron en conversación. Todo lo que se afirma aquí sale de las mediciones del
repositorio, no del material de los cursos.

| # | lección | formato | de dónde salen los números |
|---|---|---|---|
| 1 | Qué es un CRT y cómo se lee una vela de rango | conversación | `docs/CRT_H4_especificacion.md` |
| 2 | Las tres piezas: rango, manipulación, distribución | conversación | `docs/CRT_resumen.md` |
| 3 | Marcar el rango en su propia rejilla horaria | conversación | rejilla OANDA 01/05/09/13/17/21 UTC |
| 4 | **Dónde entrar** — las tres entradas, resueltas sobre 88 casos reales de 2026 | [artefacto](docs/leccion4_donde_entrar.html) · `bt/leccion4_datos.py` | `data/leccion4.json` |
| 5 | **Dónde va el stop** — excursión adversa medida, 16 niveles de colchón | [artefacto](docs/leccion5_donde_va_el_stop.html) · `bt/leccion5_datos.py` | `data/leccion5.json` |
| 6 | Los filtros de contexto, medidos sobre su setup exacto | conversación | `docs/RESULTADOS_crt_final.md` |
| 7 | **La criba de los 10 segundos** — calculadora de viabilidad | [artefacto](docs/leccion7_la_criba.html) | `docs/RESULTADOS_crt_temporalidad.md` |
| 8 | El registro: cómo medir si su propio criterio añade algo | pendiente | simulador, modo ciego |

## Un aviso sobre el marco

Las lecciones 4, 5 y 6 están dadas sobre **EURUSD en H4**. Esa elección fue
didáctica, no empírica: en H4 hay 348 operaciones al año, se ven muchos patrones
en poco tiempo, y es la rejilla que él tiene en pantalla.

**H4 es además el marco donde la aritmética dice que no.** Neta media −0,030 R,
sólo 2 de 5 instrumentos por encima de cero y los dos en +0,009 y +0,002, o sea
cero. El desglose y la comprobación de que su rejilla de TradingView da lo mismo
que la del estudio están en `RESULTADOS_rejilla_y_marco.md`.

Así que: H4 para aprender el mecanismo, sí. H4 para operarlo, no.

## La lección 7 en una línea

```
lo que te llevas = tu ventaja − coste ÷ stop
```

Con la mejor ventaja bruta medida en todo el trabajo (**+0,082 R**, constante en
las siete temporalidades probadas) y el coste medido en EURUSD (**1,43 pips**),
el stop mínimo por debajo del cual se pierde por división es **17,4 pips**.

Los dos avisos que van con la tabla de temporalidades, y que están escritos en el
propio artefacto:

1. La R neta **no** es la resta de las dos columnas anteriores. El coste de la
   tabla se calcula sobre el stop *mediano*; la neta está medida operación a
   operación, y las operaciones de stop pequeño pagan un peaje desproporcionado
   que la mediana esconde.
2. Que H12 y D1 salgan en verde no significa que estén resueltas. Se probaron
   siete temporalidades; la mejor —H12, neta +0,072— da z ≈ 2,35 cuando con siete
   contrastes hace falta |z| > 2,69. **No llega.** Lo que la tabla demuestra no es
   que H12 gane: es *por qué* los marcos pequeños pierden.
