# Resultado · barrido de M15 + estocástico de M1

Idea del usuario: *"estocástico en M1 y buscar reversiones de M15. Si hay
sobrecompra por encima del 80 y en M15 hay un liquidity sweep, subirse al
movimiento."* Código en `bt/barrido_m15_esto_m1.py`.

Seis instrumentos, **3.761.025 operaciones**, `z` agrupado por año. Se miden
las dos direcciones sobre exactamente las mismas señales: la **reversión** que
propone, y la **continuación** como control.

## El resultado

       direccion |       n   riesgo   coste |   R BRUTA       z |    R NETA       z | inst +
    continuacion | 2901396     7,3p  32,5% |   -0,0245   -9,66 |   -0,3490  -28,49 |   0/6
       reversion |  859629     3,9p  50,6% |   -0,0030   -0,28 |   -0,5095  -37,42 |   0/6

**En bruto, la reversión es cero exacto: −0,0030 con z −0,28 sobre 859.629
operaciones.** Con esa muestra, si hubiera algo se vería. No lo hay. Y la
continuación tampoco: −0,0245.

O sea que **ni siquiera llega a ser un problema de costes**. Debajo no hay nada.

Por instrumento, la reversión en bruto:

                 n   riesgo   coste     BRUTA       z      NETA
    EURUSD   86808     2,6p  64,5%   +0,0626   +4,02   -0,5820
    GBPUSD  130017     2,8p  68,1%   +0,0572   +3,52   -0,6238
    USDJPY  150291     3,0p  61,7%   +0,0141   +1,14   -0,6028
    XAUUSD   35457     2,9p  13,0%   +0,0046   +0,22   -0,1256
    SPX500   81681     2,7p  26,7%   -0,0393   -1,82   -0,3061
    NAS100  375375     5,2p  45,8%   -0,0386   -2,97   -0,4962

Las divisas dan bruto ligeramente positivo y los índices ligeramente negativo:
signos cruzados, o sea nada. Pero fíjese en EURUSD, que es el mejor caso:
**bruta +0,0626 con un coste del 64,5 % del riesgo.** Haría falta ser diez
veces mejor solo para empatar.

Y ensanchar el stop no lo arregla, porque no hay ventaja bruta que rescatar:

       direccion     stop  vent |   riesgo   coste     BRUTA      NETA
    continuacion   5velas    24 |     9,2p  25,5%   -0,0199   -0,2751
       reversion   5velas    24 |     4,0p  49,7%   -0,0109   -0,5080

## El umbral que cierra el scalping, para cualquier estrategia

Para no perder dinero hace falta: **ventaja bruta ≥ coste / riesgo**. En EURUSD
el coste medido es 1,43 pips:

        stop    coste (% del riesgo)   ventaja bruta necesaria
       3 p            47,7 %                  0,477 R
       5 p            28,6 %                  0,286 R
      10 p            14,3 %                  0,143 R
      20 p             7,2 %                  0,072 R
      50 p             2,9 %                  0,029 R

Y ahora el dato que lo cierra:

    la mayor ventaja bruta medida en TODO el proyecto: +0,082 R (el CRT)
    stop mínimo para que esa ventaja empate:           17,4 pips

**Con la mejor ventaja que se ha encontrado en dos meses, el stop tiene que ser
de al menos 17 pips.** Esta idea usa 3,9. Está diez veces por debajo del umbral
aritmético, y eso no depende del patrón: depende de la división.

## Veredicto

La idea no falla por el filtro ni por la temporalidad. Falla dos veces:

1. **No hay ventaja bruta**: −0,0030 con z −0,28 sobre 859.629 operaciones.
2. **Y aunque la hubiera**, con un stop de 3,9 pips habría que superar el
   50,6 % del riesgo solo para empatar.

Cualquier variante que ejecute en M1 con stops de pocos pips está descartada
por la segunda razón antes de mirarla, sea cual sea el patrón.
