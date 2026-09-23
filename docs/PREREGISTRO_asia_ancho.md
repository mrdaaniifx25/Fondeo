# Preregistro · el mismo filtro con stops anchos

Escrito el 28 de agosto de 2026, antes de ejecutar. Una sola pasada.

## La predicción, y de dónde sale

Con el filtro de contexto (M15 y H1 a favor) la ventaja bruta medida es de
**+0,082 R por operación** sobre 1.543 disparos, z +3,87 por día.

En un 1:2 con objetivo definido como 2 veces la distancia al stop, la
probabilidad geométrica es 1/3 **sea cual sea el tamaño del stop** (ruina del
jugador). Así que ensanchar el stop no debería cambiar el bruto en R, pero sí
diluye el coste, que se paga en pips:

```
  neta por operación = 0,082 - 1,43 / stop_en_pips
  cero en            stop = 1,43 / 0,082 = 17,4 pips
```

**Predicción firmada, principal:** con un stop mínimo de **20 pips** y el filtro
de contexto, la neta por día en 2020-2025 será **positiva**.

**Predicción secundaria:** el bruto en R se mantendrá cerca de +0,08. Si se
desploma al ensanchar, la ventaja no era estructural sino de horizonte corto.

## Especificación

Mismos disparos de `bt/asia_nivel.py`, filtrados por `favM15 & favH1`. No se
genera ninguna operación nueva ni se cambia el gatillo.

- **Stop**: `max(stop natural, stop mínimo)`. El stop natural es el extremo de la
  vela anterior, como siempre.
- **Objetivo**: 2 veces la distancia al stop, como siempre.
- **Horizonte principal**: hasta las 22:00 del mismo día, como en todo el
  proyecto. Se informa qué fracción queda sin resolver.
- **Horizonte secundario**: 3 días naturales. Es el segundo contraste.
- **Coste**: 1,43 pips.
- **Datos**: 2020-2025 principal; enero-mayo 2026 secundaria.
- **Unidad**: el día.

Barrido de stop mínimo: 0, 10, 15, 20, 25, 30 pips. El contraste firmado es
**sólo el de 20**; el resto es descripción de la curva.

## Lo que invalidaría la idea

Que el bruto en R caiga al ensanchar. Eso significaría que lo que mide el filtro
de contexto es un empujón de corto plazo que no aguanta un objetivo más lejano,
y entonces no hay forma de sacarlo del coste.
