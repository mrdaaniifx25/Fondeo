# Ampliación del CRT · conceptos recibidos de Instagram

Transcripción fiel de lo que dicen las publicaciones, convertida a reglas
mecánicas. **Nada de esto está medido todavía** salvo donde se indica.
Fuentes: `@bctrades__` (el grueso, y lo más nuevo) y `@trader.derivados`
(definiciones generales). Entrada del 25 de agosto de 2026, pendiente de
completar con más material.

---

## A · La estructura del rango en tres fases  (bctrades)

> «Las tres fases principales de la estructura de un rango en 4H. Primero la
> acumulación y la creación de la **vela base**. Después la **manipulación**,
> donde el precio liquida esa vela base y cierra dentro del cuerpo creando un
> rango. Y finalmente la **distribución**, donde el mercado desarrolla el
> desplazamiento hasta completar la estructura de 4H.»

```
VELA BASE          →   CREACIÓN DE RANGO        →   RANGO COMPLETADO
(acumulación)          (manipulación:               (distribución:
                        liquida la base y            desplazamiento hasta
                        cierra DENTRO del cuerpo)    el objetivo)
```

Esto es el CRT que ya conozco, con un matiz que **no había implementado**: el
cierre de vuelta tiene que quedar dentro del **cuerpo** de la vela base, no solo
dentro de su rango. Mi motor usa el rango. Es una diferencia medible.

Añade además el desarrollo interno: cada fase de 4H se construye con velas de
1H, y cuatro velas de 4H con el mismo cierre pueden tener recorridos internos
completamente distintos. Enlaza con lo que ya medí de rangos internos: el 17,2 %
de las velas H4 son internas y el rango efectivo es 2,11× más ancho cuando las hay.

---

## B · Liquidez simple, doble y triple  ← **lo más interesante de todo**

> «La liquidez no siempre se toma una sola vez. El precio puede tomar la
> liquidez las veces que quiera mientras siga cerrando dentro de la vela base.
> La doble y la triple liquidez ocurren cuando al precio le falta una activación
> de rango en otra temporalidad.»

| | qué pasa | qué afirma |
|---|---|---|
| **simple** | el precio abre fuera, toma el extremo de la vela base y vuelve a cerrar dentro | crea el rango y define el objetivo |
| **doble** | toma el extremo **dos veces** y sigue cerrando dentro | «confirmando la estructura y **aumentando la probabilidad**» |
| **triple** | tres o más veces, cerrando siempre dentro | «reforzando la estructura y aumentando **todavía más** la probabilidad» |

**Esto es una afirmación de probabilidad, concreta, mecánica y contrastable.** Es
un contador: cuántas veces el precio cruzó el extremo de la vela base antes de la
vuelta. Todo lo que he probado hasta ahora usaba barrido simple, sin contar. Si
el efecto existe, tiene que aparecer como un gradiente 1 → 2 → 3.

Es la pieza que más merece medirse de todo el material.

---

## C · Rango reiniciado y rango descartado

> «Rango bajista creado: el precio toma el máximo de la vela y cierra dentro.
> Rango bajista **reiniciado**: el precio toma el mínimo de la vela que origina
> el rango, reiniciándolo y generando un rango alcista en contra de la dirección.
> Rango bajista **descartado**: queda invalidado tras su reinicio y el precio
> confirma cerrando fuera.
> **Tras un reinicio, el rango solo se descarta si el precio confirma con un
> cierre fuera del rango principal.**»

Regla de invalidación en tres estados, no en dos. Mi motor solo tenía «vivo» o
«muerto». Esto dice que tomar el extremo contrario **no mata** el setup: lo da la
vuelta. Solo lo mata un cierre fuera del rango principal.

Es exactamente el tipo de regla que cambia cuántas operaciones sobreviven, y es
implementable tal cual.

---

## D · PO3 (Power of Three) en continuaciones

> «Barrida H4 → Rango M15 → Expansión → Objetivo H4»

