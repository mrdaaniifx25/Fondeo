# Bloque 8 · "Tomo o paso" — resultado

Preregistro sellado en `c7fd31d`, antes de ver una sola decisión.
240 señales de la estrategia del 71 % en M30, instrumento y fecha ocultos.
Completado entero: 240 de 240 decisiones.

## Lo primero, porque no es un detalle

Terminó el examen. Dentro de esas 240, en el orden en que las vio:

    racha de perdedoras seguidas que aguantó:   10
    bajada desde máximo que aguantó:         -17.4 R
    operaciones bajo cero durante el recorrido:  32

El bloque 7 lo abandonó con "salen muchas señales y ni un TP de los que
llevo". Este no. Es la primera evidencia del proyecto de que puede ejecutar
una regla con 65 % de perdedoras sin desviarse.

## La prueba principal, tal como estaba firmada

                           n   acierto   R bruta    R NETA
    ----------------------------------------------------------
       TODAS (regla ciega)   240     35.4 %    +0.222    +0.083
              las que TOMA   130     30.8 %    +0.062    -0.086
              las que DEJA   110     40.9 %    +0.411    +0.282

    diferencia tomadas - dejadas: -0.367 R  ·  z = -1.72  ·  p = 0.085
    umbral firmado: |z| > 1.96   ->   NO PASA

Formalmente: no concluyente. El umbral estaba puesto antes y no se mueve.

Materialmente: la dirección es inequívoca y coincide con todo lo demás del
proyecto. Lo que tomó pierde (-0.086); lo que dejó pasar gana (+0.282). Su
criterio no seleccionó las buenas: seleccionó las malas.

## Las cuatro predicciones firmadas

    1 · toma entre el 40 % y el 70 %                         OK   (54 %)
    2 · diferencia entre -0,10 y +0,25 y NO significativa    NO   (-0.367)
    3 · su acierto entre el 33 % y el 45 %                   NO   (30.8 %)
    4 · le cuesta más que el de roturas                      sin dato

La 3 falla por abajo: acertó menos de lo que yo predije en el escenario
pesimista. La 2 falla porque la diferencia se salió de la banda por el lado
malo, aunque sin alcanzar significación.

## Lo que este examen NO demuestra

Las 240 a ciegas dan +0.083 R netas, pero con error típico 0.106 (z = +0.78).
Este examen no prueba que la estrategia gane. La prueba de la estrategia
está en otro sitio: 568 operaciones en M30 y 246 en M60 del backtest.

## Hipótesis nueva, no conclusión

Partiendo el riesgo en tercios dentro de cada instrumento:

    stop ESTRECHO  toma 63 %  ·  tomadas -0.238  ·  dejadas +0.775   z = -2.60
    stop MEDIO     toma 54 %  ·  tomadas +0.348  ·  dejadas +0.320
    stop ANCHO     toma 46 %  ·  tomadas -0.360  ·  dejadas -0.067

Todo el daño está en el stop estrecho: toma más de esas y son las que peor
le salen. No estaba en el preregistro, así que es una hipótesis para una
prueba futura, no un hallazgo.

Sin patrón de revancha: toma el 56.5 % tras ganadora, 53.2 % tras perdedora,
55.7 % tras tres perdedoras seguidas. No se descompuso con las rachas.

## Conclusión operativa

Tomar las 240 sin filtrar bate a filtrarlas. La instrucción que sale de aquí
es: ejecutar la señal entera y no decidir. Y ya hay evidencia de que puede.
