# El concurso de 400 traders

Vídeo aportado por el usuario. No vende una estrategia: vende **un concurso
ganado**. Código: `bt/concurso.py`.

## Los datos son suyos

> *«más de 400 traders»* · *«20 días»* · *«Bitcoin subió un máximo de 6,25 % y
> terminó cerrando sólo un 0,20 % abajo»* · *«el primero, 186,27 %»* ·
> *«la segunda, 61,49 %»* · *«siete de los diez primeros han usado las
> estrategias que yo utilizo»*

Bitcoin **plano** durante los veinte días. Eso es lo que hace la cuenta posible.

## Qué produce un concurso así con ventaja EXACTAMENTE CERO

400 traders, 20 días, mercado plano, volatilidad diaria del 2,5 %, cada uno con
el apalancamiento que elija. 4.000 concursos simulados:

```
  apalanc.          1º          2º         10º     mediana   arruinados
       1x      +38,3 %     +33,6 %     +23,9 %      -0,6 %          0 %
       2x      +85,4 %     +72,1 %     +48,9 %      -2,3 %          0 %
       3x     +154,0 %    +128,9 %     +83,0 %      -5,2 %          0 %
       5x     +345,7 %    +272,4 %    +157,8 %     -14,0 %          0 %
      10x   +1.410,4 %    +956,8 %    +404,1 %     -47,8 %         13 %
      20x  +10.141,8 %  +4.552,8 %    +828,2 %    -100,0 %         73 %
```

**Anunciado: 1º +186,3 %, 2ª +61,5 %.**
**Con 3× de apalancamiento y ventaja cero: 1º +154 %, 2º +129 %.**

Los resultados que se publicitan **caben de sobra dentro de lo que produce el
azar** en un concurso de ese tamaño. Ni siquiera hacen falta apalancamientos
extremos: con 3× ya salen.

Y fíjese en la columna de la mediana: **−5,2 %**. El participante típico pierde.
Ésa es la columna que no se publica, igual que en `RESULTADOS_payouts.md`.

## «Siete de los diez primeros usaban mis estrategias»

```
  si eran el 30 % de los 400  ->  3,0 esperados en el top 10
  si eran el 50 %             ->  5,0
  si eran el 70 %             ->  7,0
  si eran el 80 %             ->  8,0
```

El concurso lo organiza él, en sus canales de Telegram, con sus premios y sus
mentorías. **El vídeo no dice qué fracción de los 400 eran alumnos suyos.** Sin
ese dato, «siete de diez» no distingue nada: si eran el 70 %, siete es
exactamente la media.

Es el mismo mecanismo de `RESULTADOS_payouts.md`: el número que se publica no es
falso, simplemente no separa la habilidad de la proporción.

## Lo que esto no dice

- **No dice que mienta.** Los números pueden ser exactos y aun así no demostrar
  ventaja. Son cosas distintas.
- **No dice que la estrategia no funcione.** Dice que *este concurso* no lo
  demuestra. Para eso habría que medirla, y la estrategia del vídeo —soporte en
  diario, giro, máximos crecientes en H4, patrón hasta Fibonacci 0,5-0,75 en H1,
  cambio de tendencia y ruptura de EMA50 en M5— es de la misma familia de
  confluencia multimarco que ya está medida en
  `RESULTADOS_techo_filtro.md` y `RESULTADOS_espacio.md`.

## Lo que sí demostraría algo

Un concurso no. Lo que separa habilidad de suerte es lo de siempre: **muchas
operaciones, publicadas antes de conocerse el resultado.** Con el 186 % de una
persona en veinte días no se puede distinguir nada — y con la mediana en −5,2 %,
tampoco hace falta.
