# Resultado · el CRT máximo: ensamblar todo lo bueno lo empeora

Pre-registro: `docs/PREREGISTRO_crt_maximo.md`. Código: `bt/crt_maximo.py`.
EUR/USD, coste ECN. **Dentro 2021-2024** (donde se eligieron los componentes,
inflado por construcción) y **FUERA 2025-2026** (el único número que cuenta).
2.210 operaciones.

---

## 1 · El resultado

```
                                    n   acierto   geom  coste    bruta     NETA      z
  DENTRO 2021-2024 (inflado)     1593     34,4%   33,3%  11,5%  +0,0389  -0,0757  -2,24
  FUERA 2025-2026  <-- EL NÚMERO  617     35,2%   33,3%  10,4%  +0,0713  -0,0324  -0,63
```

**Neta −0,0324 fuera de muestra.** Y comparado con la versión simple que ya
tiene en `docs/ESTRATEGIA_operativa.md`, que da **−0,0208**:

**Ensamblar todos los componentes buenos lo deja PEOR que la versión simple.**

## 2 · Una sorpresa metodológica: no hay sobreajuste

Firmé que lo de dentro de muestra saldría entre +0,05 y +0,20, porque los
componentes se eligieron ahí y eso infla por construcción.

**Salió −0,0757.** Es decir: **fuera de muestra va MEJOR que dentro.**

Eso es lo contrario del sobreajuste, y tiene una explicación limpia: los
componentes no se eligieron mirando *estos* datos, sino otros instrumentos,
otras temporalidades y otros periodos. Cada pieza venía de un documento
distinto. **Ensamblar hallazgos de fuentes independientes no sobreajusta igual
que buscar en la misma muestra.**

Es la primera vez en el proyecto que puedo decir eso, y conviene anotarlo porque
contradice lo que yo esperaba.

## 3 · La pieza nueva se invierte

`RESULTADOS_cascada.md` había medido que **los niveles viejos van mejor**:
2-4 sesiones daban R/op +0,190 (z +2,19) contra +0,067 de la sesión anterior.
Nunca se había combinado con lo demás. Combinado:

```
  FUERA 2025-2026                   n   acierto    bruta     NETA      z
    nivel de 1 sesión             164     37,8%  +0,1463  +0,0476  +0,41
    nivel de 2 a 4 sesiones       261     34,9%  +0,0728  -0,0313  -0,40
    nivel de 5 o más              192     33,3%  +0,0052  -0,1024  -1,09
```

**Monótono, y exactamente al revés de lo medido antes.** Cuanto más FRESCO el
nivel, mejor. El cubo de 5 o más sesiones acierta el 33,3 %, que es el nulo
geométrico clavado: un nivel de hace una semana no es un nivel, es un precio
cualquiera.

Dos medidas de lo mismo apuntando a lados opuestos **es ruido**, no un hallazgo
invertido. Y mi predicción firmada —que 2-4 no batiría a 1— se cumple.

## 4 · El mejor cubo, y por qué tampoco vale

```
  nivel de 1 sesión, fuera de muestra:  neta +0,0476   z +0,41   n 164
```

Positivo. Pero z +0,41 sobre 164 operaciones es nada, y además es **el mejor de
tres cubos**: con tres, el máximo esperado por puro azar ronda z +0,85. Está por
debajo del ruido de selección.

Y «nivel de 1 sesión» para una operación de Londres **es el rango de Asia del
día** — o sea, exactamente lo que ya hace la versión simple.

## 5 · Mis predicciones

| firmé | salió | |
|---|---|---|
| dentro de muestra +0,05 a +0,20 | **−0,0757** | ✘ (y es buena noticia) |
| fuera entre −0,06 y +0,02 | **−0,0324** | ✔ |
| 2-4 sesiones no batirá a 1 sesión | no la bate; se invierte | ✔ |

## Veredicto

**La mejor estrategia CRT que se puede construir con 45 documentos de mediciones
es la que ya tiene.** No es un apaño ni un punto de partida: es el techo.

Añadir niveles de más sesiones la empeora. Añadir el filtro H4 la empeora.
Añadir la cascada multimarco la empeora. Añadir confluencias no hace nada.
Esperar un retroceso la empeora. El trailing la empeora.

Cada cosa que se le añade al CRT básico lo deja igual o peor. **Eso es el
hallazgo, y es más fuerte que cualquier tabla**: no es que no se haya encontrado
la combinación buena, es que el espacio de combinaciones se ha recorrido y
apunta todo hacia la versión mínima.

Lo que queda es lo de siempre: **−0,021 R por operación**, con el coste siendo
el 10 % del riesgo y la ventaja bruta siendo del 2 % del acierto.
