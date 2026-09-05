# Resultados · el CRT en instrumentos ciegos

Pre-registro en `PREREGISTRO_h12_ciego.md`, escrito y subido **antes de que los
ficheros existieran**. Una sola pasada. XAUUSD y GRXEUR, 2023-2025, seis
instrumento-años, datos que no habían entrado nunca en este proyecto.

## El resultado, entero

| TF | n | acierto | R:R | riesgo | coste %R | **R bruta** | **R neta** | IC95 neta | z |
|---|---|---|---|---|---|---|---|---|---|
| H1 | 7.513 | 49,0 % | 1,24 | 91,3 | 11,9 % | **+0,089** | −0,110 | [−0,143, −0,076] | −6,36 |
| H2 | 3.621 | 45,8 % | 1,36 | 146,0 | 8,5 % | +0,054 | −0,086 | [−0,136, −0,037] | −3,41 |
| H4 | 1.815 | 49,3 % | 1,31 | 196,1 | 5,9 % | +0,109 | +0,020 | [−0,043, +0,083] | +0,61 |
| H8 | 902 | 46,3 % | 1,38 | 389,1 | 3,7 % | +0,005 | −0,063 | [−0,144, +0,018] | −1,52 |
| **H12** | **487** | 43,3 % | 1,49 | 550,0 | 3,3 % | **−0,003** | **−0,055** | **[−0,170, +0,061]** | **−0,93** |
| D1 | 291 | 50,2 % | 1,19 | 583,7 | 1,9 % | +0,066 | +0,040 | [−0,114, +0,195] | +0,51 |

**Criterio declarado: el IC95 de la neta de H12 excluye el cero por arriba.**
No lo excluye. **Según el pre-registro, el CRT se cierra aquí.**

## Las cinco predicciones

| | predicción | resultado |
|---|---|---|
| 1 | bruta de H12 entre +0,05 y +0,15 | **✘** −0,003 |
| 2 | coste de H12 por debajo del 4 % | ✔ 3,3 % |
| 3 | neta de H12 positiva | **✘** −0,055 |
| 4 | bruta plana entre H1 y D1 | ✔ Q = 6,36 con 5 gl |
| 5 | neta de H1 negativa en los dos | ✔ XAUUSD −0,105 · GRXEUR −0,115 |

# Lo que sí ha replicado, y es lo más valioso del día

**La ventaja bruta del CRT en H1, medida en dos instrumentos que este proyecto
no había visto nunca:**

```
cinco instrumentos originales, 2020-2026 :  +0,087
oro y DAX, 2023-2025, ciegos             :  +0,089   IC95 [+0,055, +0,122]   n = 7.513
```

Dos milésimas de diferencia. En un mercado distinto (metal), en un índice
europeo, en un periodo distinto, con los datos apartados hasta después de
escribir la predicción.

**El patrón del CRT existe.** Eso deja de ser una hipótesis. Barrer un extremo y
cerrar dentro sí anticipa un movimiento hacia el extremo opuesto, con una ventaja
de unas nueve centésimas de R por operación.

Y la aritmética del coste también replica: 11,9 % del riesgo en H1, 1,9 % en
diario, y la neta de H1 negativa en los dos instrumentos, sin excepción, que era
la predicción que más me jugaba.

# Por qué falla entonces, y un error mío en el diseño

La ventaja bruta es plana —Q de Cochran 6,36 con 5 grados de libertad, media
ponderada **+0,073 R**— y el coste en H12 es del 3,3 %. Si las dos cosas son
ciertas, la neta esperada en H12 sería de unos **+0,04 R**.

El error estándar de la celda H12 es **0,059**. Para que un efecto de +0,04
produzca un intervalo que excluya el cero hace falta un error estándar de 0,020,
o sea **nueve veces más datos**.

**La prueba que diseñé no podía salir bien aunque la hipótesis fuera cierta.**
Calculé la potencia suponiendo un efecto de +0,10 cuando la mejor estimación
disponible era +0,073, y sobre el neto, no sobre el bruto. Es un fallo de diseño
mío, y hay que decirlo antes que ninguna otra cosa sobre este resultado.

Lo que **no** voy a hacer es usarlo para rescatar la hipótesis. El criterio
estaba escrito, no se cumple, y cambiarlo ahora convertiría seis semanas de
método en otra sesión de buscar hasta encontrar.

## Cuántos datos harían falta de verdad

```
efecto neto esperado en H12          +0,04 R
desviación típica                     ~1,3
n para un IC95 que excluya el cero    ~4.200 operaciones
operaciones por instrumento-año       ~81
                                     ─────────────────
                                      52 instrumento-años
```

Nueve instrumentos con seis años cada uno. Y aunque se consiguieran y saliera
positivo, +0,04 R por operación con 81 operaciones al año son **3,2 R al año por
instrumento**. Para un objetivo de fondeo del 8-10 % arriesgando un 1 % por
operación harían falta tres instrumentos y que ninguno flojee.

# Las celdas secundarias, para que consten

Ninguna se acerca al umbral de Bonferroni |z| > 3,2 que estaba declarado:

| | neta | z | |
|---|---|---|---|
| H4 · XAUUSD | +0,037 | +0,85 | no pasa |
| D1 · GRXEUR | +0,084 | +0,81 | no pasa |
| D1 · XAUUSD | +0,000 | +0,00 | no pasa |

El único sitio donde el coste-cero supera al coste pagado con holgura es **H4 en
oro**: necesitaría 49,66 unidades y se pagan 35. Queda anotado como observación,
no como hallazgo: es una celda de doce, con z +0,85.

# Qué queda cerrado y qué no

**Cerrado.** El CRT como estrategia mecánica operable con costes de retail. Se
han probado: la especificación completa de bctrades, cuatro temporalidades de
ejecución, la regla del reinicio, las confluencias, los horarios, la liquidez
múltiple, el barrido por temporalidad, y ahora el mecanismo del coste en
instrumentos ciegos con predicción escrita de antemano.

**No cerrado.** Que el patrón exista: existe, y está replicado. Lo que no hay es
forma de cobrarlo con un spread de retail y un stop de ese tamaño.

**Y sigue sin tocarse** lo único que este tipo de prueba no puede contestar: las
300 etiquetas a ciegas. Si tu criterio al mirar el gráfico separa las buenas de
las malas por encima de la mecánica, eso no aparece en ninguna de estas tablas.

**Reservado y sin mirar:** XAUUSD y GRXEUR de enero a julio de 2026, catorce
ficheros en `reservado/`.
