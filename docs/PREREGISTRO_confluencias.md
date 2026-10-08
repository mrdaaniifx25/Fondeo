# Pre-registro · Confluencias multiactivo sobre EURUSD

**Escrito ANTES de recibir los datos de GBPUSD y USDJPY.** Su única función es
impedir que el análisis se adapte a lo que vayan diciendo los datos. Cualquier
desviación posterior queda registrada como tal en el commit correspondiente.

---

## 1 · Datos

- **GBPUSD** y **USDJPY**, M1, HistData ASCII, 2020-01 a 2026-07.
- Misma conversión horaria ya validada para EURUSD: los sellos siguen el reloj
  de Nueva York **con** horario de verano, no EST fijo.
- **DXY queda excluido** del análisis principal: con un 57,6 % de peso en euro,
  su correlación con EURUSD es en su mayor parte aritmética, no informativa.
  Si se recibe, se usará solo como comprobación descriptiva.

## 2 · Verificación previa, antes de cualquier prueba

1. Perfil de volatilidad por hora en invierno y verano, para confirmar el huso
   igual que se hizo con EURUSD.
2. Correlación de retornos diarios EURUSD–GBPUSD y EURUSD–USDJPY. Se espera
   ~+0,85 y ~−0,5. Una desviación grande indica un problema de datos, no un
   hallazgo.

## 3 · Hipótesis a contrastar. Son SEIS. No se añadirán más.

Todas se aplican como **filtro sobre los setups ya existentes** de
`CRT + order block M15 + DOL diario`, sin tocar entrada, stop ni objetivo.
La métrica es siempre la **ventaja bruta por operación en R**.

| # | Hipótesis | Regla mecánica |
|---|---|---|
| H1 | SMT clásico con GBPUSD | En un largo, EURUSD hace mínimo más bajo que su mínimo previo y GBPUSD **no**. En un corto, simétrico. |
| H2 | SMT con USDJPY invertido | Igual que H1 usando −USDJPY como sustituto del dólar. |
| H3 | Confluencia de barrido | El barrido de rango H4 ocurre **a la vez** en EURUSD y en GBPUSD dentro de la misma vela H4. |
| H4 | Fuerza relativa | En un largo, EURUSD ha subido más que GBPUSD en las últimas 24 h (euro fuerte, no solo dólar débil). |
| H5 | Régimen de correlación | La correlación móvil de 20 días EURUSD–GBPUSD está **por debajo** de su mediana histórica (los pares se han desacoplado). |
| H6 | Adelanto-retraso | Correlación cruzada de retornos EURUSD–GBPUSD con desfases de ±1 a ±15 minutos. Prueba puramente estadística, sin backtest. |

## 4 · Protocolo

- **Entrenamiento** 2020-01-01 a 2023-12-31. **Reserva** 2024-01-01 a 2026-07-31.
- Las seis hipótesis se evalúan **solo en entrenamiento**.
- Cada hipótesis admite **como máximo dos variantes de umbral**. Total ≤ 12
  contrastes. Este número se declara aquí para poder corregir después.
- Un solo disparo en la reserva, con la ganadora, si la hay.

## 5 · Criterio de éxito, declarado de antemano

Una hipótesis se considera **prometedora** si cumple **las tres** condiciones:

1. n ≥ 150 operaciones en entrenamiento.
2. Ventaja bruta superior a la del filtro DOL sin confluencia (+0,2584 R/op).
3. Las dos mitades del entrenamiento positivas.

Y se considera **confirmada** solo si además:

4. Supera la corrección de Bonferroni para 12 contrastes: **p < 0,0042**.
5. Mantiene el signo en la reserva.

## 6 · Qué se reportará pase lo que pase

- Las seis hipótesis con sus números, incluidas las que no cumplan nada.
- El recuento exacto de contrastes ejecutados.
- Si ninguna cumple, se reportará como resultado negativo y **no se buscarán
  hipótesis adicionales** sobre la misma muestra.

## 7 · Expectativa previa, declarada

De las seis, H1 y H4 son las que tienen mecanismo más plausible: separan
«euro fuerte» de «dólar débil», que es información que EURUSD por sí solo no
contiene. H3 es la más probable que resulte redundante con el propio barrido.
H6 casi con seguridad dará cero: si existiera adelanto-retraso explotable entre
los dos pares más líquidos del mundo, estaría arbitrado.

La probabilidad previa de que alguna alcance la categoría de *confirmada* la
estimo baja. Se registra aquí para que el resultado no se lea a posteriori
como si se hubiera esperado.
