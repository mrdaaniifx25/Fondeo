# ¿Prueba algo un papel de payout?

Código: `bt/payouts.py`. Pregunta del usuario: *«antes de vender cursos, todos
los payouts que sacan qué? Algo tendrán que demostrar, no sólo una captura,
sino los papeles de los payouts también»*.

## Respuesta corta

**No prueba nada.** Con dos años de intentos y **ventaja exactamente cero**, el
84 % de la gente acaba con un papel de payout real en la mano. Y de ésos, el
60 % está perdiendo dinero.

El papel no es falso. Es que cobrar un payout no es un suceso raro.

## Cómo está montado

Una persona compra retos de fondeo uno detrás de otro durante dos años. Cuando
revienta una cuenta, compra otra. Cobra cuando cobra. Reglas tipo FTMO sobre
10.000 €: fase 1 +10 %, fase 2 +5 %, pérdida diaria 5 %, pérdida total 10 %,
reparto 80 %, retira cada +5 %, reto 89 €. Operaciones a 1:2 con el coste
habitual (7 % del riesgo), 3 al día.

Dos personas:

- **Sin ventaja**: acierta el **33,3 %** a 1:2. Es el precio justo exacto de esa
  geometría. Cero habilidad. Pierde 0,070 R por operación, que es el coste.
- **Con ventaja**: acierta el **39,0 %** a 1:2. Gana +0,100 R por operación. Es
  un operador excelente, de los que casi no existen.

200.000 personas por casilla.

## El resultado

| | riesgo | llega a fondearse | **enseña payout** | pagado en retos | cobrado | neto medio | % que gana |
|---|---|---|---|---|---|---|---|
| **sin ventaja** | 1 % | 98,2 % | **84,3 %** | 1 872 € | 1 521 € | **−351 €** | 34,1 % |
| sin ventaja | 2 % | 100 % | **100 %** | 13 274 € | 6 718 € | −6 556 € | 3,2 % |
| sin ventaja | 5 % | 100 % | **100 %** | 29 753 € | 9 278 € | −20 475 € | 0,0 % |
| **con ventaja** | 1 % | 100 % | **100 %** | 974 € | 10 537 € | **+9 563 €** | 99,9 % |
| con ventaja | 2 % | 100 % | 100 % | 10 189 € | 18 382 € | +8 193 € | 94,9 % |
| con ventaja | 5 % | 100 % | 100 % | 27 230 € | 16 740 € | −10 490 € | 4,0 % |

Mira la columna de payouts: **84,3 % sin ninguna ventaja, 100 % con ella.** Esa
columna no distingue a un operador excelente de una moneda al aire. Es la
columna que se publica.

La que sí distingue es la del neto: −351 € contra +9 563 €. Ésa no se publica
nunca, porque para publicarla habría que enseñar también lo que se pagó en
retos.

## Los que enseñan payout, sin ninguna ventaja, al 1 % de riesgo

| | |
|---|---|
| ganan dinero de verdad | **40,5 %** |
| pierden dinero | **59,5 %** |
| neto mediano | **−334 €** |
| cobrado total, mediana | **+1 446 €** ← esto es lo que se enseña |
| retos comprados, mediana | **21** (1 869 €) ← esto no |
| el mejor 1 % | **+4 226 €** ← éste es el que vende el curso |

El mecanismo entero está ahí. Enseñas los 1 446 € que cobraste. No enseñas los
1 869 € en retos que pagaste para llegar. Las dos cosas son verdad. Sólo se ve
una.

Y al 2 % de riesgo la cosa se pone peor: el 100 % enseña payout, el **96,8 %**
pierde dinero, y el neto mediano es **−6 815 €** — habiendo cobrado 6 458 € de
payouts reales.

## Lo único que probaría algo

Las dos columnas juntas, de todas las cuentas, desde el principio:

> **total pagado en retos** frente a **total cobrado en payouts**, durante años.

Nadie enseña eso. Y aunque lo enseñara, harían falta cientos de operaciones
para separar la habilidad de la suerte.

## Límites del modelo

- Deja comprar retos sin límite. En el 2 % llega a 149 retos en dos años, que
  una persona real no compra. **La fila realista es la del 1 %**, con 21 retos,
  y es la que hay que citar.
- R:R fijo 1:2, riesgo fijo, 3 operaciones al día.
- No modela los reintentos gratis que regalan algunas firmas, que subirían aún
  más el porcentaje que acaba enseñando payout.
