# Una hoja

Todo lo demás del repositorio es el porqué. Esto es el qué.

---

## Antes de abrir el gráfico

```
  Instrumento:  EUR/USD          Gráfico:  M15          Hora:  Madrid
```

## 08:00 — marca el rango de Asia

```
  asiaH = el máximo más alto entre las 00:00 y las 08:00
  asiaL = el mínimo más bajo
```
No se vuelve a tocar en todo el día.

## 08:00 a 11:00 — la única ventana

Mira el cierre de cada vela de 15 minutos. Nada más.

```
  VENDER   si el máximo pasa de asiaH,  el cierre vuelve por debajo,
           y el mínimo NO toca asiaL

  COMPRAR  si el mínimo pasa de asiaL,  el cierre vuelve por encima,
           y el máximo NO toca asiaH
```

**Una vez de cada lado al día. La primera.**

## Al dispararse

```
  ENTRAS     en la apertura de la vela siguiente. A mercado.
  RIESGO     1,5 x ATR(14)
  STOP       entrada − riesgo   (compra)      entrada + riesgo   (venta)
  OBJETIVO   entrada + 2x riesgo               entrada − 2x riesgo
  LOTES      50 / (riesgo x 100.000)
  CIERRAS    a las 6 horas si no ha tocado ninguno
```

Sin trailing. Sin mover el stop. Sin esperar mejor precio.

## Las tres paradas

```
  3 operaciones hoy        ->  se acabó el día
  2 pérdidas seguidas      ->  cierras la plataforma
  -1,5 % en el día         ->  cierras la plataforma
```

## Y anotas, al abrir

```
  fecha · hora · lado · entrada · stop · objetivo · lotes · por qué
  resultado en R (al cerrar)
  las que viste y NO tomaste
```

---

## Lo único que tienes que recordar de todo lo demás

**No esperas ganar.** Esperas no reventar mientras la suerte decide: **35 % de pasar las dos fases, unos 3 meses.** La cuenta fue gratis, así que el peor caso es quedarte como estás.

**A las 100 operaciones anotadas** miramos si tu acierto pasa del **36,7 %**. Por debajo, no hay nada. Por encima, hablamos.
