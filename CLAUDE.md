# atlas-rf

Laboratorio de RF y antenas en Python: estimación de parches microstrip y factores de arreglo (`src/atlas_rf/`), dashboard Streamlit y experimentos no validados en `experiments/`. No es un solver electromagnético de onda completa: no inventes métricas que el modelo no calcula.

## Comandos

```bash
pip install -r requirements.txt
pytest -q                                   # pruebas del modelo y de experiments/
streamlit run src/atlas_rf/dashboard.py     # dashboard
python -m src.atlas_rf --config config/default.json
```

## Reglas del dueño (aplican a todo cambio)

- **Librerías**: si una dependencia está abandonada, sin mantenimiento, obsoleta o tiene una alternativa claramente más actual o potente, reemplázala sin pedir permiso. Explica el cambio y el motivo en el PR.
- **Quitar lo que no se usa**: archivos y dependencias que ningún código importa se eliminan. Menos código = menos superficie de ataque.
- **Nunca subir secretos**: ni llaves de API, ni contraseñas, ni archivos `.env`. Usa variables de entorno y `.env.example`.
- **Todo por pull request** hacia `main`, con las pruebas en verde antes de fusionar.
- **Probar antes de subir**: ejecuta las pruebas del repo; si cambia la interfaz, pruébala en un navegador.
- **Idioma**: README, PRs y comentarios para el usuario en español, claros y sin jerga.
- **Dependabot**: las actualizaciones menores se fusionan solas si las pruebas pasan; las mayores se revisan a mano.
- **Cuadernos**: sin resultados guardados y con `torch.load(..., weights_only=True)`; la prueba `tests/test_experiments.py` lo verifica.
