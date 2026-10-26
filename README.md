# Atlas RF v2 — laboratorio de RF y antenas

Prototipo científico reproducible para estudiar estimaciones iniciales de parches microstrip y factores de arreglo, con dashboard interactivo, barrido exploratorio de espaciado, registro JSON y exportación de geometría conceptual.

## Inicio rápido

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
streamlit run src/atlas_rf/dashboard.py
```

Para ejecutar pruebas:

```bash
pytest -q
```

Para generar gráficos ilustrativos desde la configuración:

```bash
python -m src.atlas_rf --config config/default.json
```

## Estructura

- `src/atlas_rf/model.py`: estimación de parche, factor de arreglo y barrido de espaciado.
- `src/atlas_rf/dashboard.py`: dashboard Streamlit.
- `src/atlas_rf/export_geometry.py`: exportación JSON y STL conceptual.
- `src/atlas_rf/plots.py`: gráficos ilustrativos.
- `config/default.json`: parámetros y perfiles iniciales.
- `docs/EQUATIONS.md`: ecuaciones y límites.
- `docs/VALIDATION_PLAN.md`: plan de validación.
- `tests/test_model.py`: pruebas unitarias.

## Límites científicos

Este proyecto **no es un solver electromagnético de onda completa**. No calcula S11, impedancia real, ganancia realizada, eficiencia, acoplamiento mutuo, red de alimentación ni campos electromagnéticos medidos. Las métricas no disponibles se dejan como `null`; no se inventan valores.

Las dimensiones del parche son estimaciones de primer orden. El STL es una envolvente conceptual, no un diseño validado para fabricar. La compatibilidad con Starlink no está demostrada: confirma el modelo exacto del terminal, las bandas, la polarización y la normativa local antes de cualquier diseño físico. No transmitas sin un sistema RF completo, validación y autorización aplicable.

## Ruta de validación

1. Verificar las estimaciones analíticas y las pruebas.
2. Validar un elemento con un solver electromagnético full-wave y/o un VNA.
3. Modelar alimentación, pérdidas, polarización y acoplamiento mutuo.
4. Comparar simulaciones con mediciones documentadas.
5. Entrenar un modelo sustituto solo con datos de solver o mediciones trazables; este repositorio no contiene un modelo ML entrenado.

## Licencia

Copyright 2026 SiriusMagic

Este proyecto se distribuye bajo la **Licencia Apache 2.0**. Consulta el archivo [`LICENSE`](./LICENSE) para ver el texto completo.

En resumen: cualquiera puede usar, copiar, modificar y distribuir este código, siempre que conserve el aviso de copyright y la licencia. El software se entrega **"tal cual", sin garantías de ningún tipo**, y los autores no se hacen responsables de daños derivados de su uso.

## Seguridad

¿Encontraste una vulnerabilidad? Lee [`SECURITY.md`](./SECURITY.md) y repórtala de forma privada.
