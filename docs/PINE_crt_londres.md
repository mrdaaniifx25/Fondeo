# El indicador · `pine/crt_londres_asia.pine`

Implementa `docs/ESTRATEGIA_operativa.md` apartado por apartado.

## Fallos corregidos antes de publicarlo

La primera versión no habría compilado. Queda escrito porque son errores
típicos de Pine y conviene no repetirlos:

| fallo | por qué |
|---|---|
| `cierra()` como función que mutaba `var` externas | en Pine una función **no puede** modificar variables del ámbito exterior. Se inlineó |
| `fila()` definida dentro de un `if` | las funciones sólo se declaran en el nivel superior |
| `box.set_top(...), box.set_bottom(...)` | Pine no admite sentencias separadas por coma |
| `pend := -1, pendRgo := ...` | lo mismo, una asignación por línea |
| `na(caja) or nuevoDia ? a : b` | precedencia: se parseaba como `na(caja) or (nuevoDia ? a : b)` |
| `(close-ent)/(ent-sl) * lado * lado` | `lado*lado` siempre vale 1. Y la expresión ya es correcta para los dos lados |

## Cómo se garantiza que no repinta

```
  1  resolver la operación viva          (usa high/low de la vela en curso)
  2  ejecutar la pendiente en open       (la apertura ya está fijada)
  3  registrar la señal SI barstate.isconfirmed
```

La señal sólo se anota **cuando la vela ha cerrado**, y la entrada usa la
**apertura de la siguiente**. Nunca se mira un dato que no existiera en ese
instante.

## Qué pinta

- Caja gris del **rango de Asia**, que deja de crecer a las 08:00.
- Fondo azul en la **ventana de 08:00 a 11:00**.
- Líneas roja y verde azulada con `asiaH` y `asiaL` durante la ventana.
- Triángulo en la vela de señal.
- Etiqueta con **lotes ya calculados**, entrada, stop, objetivo y riesgo en pips.
- Líneas de stop y objetivo mientras la operación vive.
- Tabla arriba a la derecha con operaciones, acierto, **umbral de equilibrio**,
  R neta total, R por operación, operaciones de hoy y pérdidas seguidas.

**La tabla es lo importante.** Calcula su propia estadística delante de usted:
si el acierto se queda por debajo del umbral, el indicador se lo está diciendo
sin que haga falta creerme a mí.

## Dos avisos sobre lo que el indicador NO hace

1. **No ejecuta.** Es un indicador, no una estrategia automática. Las órdenes
   las pone usted.
2. **Su contador no es un backtest.** Cuenta lo que ve en el gráfico cargado,
   con un coste estimado fijo de 0,10 R. El backtest serio está en
   `bt/su_patron_londres.py`, con 1.281 operaciones y los placebos.

## Configuración para su cuenta

```
  Saldo de la cuenta            10000
  Riesgo por operación (%)      0.50
  Máximo de operaciones al día  3
  Parar tras N pérdidas         2
  Riesgo = k x ATR(14)          1.5
  Objetivo = R:R                2.0
  Cierre forzoso                6 horas
```
