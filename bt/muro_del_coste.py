"""El muro del coste: cuanta ventaja hace falta segun el tamano del stop.

Para 1:k, la geometria pura da P(TP) = 1/(1+k), independientemente del stop.
El equilibrio con coste es p* = (1 + c/s)/(1+k). Restando:

    ventaja necesaria = (c/s)/(1+k)   puntos de acierto sobre la geometria

Todo el proyecto ha operado con stops de 3 a 10 pips. Ahi el coste es el 15-50 %
del riesgo y hace falta batir a la geometria por 5-12 puntos. Ninguna regla
mecanica medida en este proyecto ha superado los +4.

  python3 bt/muro_del_coste.py
"""
COSTE = 1.43
print("="*78)
print("CUÁNTA VENTAJA SOBRE LA GEOMETRÍA HACE FALTA, SEGÚN EL STOP  (coste 1,43 p)")
print("="*78)
print(f"  {'stop':>7s} {'coste/riesgo':>13s} {'1:1':>10s} {'1:2':>10s} {'1:3':>10s}"
      f"   {'horizonte típico'}")
print("  " + "-"*76)
HOR = {3:"minutos", 6:"media hora", 10:"una hora", 15:"unas horas", 25:"media sesión",
       40:"una sesión", 60:"un día", 100:"dos o tres días", 200:"una semana o más"}
for s in (3, 6, 10, 15, 25, 40, 60, 100, 200):
    fila = f"  {s:5d} p {100*COSTE/s:12.1f}%"
    for k in (1, 2, 3):
        fila += f" {100*(COSTE/s)/(1+k):9.1f}pt"
    print(fila + f"   {HOR[s]}")
print("""
  Lo que ha conseguido cada regla mecánica medida en el proyecto, en puntos
  por encima de su propia geometría:

    rotura del nivel de Asia (M5)          -2,5 pt
    cascada H4/M15/M5/M1, 90 celdas        -1 a +1 pt
    rechazo del nivel de Asia (M5)         +1,4 pt
    modelo de 16 variables (M5)            +4,1 pt   <- el mejor de todos
    CRT en H4 con stop en la mecha         +2,9 pt

  Con stop de 6 pips y 1:2 hacía falta +8,0. El mejor resultado del proyecto se
  queda en la mitad. No es que las reglas sean malas: es que el muro está
  demasiado alto para ese tamaño de stop.

  Con stop de 60 pips y 1:2 harían falta +0,8 puntos. Con 100, +0,5.
  Ahí sí cabe una ventaja pequeña y real.""")
