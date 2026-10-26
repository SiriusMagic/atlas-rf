"""Mobile-friendly Streamlit dashboard for Atlas RF (analytical prototype)."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from atlas_rf.model import C0_M_S, estimate_patch, array_factor, evaluate_design, spacing_sweep
from atlas_rf.export_geometry import geometry_spec, export_json, export_stl

st.set_page_config(page_title="Atlas RF", page_icon="📡", layout="wide")
st.title("Atlas RF")
st.caption("Laboratorio de antenas · prototipo analítico · no equivale a simulación electromagnética")
st.warning("No calcula S11, ganancia realizada, eficiencia, acoplamiento mutuo ni campos reales. Los gráficos muestran factores de arreglo analíticos.")

with st.sidebar:
    st.header("Parámetros")
    profile = st.selectbox("Perfil", ["Starlink Ku RX (referencia)", "Starlink Ku TX (referencia)", "Wi-Fi 5", "Wi-Fi 6E", "Personalizado"])
    preset = {"Starlink Ku RX (referencia)":11.7, "Starlink Ku TX (referencia)":14.25, "Wi-Fi 5":5.5, "Wi-Fi 6E":6.5}
    freq_ghz = preset[profile] if profile in preset else st.number_input("Frecuencia (GHz)", min_value=0.1, max_value=100.0, value=11.7, step=0.1)
    if profile in preset:
        st.info(f"Frecuencia de referencia: {freq_ghz:.3f} GHz")
    rows = st.slider("Filas", 1, 8, 4)
    cols = st.slider("Columnas", 1, 8, 4)
    spacing_lambda = st.slider("Separación entre centros (λ)", 0.20, 0.80, 0.50, 0.01)
    eps_r = st.number_input("Permitividad relativa εr", min_value=1.1, max_value=20.0, value=3.48, step=0.01)
    substrate_mm = st.number_input("Espesor sustrato (mm)", min_value=0.05, max_value=5.0, value=0.762, step=0.01)
    copper_um = st.number_input("Espesor cobre (µm)", min_value=5.0, max_value=200.0, value=35.0, step=5.0)

freq_hz = freq_ghz * 1e9
wavelength = C0_M_S / freq_hz
spacing_m = spacing_lambda * wavelength
try:
    patch = estimate_patch(freq_hz, eps_r, substrate_mm/1000)
    metrics = evaluate_design(rows, cols, freq_hz, spacing_m, spacing_m)
    spec = geometry_spec(freq_hz, eps_r, substrate_mm/1000, copper_um*1e-6, rows, cols, spacing_m)
except ValueError as exc:
    st.error(f"Parámetros no válidos: {exc}")
    st.stop()

st.subheader("Resumen")
a,b,c = st.columns(3)
a.metric("Nivel", "Estimación analítica")
b.metric("Elementos", rows*cols)
c.metric("Longitud de onda", f"{wavelength*1000:.2f} mm")
a,b,c,d = st.columns(4)
a.metric("Ancho parche estimado", f"{patch.width_m*1000:.2f} mm")
b.metric("Largo parche estimado", f"{patch.length_m*1000:.2f} mm")
c.metric("ε efectiva estimada", f"{patch.effective_permittivity:.3f}")
d.metric("Separación", f"{spacing_m*1000:.2f} mm")
st.caption("Estimaciones de primer orden; no incluyen optimización de alimentación, pérdidas, tolerancias ni validación de fabricación.")

st.subheader("Factor de arreglo — hemisferio frontal")
theta_deg = np.linspace(0,90,181)
phi_deg = np.linspace(-180,180,361)
th,ph = np.meshgrid(np.radians(theta_deg),np.radians(phi_deg),indexing="ij")
af = array_factor(rows,cols,freq_hz,spacing_m,spacing_m,th,ph)
power_db = 10*np.log10(np.maximum(af**2,1e-6))
left,right = st.columns([1.3,1])
with left:
    fig,ax = plt.subplots(figsize=(8,4.4))
    im = ax.imshow(power_db,origin="lower",aspect="auto",extent=[-180,180,0,90],cmap="magma",vmin=-40,vmax=0)
    ax.set_xlabel("Azimut φ (grados)"); ax.set_ylabel("θ desde +Y (grados)")
    ax.set_title("Mapa angular del factor de arreglo"); fig.colorbar(im,ax=ax,label="Potencia normalizada (dB)")
    fig.tight_layout(); st.pyplot(fig,width="stretch"); plt.close(fig)
with right:
    cut = array_factor(rows,cols,freq_hz,spacing_m,spacing_m,np.radians(theta_deg),np.zeros_like(theta_deg))
    fig2,ax2 = plt.subplots(figsize=(6,4.4))
    ax2.plot(theta_deg,10*np.log10(np.maximum(cut**2,1e-6)))
    ax2.set_xlabel("θ desde +Y (grados)"); ax2.set_ylabel("Potencia normalizada (dB)")
    ax2.set_title("Corte principal φ = 0°"); ax2.set_ylim(-45,1); ax2.grid(True,alpha=.3)
    fig2.tight_layout(); st.pyplot(fig2,width="stretch"); plt.close(fig2)
st.info("El patrón de elemento, el plano de masa y el acoplamiento no están modelados. No interpretes estas figuras como patrón completo de antena.")

st.subheader("Métricas no disponibles")
x,y,z = st.columns(3)
x.metric("S11", "No calculado"); y.metric("Ganancia realizada", "No calculada"); z.metric("F/B", "No calculado")
st.subheader("Barrido exploratorio de espaciado")
if cols >= 2:
    candidates = spacing_sweep(rows,cols,freq_hz)
    st.dataframe(candidates, width="stretch")
else:
    st.caption("Se requieren al menos dos columnas para calcular el barrido lateral.")

record = {"timestamp_utc":datetime.now(timezone.utc).isoformat(),"profile":profile,"frequency_hz":freq_hz,
    "rows":rows,"columns":cols,"elements":rows*cols,"spacing_lambda":spacing_lambda,"spacing_m":spacing_m,
    "substrate_eps_r_nominal":eps_r,"substrate_thickness_m":substrate_mm/1000,"copper_thickness_m":copper_um*1e-6,
    "patch_width_estimate_m":patch.width_m,"patch_length_estimate_m":patch.length_m,
    "status":"ANALYTICAL_ESTIMATE_NOT_FULL_WAVE_VALIDATED","s11_db":None,"realized_gain_dbi":None,
    "efficiency_percent":None,"front_to_back_db":None}
st.subheader("Exportación")
st.download_button("Descargar registro JSON",json.dumps(record,indent=2),file_name="atlas_rf_experiment.json",mime="application/json")
st.download_button("Descargar geometría paramétrica JSON",json.dumps(spec,indent=2),file_name="atlas_rf_geometry.json",mime="application/json")
try:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        st.caption("El STL es una envolvente geométrica conceptual, no un diseño listo para fabricar.")
        st.download_button("Descargar STL conceptual", export_stl(spec,Path(td)/"atlas_rf_concept.stl").read_bytes(),
            file_name="atlas_rf_concept.stl",mime="model/stl")
except Exception as exc:
    st.caption(f"Exportación STL no disponible en este entorno: {exc}")
