# Resultado · "hay otro rango pendiente de ocurrir"

La idea es del usuario, y es la mejor hipótesis que se ha probado en todo el
proyecto. Código en `bt/crt_objetivo_pendiente.py` y `bt/crt_contexto_h12.py`.

## Qué afirma

> *"con todos los conceptos de objetivos, POI y demás… si pasa lo que he visto
> es porque hay algún otro rango pendiente de ocurrir"*

O sea: un CRT no falla por sí mismo. Falla cuando **existe un objetivo superior
sin cumplir** tirando del precio en sentido contrario. Es la explicación clásica
de ICT/CRT y **no estaba medida**, porque no es lo mismo que las dos cosas que
sí había medido:

- `RESULTADOS_crt_semanal.md` medía la **dirección** de la semana anterior.
- `RESULTADOS_crt_cascada.md` medía si los marcos superiores estaban
  **activados** en el mismo sentido.

Ninguna de las dos es "hay un objetivo **pendiente de cumplirse**". Eso es un
estado que dura en el tiempo, no una dirección ni una activación.

## Cómo se construye, sin mirar al futuro

En el marco diario se recorren las velas buscando CRT: la vela barre un extremo
de la anterior y **cierra de vuelta dentro**. Eso deja un objetivo —el extremo
opuesto— que queda **pendiente desde el cierre de esa vela** hasta que el precio
lo toca, o hasta que caducan 10 días.

En cada señal de H12 se anota si en ese instante hay un objetivo diario
pendiente y hacia dónde tira. Todo se lee con lo que se sabía en el momento.

## El resultado, y va en la dirección que él predijo

    filtro                              n     R:R  acierto    azar   R BRUTA       z    R NETA
    sin filtro                       4454    3,41   20,5 %  31,1 %  +0,0392   +1,54   -0,0239
    OBJ diario pendiente A FAVOR     1946    3,18   21,8 %  32,8 %  +0,0717   +1,89   +0,0104
    OBJ diario pendiente EN CONTRA   1875    3,63   19,5 %  29,5 %  +0,0037   +0,09   -0,0620
    sin objetivo pendiente            633    3,50   19,4 %  30,3 %  +0,0445   +0,64   -0,0166

**A favor es la única celda con R neta positiva de todo el barrido**, y la de
mayor `z` bruta. En contra es exactamente cero. El orden es el que la hipótesis
predice.

Para comparar, los filtros que proponen los vídeos, sobre las mismas señales:

    rango diario a favor (la cascada) 1538    3,73   16,6 %  28,2 %  -0,0129   -0,30   -0,0755
    sesgo semanal a favor            2204    3,38   19,4 %  30,8 %  +0,0032   +0,09   -0,0589
    sesgo diario a favor             1695    2,58   26,5 %  37,8 %  +0,0430   +1,18   -0,0110

La cascada **empeora** el resultado. El sesgo semanal **borra** la ventaja
bruta. Su idea es mejor que las tres.

## Y aun así no pasa el control

El contraste declarado es *a favor menos en contra*: **+0,0681 R bruta**.

Se baraja la etiqueta del objetivo pendiente sobre las mismas señales, lo que
responde de una vez a "¿es casualidad?" y a "¿es de haber probado 14 filtros?",
porque el nulo pasa por el mismo embudo:

    permutación simple (4.000)     desv 0,0559   ·   p = 0,220   ·   +1,22 desviaciones
    rotando semanas enteras        desv 0,0523   ·   p = 0,199   ·   +1,30 desviaciones

**p ≈ 0,2.** Una de cada cinco veces el azar produce una separación así de
grande. No es señal.

### Y hay algo peor que el p-valor

La hipótesis dice que el mecanismo es "un objetivo superior sin cumplir tira del
precio". Si eso fuera cierto, **tendría que funcionar igual o mejor en semanal**,
que es un marco más grande. Va al revés:

    OBJ semanal pendiente a favor   n 1835   bruta +0,0085
    OBJ semanal pendiente en contra n 1797   bruta +0,0578
    DIFERENCIA                                     -0,0494

El signo se invierte. Un mecanismo real no cambia de sentido al subir de marco.

### Estabilidad de la celda buena

    EURUSD  665  +0,1181  z +1,80   |   2020 +0,1336   2023 +0,1385
    GBPUSD  664  +0,0116  z +0,18   |   2021 +0,0738   2024 -0,0657
    USDJPY  617  +0,0865  z +1,27   |   2022 +0,1767   2025 +0,0872
                                    |                  2026 -0,0788

Positiva en 5 de 7 años, pero los dos negativos son **2024 y 2026**, los más
recientes. Y descansa sobre EURUSD.

## Veredicto

La intuición apuntaba al sitio correcto y bate a todo lo que proponen los
vídeos. Pero la separación es de tamaño azar (p ≈ 0,2), el mecanismo se
invierte al subir de marco, y la mitad reciente de la muestra va en contra.

Está en el simulador como filtro (`Objetivo diario pendiente a favor`) con este
control escrito al lado, para que nadie lo lea sin él. En EURUSD solo, el total
pasa de −22,4 R a +35,1 R — y esa es exactamente la clase de cifra que un
control existe para no creerse.
