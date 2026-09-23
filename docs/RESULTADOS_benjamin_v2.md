# Resultados · la regla de Benjamín, completa

Pre-registro `6b1df99`, subido antes de medir. Código `bt/benjamin_v2.py`.
EURUSD 5,7 años. Con sus cuatro añadidos: cambio de estructura con cuerpo
antes del hueco, entrada al mitigar, jerarquía de niveles, sus dos ventanas.

## Veredicto

**Las seis celdas fallan.** Ninguna llega a su propio umbral de empate.

| celda | n | al año | acierto | riesgo | coste | **umbral** | ¿pasa? | **NETA** |
|---|---|---|---|---|---|---|---|---|
| M1 · al mitigar | 27 581 | 4 876 | 34,6 % | 2,7 p | 53,0 % | 51,0 % | no | **−0,909** |
| M1 · a mercado | 28 286 | 5 001 | 30,6 % | 5,6 p | 25,5 % | 41,8 % | no | −0,455 |
| **M2 · al mitigar** | 27 041 | 4 781 | **35,0 %** | 3,8 p | 37,6 % | 45,9 % | no | **−0,596** |
| **M2 · a mercado** | 28 032 | 4 956 | 30,1 % | 7,6 p | 18,8 % | 39,6 % | no | **−0,372** |
| M5 · al mitigar | 24 640 | 4 356 | 34,6 % | 6,0 p | 23,8 % | 41,3 % | no | −0,402 |
| **M5 · a mercado** | 26 774 | 4 733 | 29,8 % | 11,6 p | 12,3 % | 37,4 % | no | **−0,286** |

Nulo (lados barajados, M2 al mitigar): acierto **33,6 %**, neta −0,637. La
regla real saca 35,0 % y −0,596. **Apenas distinguibles.**

## El hallazgo: su entrada preferida es la que más le cuesta

Él recomienda entrar **al mitigar el hueco**, porque da mejor precio. Y **tiene
razón en que el acierto sube**:

| M2 | acierto | riesgo | coste | umbral | **neta** |
|---|---|---|---|---|---|
| al mitigar | **35,0 %** | 3,8 p | 37,6 % | 45,9 % | **−0,596** |
| a mercado | 30,1 % | 7,6 p | 18,8 % | 39,6 % | **−0,372** |

**Acierta cinco puntos más y pierde un 60 % más.**

Porque mejorar el precio **parte el stop por la mitad** (7,6 → 3,8 pips), el
coste **se dobla** (18,8 % → 37,6 %) y el umbral sube seis puntos. El mercado
le cobra la mejora de precio exactamente, y el coste fijo remata lo que queda.

Es el teorema de la barrera actuando en directo sobre su propia regla.

## El cambio de estructura no aporta

| | acierto | neta |
|---|---|---|
| sólo hueco (`RESULTADOS_benjamin_regla.md`) | 33,4 % | −0,312 |
| + cambio de estructura, a mercado | **30,1 %** | −0,372 |

Añadir la segunda confirmación **empeora**. Y filtra mucho menos de lo que yo
esperaba: de ~30.000 operaciones a ~28.000.

## Contra el umbral de su propio plan

```
lo que necesita su plan (RESULTADOS_plan_viable.md):  +0,05 R
la mejor de sus seis celdas (M5 a mercado):           -0,286 R
                                                      ------------
                                                      faltan 0,336
```

## Mi predicción: 2 de 4

| predije | salió |
|---|---|
| el cambio de estructura reducirá mucho las operaciones | ❌ de 30.000 a 28.000 |
| acierto entre 33 y 38 % | ✅ casi: 29,8 a 35,0 |
| **al mitigar: stop menor y peor neta** | ✅ **exacto** |
| neta entre −0,10 y −0,30 | ❌ salió −0,29 a −0,91 |

## Lo que cierra

Se han medido **catorce celdas** de su estrategia entre las dos versiones, con
~28.000 operaciones cada una y 5,7 años. Todas por debajo de su umbral, todas
con neta negativa, y el nulo indistinguible.

La estrategia está **descartada**. No por opinión: por 5,7 años de EURUSD.
