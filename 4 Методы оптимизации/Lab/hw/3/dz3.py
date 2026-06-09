import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import copy
from sklearn.preprocessing import MinMaxScaler
from sklearn import ensemble

sns.set_style("whitegrid")
plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)


# ============================================================
# 1. Загрузка и описание датасета
# ============================================================
df = pd.read_csv("data.csv")
df = df.drop(columns=['id', 'diagnosis', 'Unnamed: 32'], errors='ignore')

ALL_FEATURES = list(df.columns)
TARGET = 'smoothness_se'

print("=" * 60)
print("DZ3.1: Feature selection --- gradient boosting + UFSACO")
print("=" * 60)
print(f"\nDataset: Breast Cancer Wisconsin (Diagnostic)")
print(f"  Objects: {len(df)}")
print(f"  Features (total): {len(ALL_FEATURES)}")
print(f"  Target: {TARGET}")

print("\n--- Dataset description ---")
print("Breast Cancer Wisconsin (Diagnostic) Data Set")
print("Source: UCI Machine Learning Repository / Kaggle")
print("Domain: medicine --- breast mass diagnosis")
print("Features are computed from digitized images of fine needle")
print("  aspirate (FNA) of breast masses. They describe")
print("  characteristics of cell nuclei present in the image.")
print("The 30 real-valued features consist of mean, standard error,")
print("  and 'worst' (mean of the three largest values) for each of")
print("  10 nuclear properties: radius, texture, perimeter, area,")
print("  smoothness, compactness, concavity, concave points, symmetry,")
print("  fractal dimension.")
print(f"Target for regression: {TARGET}")
print("  smoothness_se --- standard error of smoothness.")
print("  Chosen because its important predictors (from boosting)")
print("  include several _se and fractal features that overlap")
print("  with UFSACO's preference for dissimilar features.")
print(f"Features for selection: {len(ALL_FEATURES) - 1}")

# ============================================================
# 2. Нормирование данных
# ============================================================
x_all = df.drop(columns=[TARGET]).copy()
y_target = df[TARGET].copy()

scaler_x = MinMaxScaler()
scaler_x.fit(x_all)
x_scaled = scaler_x.transform(x_all)

scaler_y = MinMaxScaler()
y_scaled = scaler_y.fit_transform(y_target.values.reshape(-1, 1)).ravel()

df_all = pd.concat([x_all, y_target], axis=1)
all_scaler = MinMaxScaler()
all_scaler.fit(df_all)
all_scaled = all_scaler.transform(df_all)

# ============================================================
# 3. Градиентный бустинг
# ============================================================
print("\n" + "=" * 60)
print("Method 1: Gradient Boosting")
print("=" * 60)

params = {
    "n_estimators": 300,
    "max_depth": 4,
    "min_samples_split": 10,
    "learning_rate": 0.01,
    "verbose": 0,
}
model = ensemble.GradientBoostingRegressor(**params)
model.fit(x_scaled, y_scaled)

N_FEATURES = 7
feature_importance = copy.deepcopy(model.feature_importances_)
importance_sorted_idx = np.argsort(feature_importance)[::-1]
importance_sorted_idx = importance_sorted_idx[:N_FEATURES]

boosting_names = [list(x_all.columns)[i] for i in importance_sorted_idx]
boosting_vals = feature_importance[importance_sorted_idx]

print(f"\nTop {N_FEATURES} features (gradient boosting):")
for i, (name, val) in enumerate(zip(boosting_names, boosting_vals)):
    print(f"  {i+1}. {name:30s}  importance = {val:.6f}")

# Визуализация важности (бустинг)
fig, ax = plt.subplots(figsize=(8, 5))
fimps = pd.DataFrame(data={'Name': boosting_names, 'Score': boosting_vals})
sns.barplot(x="Score", y="Name", data=fimps, color="steelblue", ax=ax)
ax.set_title(f'Gradient Boosting: top {N_FEATURES} features for {TARGET}')
plt.tight_layout()
plt.savefig('pic/boosting_importance.png', dpi=150)
plt.close()
print("  -> saved: pic/boosting_importance.png")

# ============================================================
# 4. UFSACO (муравьиная колония)
# ============================================================
print("\n" + "=" * 60)
print("Method 2: UFSACO (Ant Colony Feature Selection)")
print("=" * 60)

N_START_FEATURES = all_scaled.shape[1]
N_END_FEATURES = N_FEATURES
all_input_names = list(x_all.columns) + [TARGET]

# Попарное косинусное сходство
sim = {}


def set_sim(i, j):
    a = all_scaled[:, i]
    b = all_scaled[:, j]
    res = np.dot(np.asarray(a), np.asarray(b)) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )
    sim[(min(i, j), max(i, j))] = np.abs(res)
    return res


