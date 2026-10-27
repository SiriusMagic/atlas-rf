"""Planificador de haces para un arreglo de antenas (experimento).

Simula un arreglo lineal que barre haces sobre usuarios distribuidos en el área
y compara dos algoritmos: barrido fijo y barrido "inteligente" con memoria por
sector. Mide tiempo total, tiempo de descubrimiento (media y P95) e índice de
equidad de Jain para 10, 50, 100 y 200 usuarios.

Origen: cuaderno "Copia de Untitled10" (última versión, que corrige el cálculo
de métricas de la anterior).

Uso:
    pip install numpy pandas matplotlib
    python experiments/beam_scheduler/beam_scheduler.py

Es un modelo simplificado y no validado: no forma parte del paquete atlas_rf.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. MODELO DE ARRAY Y FÍSICA (array_model.py)
# ==========================================
def calculate_wavelength(frequency_hz):
    c = 3e8
    return c / frequency_hz

def array_factor(theta_deg, N, wavelength, d, beta_deg):
    k = 2 * np.pi / wavelength
    theta_rad = np.radians(theta_deg)
    beta = np.radians(beta_deg)

    term = k * d * np.sin(theta_rad) + beta
    AF = np.zeros_like(theta_rad, dtype=complex)
    for n in range(N):
        AF += np.exp(1j * n * term)

    AF_mag = np.abs(AF) / N
    AF_db = 20 * np.log10(np.maximum(AF_mag, 1e-5))
    return AF_db

# ==========================================
# 2. GENERACIÓN DE USUARIOS RIGUROSA (users.py)
# ==========================================
def generate_manual_test_users():
    """Genera los 5 usuarios estrictos para la prueba de fuego obligatoria."""
    return [
        {
            'id': 0, 'x': -38.3, 'y': 32.1, 'height': 1.5, 'distance': 50.0,
            'angle': -50.0, 'traffic_demand': 500, 'priority': 50,
            'discovered': False, 'creation_time': 0.0, 'discovery_time': None,
            'first_service_time': None, 'completion_time': None,
            'remaining_data': 500, 'service_received': 0
        },
        {
            'id': 1, 'x': -8.7, 'y': 49.2, 'height': 1.5, 'distance': 50.0,
            'angle': -10.0, 'traffic_demand': 1000, 'priority': 80,
            'discovered': False, 'creation_time': 0.0, 'discovery_time': None,
            'first_service_time': None, 'completion_time': None,
            'remaining_data': 1000, 'service_received': 0
        },
        {
            'id': 2, 'x': 8.7, 'y': 49.2, 'height': 1.5, 'distance': 50.0,
            'angle': 10.0, 'traffic_demand': 200, 'priority': 20,
            'discovered': False, 'creation_time': 0.0, 'discovery_time': None,
            'first_service_time': None, 'completion_time': None,
            'remaining_data': 200, 'service_received': 0
        },
        {
            'id': 3, 'x': 25.0, 'y': 43.3, 'height': 1.5, 'distance': 50.0,
            'angle': 30.0, 'traffic_demand': 1500, 'priority': 90,
            'discovered': False, 'creation_time': 0.0, 'discovery_time': None,
            'first_service_time': None, 'completion_time': None,
            'remaining_data': 1500, 'service_received': 0
        },
        {
            'id': 4, 'x': 38.3, 'y': 32.1, 'height': 1.5, 'distance': 50.0,
            'angle': 50.0, 'traffic_demand': 400, 'priority': 40,
            'discovered': False, 'creation_time': 0.0, 'discovery_time': None,
            'first_service_time': None, 'completion_time': None,
            'remaining_data': 400, 'service_received': 0
        }
    ]

def generate_users(n_users, area_min_dist=10.0, area_max_dist=100.0, seed=42):
    """Genera población de usuarios con idéntica semilla y distribución dentro del sector de haz (-60° a +60°)."""
    np.random.seed(seed)
    users = []
    for i in range(n_users):
        r = np.random.uniform(area_min_dist, area_max_dist)
        angle_deg = np.random.uniform(-60.0, 60.0)
        angle_rad = np.radians(angle_deg)

        x = r * np.sin(angle_rad)
        y = r * np.cos(angle_rad)

        demand = int(np.random.randint(200, 1500))

        users.append({
            'id': i,
            'x': float(x),
            'y': float(y),
            'height': 1.5,
            'distance': float(r),
            'angle': float(angle_deg),
            'traffic_demand': demand,
            'priority': int(np.random.randint(10, 100)),
            'discovered': False,
            'creation_time': 0.0,
            'discovery_time': None,
            'first_service_time': None,
            'completion_time': None,
            'remaining_data': demand,
            'service_received': 0
        })
    return users

# ==========================================
# 3. MOTOR DE SIMULACIÓN Y SCHEDULING (scanner.py)
# ==========================================
def run_simulation(users, beam_angles, algorithm='fixed', beamwidth=10.0,
                   scan_time_ms=2.0, trans_time_ms=5.0, max_timeout_ms=100000.0, debug=False):
    """
    Ejecuta la simulación temporal paso a paso separando exploración, descubrimiento,
    servicio parcial y completitud.
    """
    sim_users = [u.copy() for u in users]
    current_time_ms = 0.0

    sector_memory = {
        angle: {
            'detected_users': [],
            'pending_traffic': 0.0,
            'priority_sum': 0.0,
            'waiting_time': 0.0,
            'last_scan_time': -1.0
        } for angle in beam_angles
    }

    fixed_order = list(beam_angles)
    active_route = list(fixed_order)
    sweeps_completed = 0
    timeout_reached = False

    if debug:
        print(f"\n--- INICIANDO SIMULACIÓN [{algorithm.upper()}] (Total Usuarios: {len(sim_users)}) ---")

    while not all(u['completion_time'] is not None for u in sim_users):
        if current_time_ms >= max_timeout_ms:
            timeout_reached = True
            if debug:
                print(f"[!] TIMEOUT ALCANZADO EN t={current_time_ms} ms")
            break

        if algorithm == 'intelligent':
            if sweeps_completed < 1:
                active_route = list(fixed_order)
            else:
                scored_angles = []
                for angle in beam_angles:
                    mem = sector_memory[angle]
                    time_since_last = current_time_ms - mem['last_scan_time']

                    w1, w2, w3, w4 = 1.0, 1.5, 0.5, 1.0
                    score = (w1 * len(mem['detected_users'])) + \
                            (w2 * (mem['pending_traffic'] / 1000.0)) + \
                            (w3 * (time_since_last / 10.0)) + \
                            (w4 * (mem['priority_sum'] / 100.0))

                    scored_angles.append((score, angle))

                scored_angles.sort(key=lambda x: x[0], reverse=True)
                active_route = [angle for _, angle in scored_angles]
        else:
            active_route = list(fixed_order)

        for beam_angle in active_route:
            current_time_ms += scan_time_ms
            sector_memory[beam_angle]['last_scan_time'] = current_time_ms

            detected_in_this_step = []
            active_sector_users = []

            for u in sim_users:
                if abs(u['angle'] - beam_angle) <= (beamwidth / 2.0):
                    active_sector_users.append(u)
                    detected_in_this_step.append(f"U{u['id']}")

                    if not u['discovered']:
                        u['discovered'] = True
                        u['discovery_time'] = current_time_ms
                        if debug and len(sim_users) <= 10:
                            print(f"t={current_time_ms:5.1f} ms | U{u['id']} DESCUBIERTO (Ángulo: {u['angle']}°) térmico")

            pending_traffic_sec = sum(u['remaining_data'] for u in active_sector_users if u['completion_time'] is None)
            priority_sum_sec = sum(u['priority'] for u in active_sector_users if u['completion_time'] is None)

            sector_memory[beam_angle]['detected_users'] = [u['id'] for u in active_sector_users if u['completion_time'] is None]
            sector_memory[beam_angle]['pending_traffic'] = pending_traffic_sec
            sector_memory[beam_angle]['priority_sum'] = priority_sum_sec

            unserved_in_sector = [u for u in active_sector_users if u['completion_time'] is None]
            if unserved_in_sector:
                unserved_in_sector.sort(key=lambda x: (x['priority'], x['remaining_data']), reverse=True)
                target_user = unserved_in_sector[0]

                current_time_ms += trans_time_ms

                if target_user['first_service_time'] is None:
                    target_user['first_service_time'] = current_time_ms

                served_chunk = min(300, target_user['remaining_data'])
                target_user['remaining_data'] -= served_chunk
                target_user['service_received'] += served_chunk

                if target_user['remaining_data'] <= 0:
                    target_user['completion_time'] = current_time_ms
                    if debug and len(sim_users) <= 10:
                        print(f"t={current_time_ms:5.1f} ms | U{target_user['id']} COMPLETAMENTE SERVIDO")

            if debug and len(sim_users) <= 10 and detected_in_this_step:
                print(f"t={current_time_ms:5.1f} ms | Beam={beam_angle:3d}° | Detectados: {detected_in_this_step}")

            if all(u['completion_time'] is not None for u in sim_users):
                break

        sweeps_completed += 1

    return sim_users, current_time_ms, timeout_reached

# ==========================================
# 4. CÁLCULO DE MÉTRICAS Y JAIN FAIRNESS (metrics.py)
# ==========================================
def calculate_jains_fairness(users):
    services = np.array([u['service_received'] for u in users], dtype=float)
    n = len(services)
    if n == 0 or np.sum(services) == 0:
        return "N/A"
    sum_val = np.sum(services)
    sum_sq = np.sum(services**2)
    if sum_sq == 0:
        return "N/A"
    return float((sum_val**2) / (n * sum_sq))

def evaluate_performance(sim_users, total_time, timeout_reached):
    disc_times = [u['discovery_time'] - u['creation_time'] for u in sim_users if u['discovery_time'] is not None]
    first_serv_times = [u['first_service_time'] - u['creation_time'] for u in sim_users if u['first_service_time'] is not None]
    comp_times = [u['completion_time'] - u['creation_time'] for u in sim_users if u['completion_time'] is not None]

    total_bits_served = sum(u['service_received'] for u in sim_users)
    throughput = total_bits_served / (total_time / 1000.0) if total_time > 0 else 0.0

    metrics = {
        'total_time_ms': total_time,
        'timeout': timeout_reached,
        'users_completed': f"{len(comp_times)}/{len(sim_users)}",
        'discovery_mean': np.mean(disc_times) if disc_times else float('nan'),
        'discovery_median': np.median(disc_times) if disc_times else float('nan'),
        'discovery_p95': np.percentile(disc_times, 95) if len(disc_times) > 1 else (disc_times[0] if disc_times else float('nan')),
        'first_service_mean': np.mean(first_serv_times) if first_serv_times else float('nan'),
        'completion_mean': np.mean(comp_times) if comp_times else float('nan'),
        'throughput': throughput,
        'fairness_index': calculate_jains_fairness(sim_users)
    }
    return metrics

# ==========================================
# 5. VISUALIZACIÓN ANALÍTICA (visualization.py)
# ==========================================
def plot_comparative_metrics(df_results):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].plot(df_results['Usuarios'], df_results['Fixed Total (ms)'], marker='o', label='Fixed', color='royalblue')
    axes[0, 0].plot(df_results['Usuarios'], df_results['Intelligent Total (ms)'], marker='s', label='Intelligent', color='darkorange')
    axes[0, 0].set_title('Tiempo Total de Simulación vs Carga de Usuarios')
    axes[0, 0].set_xlabel('Número de Usuarios')
    axes[0, 0].set_ylabel('Tiempo Total (ms)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, linestyle='--', alpha=0.7)

    axes[0, 1].plot(df_results['Usuarios'], df_results['Fixed Disc Mean'], marker='o', label='Fixed', color='royalblue')
    axes[0, 1].plot(df_results['Usuarios'], df_results['Intelligent Disc Mean'], marker='s', label='Intelligent', color='darkorange')
    axes[0, 1].set_title('Tiempo Medio de Descubrimiento vs Usuarios')
    axes[0, 1].set_xlabel('Número de Usuarios')
    axes[0, 1].set_ylabel('Discovery Mean (ms)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, linestyle='--', alpha=0.7)

    axes[1, 0].plot(df_results['Usuarios'], df_results['Fixed P95'], marker='o', label='Fixed', color='royalblue')
    axes[1, 0].plot(df_results['Usuarios'], df_results['Intelligent P95'], marker='s', label='Intelligent', color='darkorange')
    axes[1, 0].set_title('Percentil 95 de Descubrimiento vs Usuarios')
    axes[1, 0].set_xlabel('Número de Usuarios')
    axes[1, 0].set_ylabel('Discovery P95 (ms)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle='--', alpha=0.7)

    fair_fixed = pd.to_numeric(df_results['Fixed Fairness'].replace('N/A', np.nan))
    fair_intel = pd.to_numeric(df_results['Intelligent Fairness'].replace('N/A', np.nan))
    axes[1, 1].plot(df_results['Usuarios'], fair_fixed, marker='o', label='Fixed', color='royalblue')
    axes[1, 1].plot(df_results['Usuarios'], fair_intel, marker='s', label='Intelligent', color='darkorange')
    axes[1, 1].set_title('Índice de Jain Fairness vs Usuarios')
    axes[1, 1].set_xlabel('Número de Usuarios')
    axes[1, 1].set_ylabel('Jain Fairness Index')
    axes[1, 1].set_ylim(0, 1.05)
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig("beam_scheduler_resultados.png", dpi=120)
    print("[+] Gráfico guardado en beam_scheduler_resultados.png")
    plt.show()

# ==========================================
# 6. EJECUCIÓN PRINCIPAL Y VALIDACIÓN PASO A PASO
# ==========================================
if __name__ == "__main__":
    beam_angles = [-60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60]

    print("==================================================")
    print("PASO 1: PRUEBA DE FUEGO OBLIGATORIA (5 USUARIOS)")
    print("==================================================")

    test_users_fixed = generate_manual_test_users()
    test_users_intel = [u.copy() for u in test_users_fixed]

    res_f, time_f, timeout_f = run_simulation(test_users_fixed, beam_angles, algorithm='fixed', debug=True)
    res_i, time_i, timeout_i = run_simulation(test_users_intel, beam_angles, algorithm='intelligent', debug=True)

    print(f"\n[✔] Resultado 5 Usuarios -> Fijo: {time_f} ms | Inteligente: {time_i} ms\n")

    print("==================================================")
    print("PASO 2: VALIDACIÓN INTERMEDIA (10 USUARIOS TRACE)")
    print("==================================================")
    users_10_base = generate_users(n_users=10, seed=42)
    u10_f = [u.copy() for u in users_10_base]
    u10_i = [u.copy() for u in users_10_base]

    res10_f, t10_f, _ = run_simulation(u10_f, beam_angles, algorithm='fixed', debug=False)
    res10_i, t10_i, _ = run_simulation(u10_i, beam_angles, algorithm='intelligent', debug=False)
    m10_f = evaluate_performance(res10_f, t10_f, False)
    m10_i = evaluate_performance(res10_i, t10_i, False)
    print(f"10 Usuarios -> Fijo Total: {t10_f} ms (Disc Mean: {m10_f['discovery_mean']:.1f} ms) | Inteligente Total: {t10_i} ms (Disc Mean: {m10_i['discovery_mean']:.1f} ms)")

    print("\n==================================================")
    print("PASO 3: EXPERIMENTOS MASIVOS (10, 50, 100, 200 USUARIOS)")
    print("==================================================")

    user_counts = [10, 50, 100, 200]
    experiment_results = []

    for n in user_counts:
        base_population = generate_users(n_users=n, seed=42)

        pop_fixed = [u.copy() for u in base_population]
        pop_intel = [u.copy() for u in base_population]

        tf_users, time_f_val, timeout_f_flag = run_simulation(pop_fixed, beam_angles, algorithm='fixed', max_timeout_ms=150000.0, debug=False)
        ti_users, time_i_val, timeout_i_flag = run_simulation(pop_intel, beam_angles, algorithm='intelligent', max_timeout_ms=150000.0, debug=False)

        # Corrección aplicada: Se evalúan los resultados devueltos por el motor (`tf_users` y `ti_users`)
        metrics_f = evaluate_performance(tf_users, time_f_val, timeout_f_flag)
        metrics_i = evaluate_performance(ti_users, time_i_val, timeout_i_flag)

        experiment_results.append({
            'Usuarios': n,
            'Fixed Total (ms)': f"{time_f_val}{' (TIMEOUT)' if timeout_f_flag else ''}",
            'Intelligent Total (ms)': f"{time_i_val}{' (TIMEOUT)' if timeout_i_flag else ''}",
            'Fixed Disc Mean': f"{metrics_f['discovery_mean']:.1f}" if not np.isnan(metrics_f['discovery_mean']) else "NaN",
            'Intelligent Disc Mean': f"{metrics_i['discovery_mean']:.1f}" if not np.isnan(metrics_i['discovery_mean']) else "NaN",
            'Fixed P95': f"{metrics_f['discovery_p95']:.1f}" if not np.isnan(metrics_f['discovery_p95']) else "NaN",
            'Intelligent P95': f"{metrics_i['discovery_p95']:.1f}" if not np.isnan(metrics_i['discovery_p95']) else "NaN",
            'Fixed Fairness': metrics_f['fairness_index'] if metrics_f['fairness_index'] == "N/A" else f"{metrics_f['fairness_index']:.3f}",
            'Intelligent Fairness': metrics_i['fairness_index'] if metrics_i['fairness_index'] == "N/A" else f"{metrics_i['fairness_index']:.3f}"
        })

    df_final = pd.DataFrame(experiment_results)
    print("\n")
    print(df_final.to_string(index=False))

    print("\n[+] Generando gráficos comparativos avanzados para tesis...")
    df_plot = pd.DataFrame([{
        'Usuarios': n,
        'Fixed Total (ms)': float(str(r['Fixed Total (ms)']).replace(' (TIMEOUT)', '')),
        'Intelligent Total (ms)': float(str(r['Intelligent Total (ms)']).replace(' (TIMEOUT)', '')),
        'Fixed Disc Mean': float(r['Fixed Disc Mean']) if r['Fixed Disc Mean'] != 'NaN' else 0,
        'Intelligent Disc Mean': float(r['Intelligent Disc Mean']) if r['Intelligent Disc Mean'] != 'NaN' else 0,
        'Fixed P95': float(r['Fixed P95']) if r['Fixed P95'] != 'NaN' else 0,
        'Intelligent P95': float(r['Intelligent P95']) if r['Intelligent P95'] != 'NaN' else 0,
        'Fixed Fairness': r['Fixed Fairness'],
        'Intelligent Fairness': r['Intelligent Fairness']
    } for r in experiment_results])

    plot_comparative_metrics(df_plot)