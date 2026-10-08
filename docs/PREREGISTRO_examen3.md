# Preregistro · tercer bloque del examen

Escrito antes de generar los datos. **24 sesiones nuevas**, sin solapamiento con
los bloques 1 y 2.

## De dónde sale este diseño

Juntando los dos bloques —53 operaciones, 40 sesiones— aparecen dos cosas:

**1 · La ventaja aguanta un coste mucho peor del que suponemos.**

| coste redondo | R neta / op | z |
|---|---|---|
| 1,28 p | +0,451 | +2,28 |
| **1,43 p** | **+0,426** | **+2,16** |
| 2,00 p | +0,332 | +1,69 |
| 3,00 p | +0,167 | +0,85 |

Su neta llegaría a cero con **4,01 pips** de coste redondo, casi el triple del
real. Es la primera vez en el proyecto que algo tiene margen sobre el coste en
vez de morir por él.

**2 · Se le cae el rendimiento a mitad de bloque, y pasa en los dos.**

| | n | acierto | R neta media |
|---|---|---|---|
| primera mitad de cada bloque | 27 | **70,4 %** | +0,866 |
| segunda mitad | 26 | **36,4 %** | −0,031 |

Fisher p = 0,023. Y no es un bloque: es el 1 (72,7 % → 45,5 %) **y** el 2
(73,3 % → 25,0 %). En la muestra conjunta, *el número de operación dentro del
bloque* separa ganadoras de perdedoras con t = −2,44 (p = 0,015), y es la única
variable de las nueve medidas que lo hace.

Él lo dijo antes de que yo mirara. Es **post hoc** y por eso se pone a prueba
aquí, declarado antes.

## Diseño

- **24 sesiones**, en **tres tandas de ocho**, con un descanso real entre tandas.
- La página **registra la hora de cada decisión**. No dependo de que él recuerde
  cuándo se cansó: se mide.
- Una tanda nueva se detecta por un hueco de **más de 20 minutos** entre
  decisiones.
- Todo lo demás igual: 08:00-11:30, cuatro gráficos, él pone el stop, 1:2 fijo,
  ve el resultado de cada operación.

## Contrastes principales

Los mismos tres del bloque 2, a una cola, **y los tres tienen que salir**:

| | umbral |
|---|---|
| acierto sobre el 33,3 % geométrico | z > +1,64 |
| R neta por operación | z > +1,64 |
| diferencia contra la regla mecánica, emparejada por día | z > +1,64 |

## El contraste que de verdad se pone a prueba

**¿Desaparece la caída si descansa?**

Se compara el acierto de las decisiones **1-4 de cada tanda** contra las **5-8**.

```
si la diferencia baja de los 34 puntos observados  ->  descansar lo arregla
si sigue siendo de ~34 puntos                      ->  no es cansancio de tanda,
                                                       es otra cosa
si no hay diferencia en ninguna parte              ->  la caída era ruido
```

## Predicción firmada

1. **28 a 40 operaciones** en 24 sesiones.
2. Acierto global **entre el 48 % y el 60 %**.
3. R neta positiva, **entre +0,25 y +0,55**, y esta vez **sí** pasará el umbral.
4. Volverá a batir a la regla, z **> +2,0**.
5. **La caída se reducirá a la mitad o menos** —de 34 puntos a menos de 17— al
   partir en tandas de ocho.
6. Su stop mediano se quedará **entre 6 y 8 pips**, como en el bloque 2.

La 5 es la que decide el diseño de todo lo que venga después. Si descansar
arregla el 34 %, la regla operativa deja de ser sobre el gráfico y pasa a ser
**cuántas decisiones seguidas puede tomar**, que es un tipo de regla que nunca
habíamos considerado.

## Qué contaría como hallazgo

Los tres umbrales, **y** que la caída se reduzca. Si pasan los tres pero la caída
sigue igual, hay ventaja y no sabemos gestionarla. Si no pasan los tres, dos
bloques buenos y uno malo son tres bloques que no deciden nada.
