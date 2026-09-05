# Pre-registro · «vuelta limpia» en oro y DAX

**Escrito antes de cargar un solo dato de 2026 y antes de tocar oro o DAX con
esta estrategia.** Fecha: 2026-08-28.

## De dónde sale

De `RESULTADOS_asia_anatomia.md`. Buscando por qué unas operaciones van al stop
y otras al objetivo se miraron 18 variables y se hicieron 28 contrastes sobre
1.428 operaciones de EURUSD. **Ninguna cruzó el umbral** (haría falta |z| ≥ 3,1;
el máximo fue 1,98). Pero las cuatro primeras describían lo mismo, y coincide con
la *turtle soup* clásica y con la documentación del usuario.

Eso es un candidato, no un hallazgo. Esto es su única prueba, y se hace una vez.

## La regla, con los umbrales fijados ahora

Base: el barrido de Asia de `PREREGISTRO_asia_londres.md`, lectura laxa (el
primer barrido del día que trae envolvente), un setup por día, Londres 08:00 a
14:00 hora de Madrid, cierre a las 14:00.

Encima, las cuatro condiciones, **todas a la vez**:

```
1  hora de entrada           < 10:00 (Madrid)
2  el gatillo cierra DENTRO del rango de Asia
3  mecha del barrido / rango de Asia          <= 0,3314
4  mecha de rechazo / rango de la vela gatillo <= 0,1322
```

Los umbrales 3 y 4 son las **medianas de EURUSD 2020-2026**, sin ajustar y sin
buscar el mejor corte. Son razones, no pips, así que cruzan de instrumento sin
reescalar. En EURUSD el filtro deja pasar el 11,8 % de las operaciones.

**Lo que hay que replicar**, medido en EURUSD:

| | n | %TP | geometría | bruta | neta | z |
|---|---|---|---|---|---|---|
| no cumple | 1.260 | 20,1 % | 33,3 % | −0,043 | −0,299 | −6,31 |
| **cumple las 4** | 168 | **34,5 %** | 33,3 % | **+0,218** | **+0,024** | +0,19 |

Diferencia bruta **+0,261**, z +1,93.

## Dónde se prueba

Sitios donde esta estrategia **no se ha ejecutado nunca**:

| conjunto | de dónde sale |
|---|---|
| **XAUUSD 2023-2025** | `data/xauusd_m1.parquet`, usado sólo para el CRT |
| **XAUUSD 2026 ene-jul** | `reservado/`, sin abrir |
| GRXEUR 2023-2025 | `data/grxeur_m1.parquet`, usado sólo para el CRT |
| GRXEUR 2026 ene-jul | `reservado/`, sin abrir |

Costes: los mismos de `PREREGISTRO_h12_ciego.md`, no se vuelven a elegir.
**XAUUSD** unidad 0,01 y coste 35 unidades (0,35 USD). **GRXEUR** unidad 1,0 y
coste 2,0 puntos.

### Una limitación de los datos, declarada antes de mirar

Contados ya los minutos por hora, sin resolver nada: el oro tiene **465 de 480
minutos** de la ventana de Asia cada día; el DAX sólo **307**, porque el CFD
apenas cotiza de madrugada. El rango de Asia del DAX se construye con datos
llenos de huecos.

Por eso: **el oro es la prueba principal.** El DAX se reporta como secundario y
con el requisito de vela M5 relajado a 2 minutos (en vez de 3) y el mínimo de la
sesión de Asia a 40 velas M5 (en vez de 60). Si el DAX y el oro discrepan, manda
el oro, y queda dicho ahora para que no se elija después.

## Qué decide

**Principal:** la diferencia de R bruta entre lo que cumple el filtro y lo que
no, agrupando XAUUSD 2023-2025 y 2026.

- **Replica** si esa diferencia es **≥ +0,13 R** (la mitad de la estimación de
  EURUSD, para no exigir que se repita el tamaño exacto) **con z ≥ 1,96**,
  **y además** la R neta del subconjunto que cumple es **≥ 0**.
- **No replica** en cualquier otro caso, y entonces se cierra la familia del
  barrido de Asia de forma definitiva: dos barajas ciegas, 1.428 operaciones
  diseccionadas y una réplica fallida en otro instrumento.

Se reporta siempre, replique o no: la regla sin filtrar en cada instrumento —
para saber si la estrategia base existe fuera de EURUSD—, el %TP contra la
geometría `1/(1+R:R)`, y el **coste de equilibrio** `c* = media(R)/media(1/riesgo)`,
que no depende del spread que yo suponga y cada uno compara con el suyo.

## Potencia

En EURUSD salen ~220 operaciones al año y el filtro deja pasar el 11,8 %. Si el
oro se comporta parecido, 3,5 años darían ~770 operaciones y ~90 filtradas. Con
desviación de 1,3 R el error típico de la diferencia rondaría **±0,14 R**: justo
para ver un efecto de +0,26 si es real, y sin margen si es la mitad.

O sea: esta prueba puede **confirmar** el efecto de EURUSD si es grande, pero no
puede descartar uno pequeño. Si sale plano, lo que se archiva es «no hay un
efecto grande», no «no hay nada».

## Lo que espero, dicho antes

Que la regla sin filtrar salga **negativa en neto** en los dos instrumentos, y
que el filtro **no llegue** al umbral: +0,261 con z +1,93 sobre datos ya vistos,
después de 28 contrastes, es exactamente el tamaño de efecto que suele
evaporarse al replicar.

Y una nota que también va escrita antes: el usuario dice que sus diez últimas
operaciones en TradingView fueron todas TP. Con una tasa base del 25 %, diez
seguidas son una entre un millón. Eso no lo decide esta prueba y no cambia
ninguno de los umbrales de arriba.

## Ficheros

```
bt/asia_limpia.py           la pasada, se ejecuta una vez
data/asia_limpia.csv        las operaciones resueltas
```
