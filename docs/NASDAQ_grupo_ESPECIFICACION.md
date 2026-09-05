# La estrategia del grupo · especificación completa

Reconstruida de 20 transcripciones. Esto es lo que se va a programar.
Cada regla lleva la transcripción de la que sale.

## 0 · Instrumentos

    Se operan NASDAQ y SP500. Están correlacionados y se miran los dos
    SIEMPRE, aunque solo se entre en uno.
    Él opera el MINI de la CME, no el micro.                      (nº19)

## 1 · VENTANAS  ·  una operación por apertura

    Frankfurt    08:00 - 09:00  hora de España
    Londres      09:00 - 10:00  hora de España
    Nueva York   09:30 - 11:30  hora de Nueva York      ("los días grandes")

    Premarket de acumulación de NY: 09:00 - 09:29 NY.             (nº15)
    No se entra mientras sale una noticia de alto impacto, pero los días
    de noticias SÍ se operan: "es gasolina para el precio".        (nº12)

## 2 · SESGO  ·  se reevalúa en cada vela, no se fija en la apertura

Se mira H4 y H1.                                            (nº7, nº11)

    ¿el precio está interactuando con un FVG de H4 o de H1?

      SÍ · lo tapea y AGUANTA    -> REVERSIÓN, en la dirección del FVG
         · lo INVALIDA           -> CONTINUACIÓN, en dirección de la rotura
                                                                   (nº5)

      NO · manda la tendencia -> CONTINUACIÓN
           "no hay FVGs de los que estemos reaccionando en 4 horas, todo
            superbajista, aquí veo ventas de manual"                (nº8)

    El sesgo puede darse la vuelta a media sesión y eso es correcto:
    "no quedarte casado con el bias que tengas al principio".       (nº14)
    En días ambiguos se dejan armados los dos escenarios y se opera el
    que se complete primero.                                        (nº20)

## 3 · DOL  ·  el objetivo de liquidez

    Es el charco de liquidez más cercano en la dirección del sesgo.
    Candidatos: altos/bajos de Asia, de Londres, de la sesión de NY del
    día anterior, swings de H1 y de H4, FVGs de H1/H4 sin tapear.

    CONDICIÓN: tiene que estar SIN BARRER EN LOS DOS ÍNDICES.
    Un nivel ya tomado en uno deja de ser objetivo.           (nº8, nº16)

    Es dinámico: si el FVG de H4 que era el DOL se invalida, el DOL pasa
    al siguiente nivel.                                             (nº6)

## 4 · CONFLUENCIAS  ·  su lista, textual                          (nº16)

    1. tapeo de un FVG de M15 o de M5
    2. barrido de liquidez claro (niveles de sesión)
    3. Judas Swing: acumulación -> manipulación -> distribución
    4. LRL A FAVOR: liquidez acumulada en la dirección del trade
    5. LRL EN CONTRA ya barrida antes de entrar

    Estas valen en CUALQUIERA de los dos índices: si pasa en uno, cuenta
    para los dos, "porque van correlacionados".               (nº9, nº11)

    Judas Swing NO vale si no hubo acumulación previa, o si el gatillo
    cae en premarket (antes de las 9:30).                          (nº20)

## 5 · SMT  ·  divergencia entre los dos índices

    Un evento (barrido, tapeo) que ocurre en UN índice y no en el otro.
    NO es requisito: sube el setup de A a A+.                (nº12, nº16)
    Se mide por separado en el backtest.

## 6 · GATILLO  ·  en el activo que se opera, no en el otro       (nº18)

    Preferente: IFVG · invalidación de un fair value gap
        válida solo si la vela que rompe el FVG es del COLOR de la
        dirección buscada (alcista para compras).                   (nº19)
        Temporalidad: la mayor disponible cuyo R siga funcionando,
        entre 30s y M5.                            (nº10, nº11, nº12, nº17)

    Alternativo: CISD · cierre de CUERPO a través del CUERPO de la última
        manipulation leg. Se usa cuando no hay IFVG, o cuando el IFVG se
        invalida con poca fuerza.                              (nº5, nº10)

    No se entra en la reversión: se entra en la CONTINUACIÓN de la
    reversión. "prefiero ser de los que se enganchan a la ola".     (nº19)
    No se entra al primer IFVG: primero la confluencia de M15/M5.   (nº9)

## 7 · STOP

    Al extremo de la pierna de inducción.                           (nº9)
    Al CUERPO en vez de a la mecha si la mecha estropea el ratio.
                                                            (nº6, nº13, nº15)

## 8 · TAKE PROFIT

    El DOL, si cae entre 1:1 y 1:1,5. Si no, 1:1.            (nº14, nº15)

    Ese tope NO es de la estrategia: es la regla de consistencia de la
    empresa de fondeo. En cuenta ya fondeada alarga hasta 1:4.
                                                            (nº13, nº18)
    -> se miden las DOS variantes: TP a 1:1 y TP al DOL sin tope.

## 9 · BREAK EVEN

    Se mueve a BE cuando el OTRO índice barre el DOL.          (nº4, nº11)
    "si ya has tocado tu objetivo con uno de los dos activos, protégete o
     ciérralo, ya no tienes excusa para seguir dentro"
    Se coloca en un nivel de liquidez INTERNA.                     (nº10)
    Si no hay un nivel con sentido, NO se pone.               (nº11, nº14)

## 10 · LO QUE NO SE PUEDE PROGRAMAR

    LA BALANZA · pesar confluencias a favor y en contra sobre un conjunto
    abierto de factores. Él lo nombra así y lo describe como juicio:
    "nunca vas a encontrar el setup perfecto que no tenga nada en contra".
                                                            (nº12, nº15, nº20)

    SALTARSE SESIONES · a veces por criterio ("no me gustaba cómo se
    movía"), a veces por disponibilidad ("no me dio tiempo").  (nº9, nº20)

    El backtest medirá LA ESTRATEGIA SIN LA BALANZA. Hay que decirlo así.

## 11 · DECISIONES MÍAS que las transcripciones no fijan

Estas las tengo que elegir yo. Si alguna está mal, el resultado cambia.

    a. TENDENCIA cuando no hay FVG en juego: la definiré como la posición
       del cierre dentro del rango de las últimas 20 velas de H1.
    b. LRL: grupo de 3 o más extremos dentro de un margen estrecho.
    c. "MANIPULATION LEG" para el CISD: el último tramo direccional
       contrario antes del giro.
    d. DISTANCIA MÁXIMA al DOL: si el objetivo queda a más de 4R no se
       considera candidato.
    e. VIGENCIA de la confluencia: el tapeo de M15/M5 vale para disparar
       durante los 30 minutos siguientes.
    f. SESIONES: Asia 00:00-08:00, Londres 08:00-16:30, NY 14:30-21:00
       hora de Londres.

## 12 · Límites de los datos

    - Serie de ÍNDICE, no del futuro NQ mini de la CME.
    - Granularidad mínima 1 minuto: los gatillos de 30 segundos no se
      pueden reproducir.
    - Cobertura 2020-01 a 2026-07, ~1.650 días por ventana.
