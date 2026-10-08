# Pre-registro · RSI + soporte/resistencia + vela de giro, en H1

Escrito y subido ANTES de medir. 23/09/2026. Vídeo aportado por el usuario.

## La regla, tal y como la explica

1. RSI(14) llega a **sobreventa (< 30)** o **sobrecompra (> 70)**
2. el precio está en una **zona de soporte o resistencia**
3. aparece una **vela de giro**
4. entrar al cierre de esa vela · stop tras el extremo previo · objetivo **1:2**
5. marco de **una hora**, sin EMA ni ningún otro indicador

Él mismo avisa al final del vídeo de que «una estrategia así no es suficiente».
Se mide la que enseña, no una mejorada.

## Por qué ésta sí merece medirse

No es una idea nueva —`RESULTADOS_ema_rsi.md` ya midió RSI con filtro de EMA50
en H4 y ejecución en M15: +0,0400 bruto con **p 0,156** y factor de beneficio
neto 0,951. Lo que cambia aquí es **el marco**, y con él el coste:

```
  estrategia                          stop típico   coste/riesgo   umbral   hace falta
  Benjamin (M2, extremo del barrido)      5,9 p         24,2 %     41,4 %     +8,1 puntos
  Lozano (M5, extremo + 1 pip)            8,9 p         16,1 %     38,7 %     +5,4
  EMA+RSI (M15, bajo el retroceso)       18,0 p          7,9 %     36,0 %     +2,6
  RSI del vídeo (H1, extremo previo)     32,0 p          4,5 %     34,8 %     +1,5
```

La ventaja bruta que este proyecto ha medido en **cualquier** patrón de gráfico
vive entre 0,00 y +0,10 R, o sea entre 0 y +3 puntos de acierto. **En H1 el
listón es +1,5: es la primera de las cuatro que cae dentro de ese rango.**

Eso no la hace buena. La hace la primera con una posibilidad aritmética.

## Qué se mide

| | |
|---|---|
| instrumentos | **EURUSD** 2021-2026 · **oro** y **DAX** 2023-2026 para réplica |
| marco | **H1**, todas las horas (el vídeo no pone horario) |
| RSI | 14 periodos, sobre cierres de H1 |
| umbrales | **30/70** (principal) y 20/80 |
| soporte/resistencia | pivote de H1 con 5 velas a cada lado, formado antes; el precio tiene que estar a menos de **0,5 × ATR** (también 0,25 y 1,0) |
| vela de giro | envolvente, o martillo / estrella fugaz (mecha ≥ 2 × cuerpo, al lado correcto) |
| entrada | cierre de la vela de giro |
| stop | extremo de las **3** velas previas más 0,1 × ATR |
| objetivo | **2R** (también 1R y 3R) |
| horizonte | 10 días; sin resolver se cierra a mercado |

**El PRINCIPAL, declarado ahora: EURUSD · RSI 30/70 · nivel a menos de 0,5 ATR ·
objetivo 2R.**

## Controles

- **placebo de lados barajados**: tiene que salir en el precio justo
- **sin el filtro de nivel**: sólo RSI + vela de giro. Si rinde igual, el
  soporte no aporta
- **sin el filtro de RSI**: sólo nivel + vela de giro. Si rinde igual, el RSI
  no aporta

Estos dos últimos son los que dicen si la combinación aporta algo o si uno de
los tres ingredientes lo hace todo.

## El sesgo de selección

2 umbrales × 3 distancias × 3 objetivos = **18 celdas** por instrumento. El
mejor de 18 sale **1,82 errores estándar** por encima de la verdad. Con el error
estándar que dé la muestra se calculará el regalo exacto al publicar.

## Criterio

1. El principal con **neta > 0** y el IC95 sin tocar el cero, **y**
2. por encima del sesgo de selección, **y**
3. los dos controles de ingredientes **peores** que la señal completa, **y**
4. el mismo signo en **oro y DAX**.

## Predicción

- **Saldrá plano**: bruta entre −0,03 y +0,05 con el cero dentro.
- El control «sin nivel» rendirá **prácticamente igual** que la señal completa.
  La zona de soporte es lo que más se parece a lo ya medido treinta veces.
- El de «sin RSI» también.
- **Habrá pocas operaciones**: espero 150-400 en EURUSD, porque exigir las tres
  cosas a la vez en H1 es restrictivo.
- Y aun así, si saliera algo, sería lo primero: es la única geometría de las
  cuatro cuyo listón cabe dentro de lo medido.

Van dieciocho predicciones con errores. Ésta también puede fallar.
