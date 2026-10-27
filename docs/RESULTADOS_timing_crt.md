# Resultado · el timing del CRT, con la dirección dada por buena

Pre-registro: `docs/PREREGISTRO_timing_crt.md`.
Código: `bt/timing_crt.py` (preregistrado) y `bt/timing_crt_controles.py`
(**post hoc**, no estaba firmado — se marca y cuenta menos).
13.627 velas H4 en EURUSD, oro y DAX. Costes ECN.

---

## Lo primero: fallé tres de mis cuatro predicciones

| firmé | salió | |
|---|---|---|
| el acierto crudo subirá con la regla del vídeo | **bajó**: 36,7 % contra 42,6 % del ciego (porque sube el R:R) | ✘ |
| **no superará su nulo geométrico; exceso entre −2 y +2 pp** | **+6,2 pp** | ✘ |
| **la espera al azar capturará casi toda la mejora (±1 pp)** | **+2,0 pp de diferencia** | ✘ |
| la esperanza por día bajará | **subió** con oráculo (+0,73 contra +0,27); bajó sin él | ✘/✔ |

Mi modelo del mundo estaba equivocado aquí. Conviene decirlo antes de contar
nada más, porque lo que sigue lo descubrí **después** de ver que me había
equivocado, y eso vale menos que una predicción acertada.

## Sin ventaja de dirección: la regla no aporta nada

```
  regla                           n    R:R  acierto     geom  exceso  neta/día
  1 ciego (cada vela H4)      14254   8,81    37,9%    37,7%    +0,1    -0,882
  2 CRT alineado               6124  11,46    30,3%    29,9%    +0,3    -0,268
  3 espera al azar (CONTROL)   6124   8,71    37,1%    37,5%    +0,2    -0,438
  4 espera fija (2 velas H4)   6122  10,05    37,9%    37,7%    +0,2    -0,298
```

**CRT menos azar: +0,1 pp.** Comprando siempre, esperar el rango alineado no se
distingue de esperar al azar.

Y una trampa que conviene nombrar: la `neta/día` de la regla 2 (−0,268) parece
mucho mejor que la del ciego (−0,882). **No es mejor ventaja: es operar menos.**
Con esperanza negativa, cualquier filtro «mejora» el resultado por la vía de no
operar. Eso explica la mitad de los filtros que se venden.

## Con la dirección dada por buena: aquí sí pasa algo

Sesgo oráculo = la dirección real de la semana, conocida de antemano. Mira al
futuro **a propósito**: es la implementación fiel de su premisa.

```
  regla                                   n    R:R  acierto     geom  exceso   R neta  neta/día
  1 ciego                             13627  10,14    42,6%    38,4%    +4,2  +0,0342   +0,266
  2 CRT alineado                       5473   9,82    36,7%    30,4%    +6,2  +0,2325   +0,728
  5 retroceso GENÉRICO (sin CRT)       4411  15,45    33,1%    25,8%    +7,3  +0,1572   +0,397
```

**El exceso pasa de +4,2 a +6,2 pp sólo por esperar.** z de permutación +6,35,
p < 0,0001. **Él tiene razón en lo que afirma**: con el sesgo correcto, el
instante de entrada cambia el resultado, y mucho.

Lo dijo así y así sale: *«de nada sirve tener el bias bien si estáis comprando
en los momentos en los que no toca»*.

## Pero el mecanismo no es CRT. Es «compra el retroceso».

El control lo señala el propio vídeo en su última parte:

> *«lo que os he dado yo en este vídeo no deja de ser al final **esperar un
> retroceso** para sumarte el movimiento»*

Así que se mide contra un retroceso genérico: *el cierre está en el tercio bajo
del rango de las últimas 6 velas H4*. Ni rangos, ni barridos, ni turtle soup.
Sólo «ha retrocedido».

```
  exceso:   ciego +4,2   ·   CRT alineado +6,2   ·   retroceso genérico +7,3
  CRT menos retroceso genérico:  -1,0 pp
```

**El filtro tonto gana.** Y la descomposición en las cuatro casillas lo cierra:

```
  casilla                                 n    acierto    geom   exceso
  CRT y retroceso a la vez             2599     30,7%    22,4%    +8,3
  retroceso SIN CRT                    1812     36,5%    30,7%    +5,8
  CRT SIN retroceso                    2874     42,0%    37,7%    +4,3
  ciego (referencia)                  13627     42,6%    38,4%    +4,2
```

**Cuando el rango CRT se alinea pero el precio NO ha retrocedido de verdad, el
exceso es +4,3 — idéntico al ciego.** Cero valor añadido.

Todo el aporte de CRT viene de las veces que coincide con un retroceso real. Es
decir: **el «rango alineado» es un detector ruidoso de retrocesos.** Funciona
porque detecta retrocesos, no porque detecte rangos. Y un detector directo de
retrocesos lo hace mejor.

## Lo que sí hay que concederle a CRT

En la métrica del dinero, CRT gana: `neta/día` +0,728 contra +0,397 del
retroceso genérico y +0,266 del ciego.

Pero el motivo no es la ventaja, es el **R:R**: CRT entra con R:R 9,8 y el
retroceso genérico con 15,5. El mismo exceso de acierto convertido a un R:R más
moderado da más dinero. Eso es una observación sobre **tamaño de objetivo**, no
sobre habilidad — y es real y útil: *los objetivos más cercanos convierten mejor
la misma ventaja*. Pero no valida los rangos.

*(Y el retroceso genérico solo, sin CRT, da neta/día **−0,061**: negativa. Con
R:R 17,4 el objetivo casi nunca llega. Un exceso de acierto no es dinero
automáticamente.)*

## Lo que esto NO es

**No es operable.** Todo lo de arriba vive debajo del oráculo: hay que saber de
antemano la dirección de la semana. Sin eso —la tabla de «comprar siempre»— el
exceso es +0,3 pp y la neta/día es negativa en las cuatro reglas.

Y eso es exactamente lo que el proyecto ha medido nueve veces: **la dirección es
lo que no se puede saber.** Este vídeo asume resuelto el único problema que hay,
y sobre esa base construye algo que sí funciona. Su frase *«obviamente íbamos a
estar buscando compras»* es toda la estrategia, y es la parte que no está medida
en ningún sitio.

## El resumen honesto

1. **Su afirmación es correcta y la firmé al contrario.** Con el sesgo bien, el
   timing vale +2 a +3 puntos de acierto. No es ruido: z +6,35.
2. **Su explicación no es correcta.** No son los rangos H4: es el retroceso. Un
   detector de retrocesos de dos líneas lo hace mejor que el aparato entero.
3. **Y nada de esto sirve**, porque depende de acertar la dirección de la
   semana, que es precisamente lo que no se sabe hacer.

Es la primera vez en tres meses que un vídeo acierta en el *qué*. Sigue
fallando en el *por qué*, y el *para qué* sigue fuera de alcance.
