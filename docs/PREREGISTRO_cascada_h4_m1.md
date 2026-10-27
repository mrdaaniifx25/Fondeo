# Preregistro · H4 marca, CRT en M15, confirma M5, ejecuta M1

Escrito antes de correr `bt/cascada_h4_m1.py`. Un solo pase.

Es lo que él pide, y nada más: *«el CRT en M15, que pegues un vistazo en H4 a la
dirección del mercado, con confirmación en M5 y ejecución en M1, teniendo en
cuenta también el high y el low de Asia»*.

## Los cuatro pisos

**1 · H4 — la dirección.** Signo de `cierre[última cerrada] − cierre[4 cerradas
antes]`, o sea el sentido de las últimas **16 horas** de H4. Solo cuentan velas
**ya cerradas** en el instante de la señal: el índice se busca con
`ts − duración`, que es la corrección de `CORRECCION_mirada_al_futuro.md`.
Solo se opera **a favor** de ese signo.

**2 · M15 — el CRT.** Rejilla alineada a :00/:15/:30/:45.

```
Vela 1   el rango
Vela 2   la manipulación: barre UN solo lado del rango y CIERRA dentro
Vela 3   la ventana donde se busca la confirmación
```

Barre el mínimo → operación larga. Barre el máximo → corta. La turtle soup y la
manipulación del CRT son aquí **el mismo mecanismo**: barrido falso que vuelve
dentro. No se modelan por separado.

**3 · Asia — el filtro de confluencia.** Sesión asiática **00:00-08:00, hora de
Madrid**. Dos clases de nivel, las dos que él usa:

- el **alto y el bajo de la sesión entera**
- los **altos y bajos intermedios**: fractales de M15 dentro de la ventana de
  Asia, con dos velas a cada lado

Se exige que el extremo barrido por la Vela 2 caiga **a 3 pips o menos** de
alguno de esos niveles. Es decir: el CRT solo vale si ocurre **en un nivel de
Asia**, no en cualquier sitio.

**4 · M5 — la confirmación.** Dentro de la Vela 3, una vela de M5 tiene que
**cerrar** más allá del extremo de la Vela 2 en el sentido de la operación.
Cierre, no mecha: es su regla, la que explicó hoy.

**5 · M1 — la ejecución.** Entrada en la **apertura del primer M1** posterior al
cierre de esa vela de M5. Nunca en el cierre mismo: en real esa vela no ha
cerrado cuando decides.

## Configuración principal

| | |
|---|---|
| stop | extremo de las **3 velas M1 cerradas** antes de la entrada, ∓1 pip — lo que él hace |
| objetivo | **1:2** fijo |
| ventana | 08:00-17:00 hora de Madrid |
| vida máxima | 8 horas |
| coste | 1,43 pips redondos |
| empate en el minuto | cuenta **SL** |

Una sola configuración principal → umbral **|z| > 1,96** sobre la R neta por
operación.

## Secundarias declaradas

Se reportan, no se reclaman:

- sin filtro de H4 · sin filtro de Asia · sin ninguno de los dos
- stop en el extremo del barrido en vez de en M1
- objetivo en el extremo opuesto del rango de M15 en vez de 1:2
- solo Londres 08:00-11:30
- GBPUSD y USDJPY

## Predicción firmada

1. El filtro de Asia **reducirá mucho la muestra** —de miles a cientos— y subirá
   el acierto bruto un poco, no lo bastante.
2. El filtro de H4 **no cambiará el acierto** de forma apreciable. Ya se midió una
   vez, con la mirada al futuro corregida: a favor 30,8 %, en contra 30,8 %,
   idénticos.
3. La configuración principal saldrá **neta negativa**, entre −0,3 y −0,9 R, por
   la misma razón de siempre: el stop de M1 deja el coste por encima del 40 % del
   riesgo.
4. **Ninguna celda llegará a z > +1,96 en R neta.**

De los dos filtros, el de Asia es el único con mecanismo que se entiende, así que
es donde daría la sorpresa si la hay.

## Qué contaría como hallazgo

R neta con **z > +1,96** en la principal, que además aguante en Londres solo y
mantenga el signo en GBPUSD y USDJPY.
