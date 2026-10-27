# Preregistro · el simulador

Escrito el 28 de agosto de 2026, **antes** de generar los casos. Fija cómo se
eligen los días y qué se va a medir, para que ni la selección ni el análisis se
puedan tocar después de ver las respuestas.

## Qué se prueba

Si su criterio de entrada, aplicado sin saber lo que viene después, bate al
33,3 % que da la geometría de un 1:2.

Es la primera vez en todo el proyecto que se mide **a él** y no a una regla
mecánica. Su agosto no vale como prueba: en TradingView gratis no hay repetición
y todo lo que marcó lo marcó con las velas siguientes a la vista.

## Cómo se eligen los días

- **Universo**: todos los días hábiles de **2024-01-01 a 2025-12-31** con rango
  de Asia válido (al menos 60 velas de un minuto antes de las 08:00 y rango
  mayor que cero) y con al menos un toque del alto o del mínimo de Asia entre
  las **08:20 y las 11:30**, hora de Madrid.
- **Muestreo**: 100 días **al azar sin reemplazo**, `numpy.default_rng(20260828)`.
- **Sin filtrar por nada más.** No se mira si el patrón dispara, ni si acabó en
  TP o en SL, ni si el día fue bueno. La lista de días queda fijada antes de
  mirar ningún resultado y se guarda en `data/simulador_dias.csv`.

## Qué ve él

- Velas de 5 minutos desde las 04:00 hasta el punto actual, y ni una más.
- El alto y el mínimo de Asia dibujados.
- Un gráfico de H1 y otro de M15 hasta el mismo instante, para que juzgue el
  contexto él mismo. **No se le muestra ninguna etiqueta de «a favor» o «en
  contra»**: eso sería darle el filtro ya masticado.
- El caso arranca en el primer toque del nivel a partir de las 08:20 y puede
  avanzar vela a vela hasta las 11:30.

## Qué NO ve

- Ninguna vela posterior a su punto actual.
- Ningún resultado, ni suyo ni ajeno, **hasta que termine los 100 casos**.
- El fichero de la página no contiene datos posteriores a las 11:30 ni ninguna
  resolución: las operaciones se resuelven aquí, después, con los datos M1.

## Qué se mide, y con qué umbral

**Principal**: el porcentaje de acierto de sus entradas, resueltas con stop y
objetivo tal como él los ponga, contra el **33,3 %** geométrico.

Se firma la dirección: la predicción es que **será mayor**.

Potencia calculada de antemano, α = 0,05 a una cola:

```
  detectar un 65 % ->  20 entradas
  detectar un 57 % ->  30 entradas
  detectar un 50 % ->  60 entradas
  detectar un 45 % -> 125 entradas
```

Con 100 casos y una tasa de entrada del 50 % salen unas 50 entradas: alcanza
para un 50 % de acierto y sobra para un 57 %.

**Secundarios, declarados ya para que no sean pesca posterior:**

1. Neto en R con el coste real de 1,43 pips.
2. Acierto de las entradas donde H1 y M15 iban a favor, contra el resto.
3. Comparación de sus entradas contra los disparos de la regla mecánica en esos
   mismos 100 días — es decir, si su selección aporta algo sobre la regla.
4. Lectura de los motivos que escriba al pasar.

## Lo que este test no puede demostrar

- No hay dinero ni prisa: es más fácil que operar de verdad.
- Él ya conoce el hallazgo de H1 de esta misma conversación, así que mide su
  criterio **de hoy**, no el de agosto.
- Un resultado malo no prueba que no sepa operar en real; uno bueno sí es
  evidencia fuerte, porque no hay forma de mirar el futuro.