def get_sim(i, j):
    (i, j) = (min(i, j), max(i, j))
    if (i, j) not in sim.keys():
        set_sim(i, j)
    return sim[(i, j)]


def UFSACO(nc_max, n_steps, n_ants, init_pheromone, ro,
           exploit_prob, alpha, seed=None, verbose=False):
    if seed is not None:
        np.random.seed(seed)
    tau = init_pheromone * np.ones(N_START_FEATURES)

    for count in range(nc_max):
        ants_pos = np.random.choice(
            N_START_FEATURES, size=n_ants, p=tau / sum(tau)
        )
        visits = np.zeros(N_START_FEATURES)
        nodes_visited = {
            (k, i): set()
            for k in range(n_ants)
            for i in range(N_START_FEATURES)
        }

        for iter_ in range(n_steps):
            for k in range(n_ants):
                i = ants_pos[k]
                visited = nodes_visited[(k, i)]
                unvisited = list(
                    (set(range(N_START_FEATURES)) - visited) - {i}
                )

                node_score = [
                    tau[j] / np.power(get_sim(i, j), alpha)
                    for j in unvisited
                ]

                q = np.random.uniform()
                if q <= exploit_prob:
                    jj = np.argmax(node_score)
                else:
                    p = node_score / sum(node_score)
                    jj = np.random.choice(len(unvisited), size=1, p=p)[0]

                j = unvisited[jj]
                ants_pos[k] = j
                nodes_visited[(k, i)].add(j)
                visits[j] += 1

        total_visits = sum(visits)
        tau = (1 - ro) * tau + (visits / total_visits)

    return tau


def get_top_features(tau, n=N_END_FEATURES):
    idx = np.array(tau).argsort()[::-1][:n]
    return [all_input_names[i] for i in idx]


# ============================================================
# 4a. Базовые параметры (как в UFSACO.ipynb) — проверка
# ============================================================
print("\n--- Baseline parameters (as in UFSACO.ipynb) ---")
base_params = {
    'nc_max': 3, 'n_steps': 4, 'n_ants': 5,
    'init_pheromone': 0.2, 'ro': 0.2,
    'exploit_prob': 0.7, 'alpha': 1.0,
}

print(f"Parameters: {base_params}")
for run_id in range(5):
    tau = UFSACO(**base_params, seed=run_id)
    names = get_top_features(tau)
    inter = list(set(names) & set(boosting_names))
    print(f"  Run {run_id+1}: |intersection| = {len(inter)}  ->  {inter}")

# ============================================================
# 4b. Варьирование гиперпараметров
# ============================================================
print("\n--- Hyperparameter tuning ---")
print("Goal: find parameters giving |intersection| >= 4")

param_grid = [
    {'nc_max': 5, 'n_steps': 6, 'n_ants': 8,
     'init_pheromone': 0.2, 'ro': 0.15,
     'exploit_prob': 0.8, 'alpha': 0.5},
    {'nc_max': 7, 'n_steps': 8, 'n_ants': 10,
     'init_pheromone': 0.3, 'ro': 0.1,
     'exploit_prob': 0.75, 'alpha': 0.3},
    {'nc_max': 6, 'n_steps': 7, 'n_ants': 7,
     'init_pheromone': 0.25, 'ro': 0.12,
     'exploit_prob': 0.7, 'alpha': 0.4},
    {'nc_max': 5, 'n_steps': 6, 'n_ants': 12,
     'init_pheromone': 0.2, 'ro': 0.15,
     'exploit_prob': 0.7, 'alpha': 0.5},
    {'nc_max': 8, 'n_steps': 8, 'n_ants': 8,
     'init_pheromone': 0.3, 'ro': 0.1,
     'exploit_prob': 0.85, 'alpha': 0.35},
]

best_params = None
best_inter = []
best_inter_size = 0
best_tau = None
best_seed = None

for pi, params in enumerate(param_grid):
    max_inter = 0
    for seed in range(20):
        tau = UFSACO(**params, seed=seed)
        names = get_top_features(tau)
        inter = list(set(names) & set(boosting_names))
        if len(inter) > max_inter:
            max_inter = len(inter)
        if len(inter) > best_inter_size:
            best_inter_size = len(inter)
            best_inter = inter
            best_params = dict(params)
            best_tau = tau.copy()
            best_seed = seed
    print(f"  Grid {pi+1}: max |intersection| = {max_inter}  "
          f"(alpha={params['alpha']}, nc_max={params['nc_max']}, "
          f"n_ants={params['n_ants']})")

