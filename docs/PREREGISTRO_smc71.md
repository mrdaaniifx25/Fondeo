# Preregistro · el pase limpio de la estrategia del 71 %

Sellado **antes** de correr nada de lo que hay aquí dentro.
`RESULTADOS_smc_71.md` es exploratorio y ya ha visto los 7 instrumentos y las dos
épocas. **No me queda reserva temporal.** Lo que sí está intacto son tres cosas, y
son las que deciden si el hallazgo es real o es mi implementación.

## Lo que ya sé y NO puede volver a contar

```
  1.111 operaciones · acierto 32,6 % contra 29,0 % · z +2,63
  R bruta +0,124, positiva en 6/7 · R neta positiva en 4/7
  épocas: +0,128 (20-22) y +0,121 (23-26)
```

## Prueba 0 · AUDITORÍA · el relleno optimista

En la versión exploratoria, cuando la limitada del 71 % se rellena en una vela,
**esa misma vela no puede saltarme el stop**: la resolución empieza en la
siguiente. Es optimista: una vela que llega al 71 % puede seguir hasta el 100 %
en el mismo minuto.

Se rehace resolviendo la vela del relleno de forma **pesimista**: si esa vela
también toca el stop, cuenta como −1.

**Predicción firmada:** la ventaja baja pero sobrevive. R bruta agregada **> 0**
con **z > +1,64**. Si se cae, era mi supuesto y no el mercado.

## Prueba 1 · los parámetros que elegí yo

Su especificación fija M15 y el 71 %. **H4V=20 velas para el rango de H4 y
VIDA=96 horas los elegí yo.** Si el efecto depende de ese punto exacto, es ajuste.

Rejilla: H4V ∈ {10, 40} × VIDA ∈ {48, 192}, cuatro combinaciones, 7 instrumentos.

**Predicción firmada:** R bruta agregada positiva en **al menos 3 de las 4**
combinaciones.

## Prueba 2 · otra temporalidad de ejecución

Si el mecanismo es real —barrido, ruptura de estructura, retroceso— debe aparecer
también en M5 y M30, más fuerte o más débil pero presente. **Nunca las he corrido.**

**Predicción firmada:** R bruta positiva en **las dos**, y acierto por encima del
29,0 % geométrico en las dos.

## El veredicto

- **Las tres pasan** → el efecto es real y merece un pase con dinero de mentira
  antes que ninguna otra idea del proyecto.
- **La 0 falla** → era mi relleno optimista. Se cierra y se escribe.
- **La 1 o la 2 fallan** → el efecto existe solo en un punto concreto de
  parámetros. Se reporta como no concluyente.

Un solo pase. Se reporta salga lo que salga.

## Lo que este pase NO puede contestar

**Si es rentable.** La R neta media es −0,066 y solo sale positiva donde el coste
pesa menos del 10 % del riesgo — y esos costes son **estimaciones mías**, no
medidas. Ninguna de estas tres pruebas cambia eso.
