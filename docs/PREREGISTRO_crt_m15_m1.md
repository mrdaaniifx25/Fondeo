# Preregistro · CRT detectado en M15, entrada afinada en M1

Escrito **antes** de correr `bt/crt_m15_m1.py`. Un solo pase.

## De dónde sale la pregunta

Él pide «el CRT en M15 con entrada en M1». No es lo mismo que el CRT en M15 a
secas: lo que aporta el M1 es **afinar la entrada**, y afinar la entrada cambia
el tamaño del stop. Ese es todo el asunto.

Ya sabemos dos cosas medidas (`RESULTADOS_crt_temporalidad.md`):

1. La ventaja bruta del CRT es **plana** entre H1 y D1: ≈ +0,082 R, con Q = 7,75
   sobre 6 g.l. No hay señal de que dependa del marco.
2. El coste en R es exactamente `coste / riesgo`, y por eso sube al estrechar el
   stop: 2,3 % del riesgo en D1, 14,3 % en H1.

Afinar en M1 estrecha el stop. Si la ventaja bruta por operación fuese fija en
pips, estrechar el stop **multiplica la R** y también multiplica el coste en R,
en la misma proporción. La pregunta real es si la entrada en M1 aporta algo
**más** que ese cambio de escala.

## El patrón, cerrado antes de mirar

Rejilla M15 alineada a :00/:15/:30/:45 UTC, construida desde M1.

- **Vela 1** (barra `i-1`): el rango. `r_hi`, `r_lo`.
- **Vela 2** (barra `i`): la manipulación. Barre **un solo** lado
  (`low < r_lo` XOR `high > r_hi`) y **cierra dentro** del rango.
  Barre el mínimo → operación larga. Barre el máximo → corta.
- **Vela 3** (barra `i+1`): la ventana donde se entra. Nada fuera de ella.

Objetivo, idéntico en las cuatro ejecuciones: el **extremo opuesto del rango**
(`r_hi` en largos, `r_lo` en cortos).

## Las cuatro ejecuciones

Mismas señales, misma diana, distinta forma de entrar y de poner el stop. Eso es
lo que aísla lo que aporta el M1.

| | entrada | stop |
|---|---|---|
| **A · M15 a mercado** | apertura de la Vela 3 | extremo del barrido ∓ 1,0 p |
| **B · M15 orden stop** | buy/sell-stop en el extremo de la Vela 2, disparada dentro de la Vela 3 | extremo del barrido ∓ 1,0 p |
| **C · M1 confirmación** | apertura del M1 siguiente al primer M1 que **cierra** más allá del extremo de la Vela 2 | extremo del barrido ∓ 1,0 p |
| **D · M1 confirmación, stop en M1** | igual que C | extremo de las **3 velas M1 cerradas** hasta la confirmación ∓ 1,0 p |

**D es su método**: espera el cuerpo que confirma y deja el stop pegado, detrás
de las últimas velas de M1. Es lo que produce sus stops de 2 a 10 pips.

**D2**: igual que D pero con objetivo fijo **1:2** en vez del extremo del rango,
porque sus operaciones reales son a 1:2.

Se entra en la apertura de la vela siguiente a la que confirma, nunca en el
cierre de la que confirma: en real esa vela no ha cerrado cuando decides.

## Reglas de resolución

- Desde la vela de entrada, se busca stop u objetivo sobre M1.
- Si en el mismo minuto se tocan los dos, cuenta **SL**.
- Máximo 8 horas abiertas; lo que no resuelve sale a mercado y se marca «tiempo».
- **Sin filtro de R:R y sin tope diario ni de solapamiento** en el pase
  principal, para que las cuatro ejecuciones vean exactamente el mismo conjunto
  de señales. Con esos filtros cada ejecución se quedaría una muestra distinta y
  la comparación dejaría de significar nada.

Coste **1,43 pips** por operación redonda (`COSTE_real.md`), con la banda
1,28-1,58 como sensibilidad.

## Muestra

- **Principal**: EURUSD, 2020-01 a 2026-07, en las tres killzones de la guía
  (CET 08-11, 13-16, 16-18).
- **Secundarias declaradas**: solo Londres 08:00-11:00 CET; sin filtro horario;
  con las reglas canónicas (R:R ≥ 1,5, tope 3/día, sin solapar); GBPUSD y USDJPY.

## Métrica principal y umbral

**R neta por operación**, con su z. Cuatro ejecuciones contrastadas →
Bonferroni: hace falta **|z| > 2,50**.

Se reporta además, para cada una, el **acierto contra su propia geometría**
`1/(1+k)` con k = R:R mediana realizada. Es la única comparación honesta: una
ejecución con stop más estrecho tiene por fuerza más R y menos acierto, y eso
no es ventaja, es aritmética.

## Predicción firmada

Escrita antes de ver nada:

1. La **bruta en R** será mayor en D que en A, B y C, solo por el cambio de
   escala del stop.
2. La **bruta en pips** por operación será parecida en las cuatro.
3. El **coste sobre el riesgo** en D pasará del 25 %, y en A/B/C rondará el
   10-15 %.
4. El **acierto de cada una no superará su propia geometría** de forma
   significativa.
5. **Ninguna de las cuatro llegará a z > +2,50 en R neta.** La más negativa será
   D.

Si D sale positiva y significativa, la predicción está mal y eso es la noticia.

## Qué contaría como hallazgo

Solo esto: una ejecución con **z > +2,50 en R neta** que además **aguante** en
Londres solo, en GBPUSD y en USDJPY con el mismo signo. Cualquier cosa por
debajo se reporta como lo que es, un no.
