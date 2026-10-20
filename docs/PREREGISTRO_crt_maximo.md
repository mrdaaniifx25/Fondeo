# Pre-registro · el CRT máximo: todo lo que midió no-negativo, junto

Firmado **antes** de correr `bt/crt_maximo.py`. Un solo pase.

## Lo que pide el usuario

> *«hazme la mejor estrategia CRT con todos los datos que tienes»*

## La trampa que lleva dentro, declarada antes de medir

Voy a ensamblar los componentes que **midieron mejor** en 45 documentos. Esos
componentes se eligieron **mirando resultados pasados**. Por tanto:

**El resultado dentro de muestra está inflado por construcción y no vale nada.**

Es exactamente lo que midió `RESULTADOS_busqueda_masiva.md`: las 10 mejores de
14.166 estrategias daban +0,2766 dentro y **−0,0198 fuera**. La retención fue
del 13 % para las 500 mejores.

Así que:

- **Dentro de muestra: 2021-2024.** Es donde se eligieron los componentes. Se
  informa, y se ignora.
- **FUERA: 2025-2026.** No se mira hasta tener el diseño cerrado.
  **Es el único número que cuenta.**

## Los componentes que ENTRAN (midieron no-negativo)

| pieza | medida | dónde |
|---|---|---|
| ventana **Londres 08:00-11:00** | bruta +0,0835 (z +2,12) | `RESULTADOS_su_patron.md` |
| entrada en la **Vela 3**, no la 2 | −0,0895 → +0,0248 | `RESULTADOS_crt_canonico.md` |
| stop **1,5 × ATR(14)**, no la mecha | neta −0,124 → −0,021 | `RESULTADOS_su_patron.md` |
| **R:R 2**, objetivo cercano | los lejanos se alcanzan menos que por azar | `RESULTADOS_crt_cascada_video.md` |
| **sin trailing** | acierto 40,9 % → 37,5 % con él | `RESULTADOS_su_patron.md` |
| entrada **inmediata**, sin esperar retroceso | los retrocesos empeoran de forma monótona | `RESULTADOS_punto_optimo.md` |
| **una por lado y día** | — | diseño |
| **NIVELES DE 2 A 4 SESIONES DE ANTIGÜEDAD** | R/op **+0,190** (z +2,19) contra +0,067 de la sesión anterior | `RESULTADOS_cascada.md` |

**La última es la única que nunca se ha combinado con el resto.** Es la pieza
nueva de esta prueba.

## Los que se EXCLUYEN porque midieron negativo

```
  filtro de dirección H4          resta: 35,0 % sin él -> 34,3 % con él
  filtro de dirección semanal     empeora en los tres instrumentos
  cascada multimarco              3 marcos alineados = la PEOR celda
  entrada por retroceso           monótonamente peor
  trailing stop                   baja el acierto sin arreglar el neto
  ventana de Nueva York           bruta -0,0464 (z -2,60)
  Fibonacci / confluencias        AUC 0,4984
```

## Contraste PRINCIPAL, declarado antes de mirar

**R neta por operación del CRT máximo en 2025-2026**, EUR/USD, coste ECN.

Y el contraste interno que decide si la pieza nueva vale: **R neta por
antigüedad del nivel** (1 sesión / 2-4 / 5+), fuera de muestra.

## Predicción firmada

- **Dentro de muestra saldrá positivo.** Tiene que salirlo: los componentes se
  eligieron ahí. Predigo entre +0,05 y +0,20 de R neta.
- **FUERA saldrá entre −0,06 y +0,02.** Es decir, indistinguible de cero o
  negativo, con una retención del orden del 10-20 % de lo de dentro.
- **La antigüedad del nivel no se sostendrá fuera**: predigo que el cubo de 2-4
  sesiones no batirá al de 1 sesión por más de 0,05 de R.

## Qué me refutaría

R neta **fuera de muestra** positiva con z > +2, y el cubo de 2-4 sesiones
batiendo al de 1 sesión también fuera. Eso sería una estrategia CRT con ventaja
real y lo diría así, con las reglas exactas.

Una sola pasada. Lo que salga se publica, dentro y fuera.
