# El muro no es una constante: baja con el horizonte

Código: `bt/muro_horizonte.py`.

## De dónde sale

El usuario objetó, con razón, que el proyecto estaba generalizando de más. Lo
medido hasta ahora es **intradía, en FX, a coste de minorista, en tres
instrumentos**. De ahí no se sigue nada sobre «el trading».

Y los propios datos lo dicen: el coste es **fijo** por operación, mientras que
el ruido crece con la raíz del tiempo. Así que la ventaja mínima necesaria para
empatar —el coste medido en unidades de ruido— se hace pequeña sola según
alargas el horizonte.

## La tabla

Ventaja mínima para no perder dinero, en unidades del ruido de ese horizonte:

| horizonte | EURUSD | oro | DAX |
|---|---|---|---|
| **1 hora** | **0,1076** | 0,0353 | 0,0156 |
| 4 horas | 0,0539 | 0,0181 | 0,0078 |
| 1 día | 0,0226 | 0,0070 | 0,0032 |
| 1 semana | 0,0104 | 0,0033 | 0,0014 |
| **1 mes** | **0,0053** | 0,0019 | **0,0007** |
| 3 meses | 0,0033 | 0,0011 | 0,0004 |
| 1 año | 0,0018 | 0,0006 | (sin histórico) |

Costes usados: EURUSD 1,43 pips · oro 0,35 unidades · DAX 1,6 puntos.
Horas de mercado, no de calendario.

**En EURUSD a un mes el muro es 20 veces más bajo que a una hora. En el DAX a
un mes es 150 veces más bajo que en EURUSD intradía.**

Esto explica por qué el seguimiento de tendencia en futuros —horizonte de
semanas y meses, decenas de mercados— puede ser un negocio con resultados
auditados, y esto otro no. No son estrategias distintas enfrentadas: es el
mismo muro a dos alturas distintas.

## El pero

El muro baja con el horizonte. Pero **la señal encontrada baja más rápido**:

| | 1 hora | 4 horas | 1 día |
|---|---|---|---|
| lo que da la finta | +0,047 | +0,021 | −0,024 |
| lo que cuesta | 0,1076 | 0,0539 | 0,0226 |

No se cruzan en ningún punto. Estirar el horizonte **no rescata esta señal**.
Haría falta una distinta, que prediga a días o semanas.

## Lo que corrige de mensajes anteriores

Se retira la afirmación de que «el trading es difícil y negativo». No se ha
medido y no se sigue de lo medido. Lo que se mantiene, por cubrir exactamente
lo que dice:

- los porcentajes de pérdida publicados por los brókers (son suyos y obligatorios);
- la aritmética de `docs/RESULTADOS_payouts.md`;
- las 27 mediciones, **para intradía en FX a coste de minorista**.

## Adónde apunta

A lo contrario de donde se ha buscado: **horizonte largo y muchos instrumentos
a la vez**, en vez de horizonte corto y un instrumento con mucho histórico.
6 años son 1 500 días o 300 semanas: poquísimas observaciones independientes
por instrumento, así que la potencia tiene que venir del número de mercados.
