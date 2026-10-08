# Resultado · el CRT al revés

Ejecutado el 28 de agosto de 2026 según `docs/PREREGISTRO_crt_invertido.md`.
`bt/crt_invertido.py`. Una sola pasada.

## Se confirma la predicción: no funciona

```
2020-2025 · 1.232 operaciones      %TP     R/op   NETA/día       z     PF    €/mes
  el CRT como está                41,6%   -0,075     -0,184   -4,39   0,77    -262€
  el CRT al revés                 40,7%   -0,020     -0,118   -2,76   0,85    -167€
```

En 2026 enero-julio, igual: el invertido da −0,203 por día.

## Y el hallazgo que cierra la idea para siempre

**Las dos versiones pierden en bruto.** −0,075 la original y −0,020 la invertida.
No es que una sea el negativo de la otra.

```
  gana la original ......... 41,6 %
  gana la invertida ........ 40,7 %
  suma ..................... 82,3 %

  PIERDEN LAS DOS .......... 17,7 %   (218 de 1.232 operaciones)
  ganan las dos .............  0,0 %
```

**Una de cada seis veces pierden las dos.** Porque una operación con stop y
objetivo no tiene un complemento: entre el stop de una y el objetivo de la otra
hay una franja donde el precio toca los dos stops sin llegar a ningún objetivo.
En esa franja pierdes compres o vendas.

Por eso «hacer lo contrario» no convierte una estrategia perdedora en ganadora.
Sólo funcionaría si la estrategia tuviera **poder predictivo negativo**, es
decir, si acertara mucho menos del 33 % que da el azar. Ninguna de las nuestras
lo tiene: todas rondan el azar o lo superan ligeramente.

## La regla, para no volver a plantearla

```
  neta = bruta - coste
  neta al revés ≈ (algo peor que -bruta) - coste
```

Darle la vuelta sólo puede salir si **la bruta es más negativa que el coste**, y
aun así se pierde la franja del 17,7 %. En este proyecto:

```
  familia                       bruta     coste   ¿al revés?
  cascada M15                  +0,096     0,326   no, la bruta es positiva
  barrido de Asia M5           +0,080     0,318   no
  invertido del contexto       +0,109     0,298   ya era el invertido
  CRT                          -0,069     0,078   probado: sigue perdiendo
```

## Lo que sí dice el CRT y no habíamos mirado así

El CRT es la única familia del proyecto donde **el coste no es el problema**:
stops de 19,3 pips de mediana, coste 0,078 R por operación, el 7,8 % del riesgo.
Los barridos de Asia pagan el 30 %.

Y aun con esa ventaja estructural, su bruta es −0,069. El CRT no falla por
fricción: falla porque no acierta. Acierta el 41,6 % cuando su propia geometría
(rr mediano 1,32) da el 43,1 %.

Son dos fracasos de naturaleza distinta y conviene no confundirlos:

- **Los niveles de sesión** tienen ventaja y no cabe en el coste.
- **El CRT** cabe de sobra en el coste y no tiene ventaja.