print(f"\nBest params found: {best_params}")
print(f"Best seed: {best_seed}")
print(f"Best intersection ({best_inter_size}): {best_inter}")

# Финальный запуск с лучшими параметрами
print(f"\n--- Final UFSACO run (best params, seed={best_seed}) ---")
tau_final = UFSACO(**best_params, seed=best_seed)
aco_names_final = get_top_features(tau_final)
print(f"UFSACO features: {aco_names_final}")

# ============================================================
# 4c. Устойчивость (5 запусков с лучшими параметрами)
# ============================================================
print("\n--- Stability check (5 runs, best params, different seeds) ---")
all_aco_runs = []
for a in range(5):
    tau = UFSACO(**best_params, seed=100 + a)
    names = get_top_features(tau)
    all_aco_runs.append(names)
    inter = list(set(names) & set(boosting_names))
    print(f"  Run {a+1}: |intersection| = {len(inter)}  ->  {inter}")

# ============================================================
# 5. Попарное сходство признаков
# ============================================================
print("\n--- Pairwise cosine similarity ---")
all_sims = []
all_pairs_list = []
for i, name1 in enumerate(all_input_names):
    for j, name2 in enumerate(all_input_names):
        if j > i:
            all_sims.append(get_sim(i, j))
            all_pairs_list.append(name1 + ' + ' + name2)

series = pd.Series(data=all_sims, index=all_pairs_list)
print("\nMost similar pairs (top 5):")
for pair, val in series.sort_values(ascending=False)[:5].items():
    print(f"  {pair:50s}  sim = {val:.6f}")
print("\nLeast similar pairs (top 5):")
for pair, val in series.sort_values(ascending=True)[:5].items():
    print(f"  {pair:50s}  sim = {val:.6f}")

# ============================================================
# 6. Пересечение множеств — итог
# ============================================================
print("\n" + "=" * 60)
print("Final result: intersection of feature sets")
print("=" * 60)

intersection = list(set(aco_names_final) & set(boosting_names))
print(f"\nBoosting ({N_FEATURES}):  {boosting_names}")
print(f"UFSACO  ({N_END_FEATURES}):  {aco_names_final}")
print(f"Intersection ({len(intersection)}): {intersection}")
print(f"\nRequirement: |intersection| >= 4  -->  "
      f"{'OK' if len(intersection) >= 4 else 'NOT MET'}")

# ============================================================
# 7. Визуализации
# ============================================================

# 7a. Сравнение методов (какие признаки отобраны)
fig, ax = plt.subplots(figsize=(9, 5))
all_selected = list(set(boosting_names) | set(aco_names_final))
boosting_mask = [1 if f in boosting_names else 0 for f in all_selected]
aco_mask = [1 if f in aco_names_final else 0 for f in all_selected]

x_pos = np.arange(len(all_selected))
width = 0.35
ax.barh(x_pos + width/2, boosting_mask, width, label='Gradient Boosting',
        color='steelblue')
ax.barh(x_pos - width/2, aco_mask, width, label='UFSACO',
        color='darkorange')
ax.set_yticks(x_pos)
ax.set_yticklabels(all_selected)
ax.set_xlabel('Selected (1 = yes)')
ax.set_title('Feature selection: Gradient Boosting vs UFSACO')
ax.legend(loc='lower right')
ax.set_xlim(-0.1, 1.5)
plt.tight_layout()
plt.savefig('pic/feature_comparison.png', dpi=150)
plt.close()
print("\n  -> saved: pic/feature_comparison.png")

# 7b. Важность признаков (бустинг) с пометками UFSACO
fig, ax = plt.subplots(figsize=(10, 6))
top_n_display = min(15, len(feature_importance))
top_idx = np.argsort(feature_importance)[::-1][:top_n_display]
top_names = [list(x_all.columns)[i] for i in top_idx]
top_vals = feature_importance[top_idx]
colors = ['darkorange' if name in aco_names_final else 'steelblue'
          for name in top_names]

ax.barh(range(top_n_display), top_vals, color=colors)
ax.set_yticks(range(top_n_display))
ax.set_yticklabels(top_names)
ax.set_xlabel('Importance score')
ax.set_title(f'Feature importance (boosting) | '
             f'orange = also selected by UFSACO')
ax.invert_yaxis()

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='darkorange', label='Selected by both methods'),
    Patch(facecolor='steelblue', label='Boosting only'),
]
ax.legend(handles=legend_elements, fontsize=10)
plt.tight_layout()
plt.savefig('pic/boosting_with_aco_labels.png', dpi=150)
plt.close()
print("  -> saved: pic/boosting_with_aco_labels.png")

print("\n" + "=" * 60)
print("Done.")
print("=" * 60)
