# Resultados · el CRT en DAX dentro del horario del usuario

Pre-registro `5376608`, subido antes de medir. Código `bt/dax_horario.py`,
que reutiliza `bt/crt_por_temporalidad.py` sin reimplementar nada.
DAX (GRXEUR) 2023-2026, 3,6 años. Coste 1,6 puntos.

## Veredicto

**No cumple el criterio.** Nada de lo que cae dentro de su horario tiene neta
positiva.

| TF | tramo | n | al año | R bruta | IC95 | **R neta** |
|---|---|---|---|---|---|---|
| H1 | **dentro** | 1 442 | 403 | +0,062 | [−0,003, +0,127] | **−0,049** |
| H1 | fuera | 2 779 | 777 | +0,075 | [+0,018, +0,133] | −0,083 |
| H2 | **dentro** | 466 | 130 | +0,015 | [−0,103, +0,132] | **−0,051** |
| H2 | fuera | 1 517 | 424 | +0,068 | [−0,013, +0,150] | −0,036 |
| H4 | **dentro** | 317 | 89 | −0,046 | [−0,192, +0,099] | **−0,104** |
| H4 | fuera | 716 | 200 | +0,120 | [+0,001, +0,240] | **+0,052** |
| H8 | **dentro** | 129 | 36 | −0,094 | [−0,278, +0,089] | −0,145 |
| H12 | **dentro** | **0** | — | — | — | — |
| H12 | fuera | 239 | 67 | +0,050 | [−0,159, +0,258] | +0,016 |
| D1 | **dentro** | **0** | — | — | — | — |
| D1 | fuera | 180 | 50 | +0,118 | [−0,062, +0,299] | **+0,101** |

Los tres tramos con neta positiva —H4 fuera, H12 y D1— caen **todos fuera de
su horario**, y los tres tienen el cero dentro del intervalo.

## El hallazgo que no esperaba: es el anclaje, no el mercado

En H12 y D1 hay **cero** operaciones dentro de su horario. Y no es porque el
DAX no cotice: es por **cómo están ancladas las velas**.

`velas_ref` las ancla a la **01:00 de Nueva York**, que es la convención del
CRT canónico. En hora de Madrid:

```
H12  cierra a las 07:00 y a las 19:00     -> fuera de 08-12 y de 13-16
D1   cierra a las 07:00                    -> fuera
```

Por una hora. **Las velas de H12 cierran a las 07:00 y él empieza a las 08:00.**

Eso no es una propiedad del mercado, es una elección de rejilla que yo heredé
del estudio anterior. Y se puede cambiar.

## Lo que NO se puede hacer con eso

Probar anclajes hasta que uno dé positivo. Para H12 hay doce anclajes posibles;
elegir el mejor de doce es exactamente cómo se fabrica un falso positivo.

La pregunta legítima es otra: **¿es la ventaja del CRT invariante al anclaje?**
Si el patrón es real, debería salir parecido en los doce. Si sólo aparece en
uno, es ruido con suerte. Eso se mide **declarando los doce y publicando los
doce**, no quedándose con el bueno.

Queda como la siguiente prueba.

## Mi predicción, otra vez a medias

| predije | salió |
|---|---|
| bruta positiva y pequeña en varios marcos | ✅ H1 +0,071 · H2 +0,056 · H4 +0,069 · D1 +0,118 |
| neta negativa en H1-H4, cruzando en H8-D1 | ✅ casi: cruzó ya en H4 |
| intervalos demasiado anchos para concluir | ✅ |
| «casi todo caerá dentro de su horario» | ❌ **al revés**: en H12 y D1 cayó **cero** |

Fallé el mecanismo: me olvidé del anclaje. Cuarta predicción con un error.
