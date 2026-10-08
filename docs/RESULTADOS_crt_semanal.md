# Resultado · el filtro de dirección semanal en el CRT diario

Sale de una nota de voz de la comunidad de WhatsApp sobre CRT en rangos
diarios del NASDAQ. Código en `bt/crt_semanal.py`.

## Lo que afirma la nota

    "el precio se mueve utilizando los rangos"
    "esperas el rango a favor del objetivo y te sumas al movimiento"
    "si todo te marca alcista, nosotros buscamos una compra"

O sea: rango diario, objetivo en el extremo opuesto, y **filtro de dirección
superior**. La pregunta concreta es si ese filtro añade algo sobre el +0,042 R
bruto del CRT diario ya medido en `RESULTADOS_crt_temporalidad.md`.

## El resultado

Dirección semanal tomada de la semana **anterior ya cerrada**.

     instr           filtro     n   R BRUTA       z    R NETA       z
    NAS100            todas   556   -0,0424   -0,73   -0,0574   -0,99
    NAS100  semanal a favor   244   -0,1225   -1,38   -0,1380   -1,55
    NAS100 semanal en contra  309   +0,0302   +0,39   +0,0155   +0,20

    SPX500            todas   580   -0,0148   -0,25   -0,0430   -0,74
    SPX500  semanal a favor   255   -0,1062   -1,31   -0,1326   -1,64
    SPX500 semanal en contra  322   +0,0667   +0,80   +0,0371   +0,45

    EURUSD            todas   648   -0,0340   -0,60   -0,0909   -1,62
    EURUSD  semanal a favor   321   -0,0527   -0,65   -0,1068   -1,32
    EURUSD semanal en contra  324   -0,0066   -0,08   -0,0648   -0,82

**En los tres instrumentos, filtrar "a favor de la semana" EMPEORA el
resultado.** Y en NAS100 y SPX500 el subconjunto que va en contra es el único
con signo positivo.

## La lectura correcta

Ningún z pasa de |1,64|: todo está dentro del ruido. Así que la conclusión
**no** es "hay que operar contra la semana". Es:

**El filtro de dirección semanal no aporta información.**

Es el mismo patrón que el GannHiLo en la estrategia del oro: la pieza que
parece el análisis inteligente no hace nada, y sin ella el resultado es igual
o mejor.

## Contexto

La nota también afirma que "los rangos se completan" en todas las
temporalidades. **Esa parte sí está respaldada**: la ventaja bruta del CRT es
+0,082 R de media y homogénea entre marcos (Q = 7,75 con 6 gl).

Lo que la nota no dice es lo que decide: el coste pasa del 14,3 % del riesgo
en H1 al 2,3 % en D1, y la ventaja está decayendo — las seis temporalidades
bajan en 2024-2026 respecto a 2020-2023, prueba de signos p = 0,031.