1. **Barrida en 4H** — el precio toma la liquidez del mínimo de la vela base y
   activa el movimiento. El objetivo queda definido: el máximo de esa vela de 4H.
2. **Creación de rango en M15** — dentro del PO3 de esa vela de 4H, el precio
   crea un rango en M15 y muestra el cambio de estructura.
3. **Expansión del primer rango** — primera entrada en M15, tras la barrida,
   en dirección al objetivo de 4H.
4. **Continuación en el PO3** — segunda entrada en M15, esta vez dentro de la
   **mecha de la segunda vela de 4H**, hacia el mismo objetivo.

Dos entradas por estructura, no una. El objetivo no es 1:1 ni un múltiplo fijo:
es **el extremo opuesto de la vela base de 4H**. Eso cambia el perfil por
completo — objetivo estructural en vez de razón fija.

---

## E · CRT + Order Block, confirmación de continuidad

> «15M completa rango y 1H crea order block.»

Alcista: se completa el CRT en M15 **y** la vela de 1H deja un order block.
Bajista: lo mismo al revés. Es una confluencia de dos marcos, uno que cierra la
estructura y otro que deja la zona de entrada.

---

## F · Definiciones generales  (trader.derivados)

**Order Block.** «La última vela antes de un movimiento muy fuerte en la
dirección opuesta.» Cómo identificarlo: 1) movimiento fuerte y claro en una
dirección, 2) la última vela opuesta antes de ese impulso, 3) marcar esa vela y
extender el OB en la zona de su rango, 4) esperar que el precio regrese y buscar
rechazo.

Ojo: **esta definición no es la del vídeo de liquidez.** Allí el order block era
la propia vela envolvente y la entrada era inmediata. Aquí es la vela previa al
impulso y la entrada llega **cuando el precio vuelve**. Son dos modelos
distintos con el mismo nombre, y hay que decidir cuál se prueba.

**Fair Value Gap.** Zona donde el precio se movió tan rápido que dejó un hueco
sin negociar; tiende a volver a rellenarla. *(La publicación va marcada como
«Contenido generado con IA».)*

**Patrones de vela de confirmación.** Envolvente, martillo y estrella de la
mañana en compra; envolvente, estrella fugaz y estrella de la tarde en venta.
Uso propuesto: zona clave → cambio de estructura (BOS/MSS) → pullback a EMA 9/20,
VWAP u order block → vela de confirmación → entrada con gestión de riesgo.

---

## Qué de esto es nuevo de verdad

| pieza | ¿medido ya? |
|---|---|
| CRT de tres velas, barrido simple | sí, `RESULTADOS_crt_canonico.md` |
| Rangos internos en H4 | medidos (17,2 %, 2,11×), nunca metidos en el motor |
| Envolvente como gatillo | sí, `RESULTADOS_ls_nasdaq.md` |
| FVG como zona de entrada | sí, `RESULTADOS_crt_fib.md` |
| **Cierre dentro del CUERPO, no del rango** | **no** |
| **Liquidez doble y triple** | **no** |
| **Rango reiniciado / descartado** | **no** |
| **PO3 con dos entradas y objetivo estructural** | **no** |
| **CRT M15 + OB en H1** | **no** |

Cinco piezas nuevas. Las tres primeras son variantes del motor que ya existe;
las dos últimas son modelos de ejecución distintos.

## Orden de prueba propuesto

1. **Liquidez doble y triple.** Es un contador sobre el motor que ya está
   escrito, y es la única afirmación del material que viene con una predicción
   explícita («aumenta la probabilidad»). Si el gradiente no aparece, se cae.
2. **Cierre en el cuerpo** y **rango reiniciado**. Dos cambios de regla sobre el
   mismo motor.
3. **PO3 con objetivo estructural.** Es lo que más se aleja de todo lo probado:
   objetivo en el extremo de la vela base en vez de razón fija. Merece motor
   propio.

Pendiente de más material antes de tocar nada.
