# Plan de validación

## Etapa 0 — Definición
- Confirmar frecuencia exacta y ancho de banda requerido.
- Confirmar variante de RO4350B, espesor disponible, cobre, tolerancias y fabricante.
- Definir con claridad el eje frontal +Y y los ángulos usados para front-to-back.
- Para el caso Starlink, identificar terminal/modelo, banda autorizada y objetivo funcional. No asumir que 5 GHz es compatible.

## Etapa 1 — Validación analítica
- Ejecutar `pytest`.
- Comparar cálculos de longitud de onda y dimensiones con una referencia independiente de diseño de antenas.
- Hacer un análisis de sensibilidad frente a permitividad, espesor y frecuencia.

## Etapa 2 — Solucionador electromagnético
- Construir la geometría exacta incluyendo plano de tierra, puerto y caja de radiación.
- Ejecutar un barrido de frecuencia alrededor de la resonancia.
- Exportar S11, VSWR, ganancia realizada, eficiencia, patrón 3D y corrientes superficiales.
- Refinar malla hasta que los resultados relevantes converjan.

## Etapa 3 — Fabricación y medición
- Fabricar solo tras revisión del diseño y reglas eléctricas/mecánicas.
- Medir S11 con analizador de redes vectorial (VNA) calibrado.
- Registrar fixture, plano de calibración, cables, conectores y condiciones ambientales.
- Medir patrón de radiación en un entorno adecuado; no inferirlo solo de una medición de potencia recibida informal.
- Comparar medición y simulación con incertidumbre explícita.

## Etapa 4 — Optimización
- Empezar con búsqueda de parámetros y un diseño base reproducible.
- Usar optimización bayesiana o algoritmos evolutivos solo si cada evaluación viene de un modelo validado.
- Objetivo multiobjetivo posible: maximizar ganancia frontal y eficiencia, minimizar potencia trasera y lóbulos laterales, mantener S11 bajo el límite y respetar dimensiones fabricables.
- Mantener límites geométricos, espaciado, reglas de fabricación y semillas aleatorias registradas.
- Reservar diseños de validación que no se usen durante el ajuste para evitar sobreajuste del modelo.

## Criterios de aceptación propuestos
- Error numérico de pruebas unitarias: dentro de tolerancias definidas por prueba.
- Convergencia EM: cambios pequeños y documentados entre refinamientos de malla.
- Concordancia medición-simulación: umbrales definidos antes de medir; informar error y condiciones.
- No declarar compatibilidad con un sistema comercial hasta verificar banda, polarización, patrón, enlace y restricciones regulatorias.
