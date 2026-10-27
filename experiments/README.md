# Experimentos

Trabajo exploratorio relacionado con Atlas RF, traído desde cuadernos antiguos de Google Colab. **No forma parte del paquete `atlas_rf`**: no tiene pruebas automáticas y sus resultados no están validados.

## `antenas/antenas.ipynb`

Cuaderno de investigación sobre antenas de parche (antes `Copia de Antenas.ipynb`):

- Plegado de un parche de 5 × 6,3 mm modelado como grafo, con cinemática espacial.
- Varias iteraciones ("notas" y "sinfonías") de un diseño guiado por optimización evolutiva y aprendizaje automático.
- **Simulador FDTD** (diferencias finitas en el dominio del tiempo) que resuelve las ecuaciones de Maxwell en una banda de 2,4 GHz.
- **Validación IA vs. física**: la IA propone las medidas de un microstrip a 5 GHz y el FDTD comprueba el resultado.
- Una evaluación técnica del propio proyecto, con sus límites.

Se limpiaron los resultados guardados (de 22 MB a ~0,5 MB). Todas las cargas con `torch.load` usan `weights_only=True`: solo leen tensores y números, nunca código. Ábrelo en Colab con **Archivo → Abrir cuaderno → GitHub** → `SiriusMagic/atlas-rf`, y ejecuta cada sección por separado.

## `beam_scheduler/beam_scheduler.py`

Planificador de haces para un arreglo de antenas (antes `Copia de Untitled10.ipynb`). Compara un barrido fijo con uno "inteligente" que recuerda qué sectores tienen usuarios, y mide tiempo total, tiempo de descubrimiento (media y P95) e índice de equidad de Jain con 10, 50, 100 y 200 usuarios.

```bash
pip install numpy pandas matplotlib
python experiments/beam_scheduler/beam_scheduler.py
```

Guarda el gráfico comparativo en `beam_scheduler_resultados.png`. El cuaderno original tenía varias versiones del mismo programa; aquí está la última, que corrige el cálculo de métricas de la anterior (devolvía `NaN`).
