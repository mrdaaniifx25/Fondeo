# Resultados · el reloj, sin patrón ninguno

Pre-registro: `docs/PREREGISTRO_reloj.md`, subido **antes** de medir.
Código: `bt/reloj.py`. EURUSD 2021-2026, oro y DAX 2023-2026.

## Veredicto

**El reloj no tiene dirección.** Cada sesión se lleva exactamente la parte de la
deriva del instrumento que le toca por horas, ni más ni menos.

## El principal declarado · Londres en EURUSD

```
  n 1.449   bruto -0,0437 [-0,0952, +0,0078]   muro 0,0507   NETO -0,0944
```

No es que salga plano: sale **negativo**. Comprar la sesión de Londres en EURUSD
todos los días pierde, y pierde en **cinco de los seis años**:

```
  2021 -0,0877 · 2022 -0,0501 · 2023 -0,0344
  2024 -0,0851 · 2025 -0,0201 · 2026 +0,0268
```

Es la deriva bajista del euro en el periodo, repartida por el día. No es un
efecto de sesión.

## Las nueve sesiones, en bruto

```
  EURUSD   Asia +0,0242   Londres -0,0437   NuevaYork +0,0015
  oro      Asia +0,0916   Londres +0,0616   NuevaYork -0,0038   <- Asia "CRUZA"
  DAX      Asia -0,0013   Londres +0,0559   NuevaYork +0,0552
```

La sesión de Asia en oro cruza el muro con el intervalo limpio. **Y no significa
nada**, como demuestra el control siguiente.

## El control que decide

El oro sube un 40 % entre 2023 y 2026. Cualquier trozo de su día sale positivo.
La pregunta correcta no es «¿rinde esta sesión?» sino **«¿rinde más de lo que le
toca por horas?»**

```
  instrumento  sesión         horas  su parte  deriva real  le toca   EXCESO      t
  EURUSD       Asia 00-08         8      34 %    +0,0043%  -0,0013%  +0,0056%  +1,22
  EURUSD       Londres 08-14      6      26 %    -0,0111%  -0,0010%  -0,0101%  -1,51
  EURUSD       NuevaYork 14-23    9      39 %    +0,0005%  -0,0015%  +0,0020%  +0,21

  oro          Asia 00-08         8      36 %    +0,0610%  +0,0347%  +0,0263%  +1,21
  oro          Londres 08-14      6      27 %    +0,0340%  +0,0261%  +0,0079%  +0,44
  oro          NuevaYork 14-23    9      41 %    -0,0031%  +0,0391%  -0,0422%  -1,44

  DAX          Asia 00-08         8      40 %    -0,0005%  +0,0303%  -0,0308%  -2,17
  DAX          Londres 08-14      6      30 %    +0,0335%  +0,0227%  +0,0108%  +0,53
  DAX          NuevaYork 14-23    9      45 %    +0,0381%  +0,0341%  +0,0040%  +0,16
```

**La sesión de Asia en oro, que parecía cruzar, tiene un exceso de t = +1,21.**
Era el oro subiendo, nada más.

De las nueve celdas, una sola pasa de |t| = 2 — el Asia del DAX, y **en
negativo**. Con nueve celdas, la mejor por azar sale a 1,7. No queda nada.

## El reloj hora a hora · exploratorio

```
  EURUSD, muro de una hora suelta: 0,1339
  00h +0,1642*  09h +0,0638*  12h -0,0526*  13h -0,1357*
  14h +0,0630*  22h -0,1742*  23h +0,2632*
```

Las tres grandes —22h, 23h y 00h— son **las horas del rollover diario**, donde
el fichero tiene huecos y la «hora» no es una hora de mercado real. Son un
artefacto del dato, no un efecto. Las demás no llegan ni al muro ni al sesgo de
selección de +0,065.

## La noche contra el día

```
  EURUSD   noche +0,0043   día -0,0085
  oro      noche -0,0106   día +0,0797  CRUZA
  DAX      noche +0,0303   día +0,0800  CRUZA
```

Lo que «cruza» es comprar y mantener durante el día en dos instrumentos que
subieron un 40 %. Es la deriva otra vez.

Y el efecto documentado en índices de bolsa —que casi todo el rendimiento pasa
de noche— **no aparece en el DAX**: aquí el día (+0,080) rinde más que la noche
(+0,030). Tiene sentido: el CFD cotiza casi 24 horas, así que no hay un hueco
nocturno de verdad.

## El día de la semana · EURUSD

```
  lunes +0,0627   martes -0,0248   miércoles +0,0125
  jueves -0,0122  viernes -0,0747
```

Todos con el cero dentro del intervalo. Nada.

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. el principal con neto > 0 y el IC limpio | **NO.** −0,0944, y negativo cinco de seis años |
| 2. mismo signo partido por años | negativo en cinco de seis |
| 3. mismo signo en oro y DAX | Londres: EURUSD −0,04, oro +0,06, DAX +0,06 — no coinciden |

## Récord de predicciones

Cuatro de cinco.

| predicción | resultado |
|---|---|
| el principal saldrá plano | sale **negativo**, −0,0437 ✔ (más que plano) |
| habrá horas que parezcan buenas y ninguna pasará el filtro | las tres grandes son el rollover ✔ |
| lo único que puede salir es la noche del DAX | +0,0303 con el cero dentro; y el día rinde más ✘ |
| el día de la semana saldrá plano | plano ✔ |
| el reloj no tiene dirección, sólo volumen | exacto ✔ |

## Lo que cierra

Ahora sí está cerrada la familia de sesiones, y por la puerta buena: se ha hecho
**la pregunta simple** —¿qué hace el precio en cada hora, sin condición ninguna?—
y la respuesta es que cada sesión se lleva su parte proporcional de la deriva del
instrumento y nada más.

Las 34 pruebas condicionales anteriores salían planas. Ésta explica por qué: **no
hay nada debajo que condicionar.**
