import csv
import os
import math
import numpy as np
from scipy import stats

# ============================================================
# 0. Настройка
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALPHA = 0.05  # уровень значимости

# ============================================================
# 1. Загрузка данных
# ============================================================
csv_path = os.path.join(BASE_DIR, 'RGR2_A-5_X1-X4.csv')
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    data = list(reader)

X1, X2, X3, X4 = [], [], [], []
for row in data:
    if len(row) == 4:
        try:
            X1.append(float(row[0]))
            X2.append(float(row[1]))
            X3.append(float(row[2]))
            X4.append(float(row[3]))
        except ValueError:
            pass

X1 = np.array(X1)
X2 = np.array(X2)
X3 = np.array(X3)
X4 = np.array(X4)

n = len(X1)
n1, n2 = len(X1), len(X2)
print(f"Объём выборки: n = {n}")
print(f"Уровень значимости: α = {ALPHA}")
print()

# ============================================================
# 2. Описательные статистики
# ============================================================
print("=" * 70)
print("ОПИСАТЕЛЬНЫЕ СТАТИСТИКИ")
print("=" * 70)

for name, col in [('X1', X1), ('X2', X2), ('X3', X3), ('X4', X4)]:
    print(f"\n{name}:")
    print(f"  Среднее: {np.mean(col):.4f}")
    print(f"  Медиана: {np.median(col):.4f}")
    print(f"  СКО (несмещ.): {np.std(col, ddof=1):.4f}")
    print(f"  Дисперсия (несмещ.): {np.var(col, ddof=1):.4f}")
    print(f"  Минимум: {np.min(col):.4f}")
    print(f"  Максимум: {np.max(col):.4f}")
    print(f"  Q1: {np.quantile(col, 0.25):.4f}")
    print(f"  Q3: {np.quantile(col, 0.75):.4f}")

# ============================================================
# ЗАДАНИЕ 4.2: Проверка гипотезы о равенстве математических ожиданий
#              X1 и X2 (параметрический критерий)
# ============================================================
print("\n" + "=" * 70)
print("ЗАДАНИЕ 4.2: ПРОВЕРКА ГИПОТЕЗЫ О РАВЕНСТВЕ МАТ. ОЖИДАНИЙ X1 И X2")
print("=" * 70)

# Двухвыборочный t-тест (приложение A.4)
t_stat, p_value_t = stats.ttest_ind(X1, X2, equal_var=True)

print(f"\n  H₀: EX₁ = EX₂")
print(f"  H₁: EX₁ ≠ EX₂ (двусторонняя альтернатива)")
print(f"  Критерий: двухвыборочный t-критерий Стьюдента (приложение A.4)")
print(f"  h = {t_stat:.4f}")
print(f"  p-value = {p_value_t:.6f}")
print(f"  Число степеней свободы: {n1 + n2 - 2}")

if p_value_t < ALPHA:
    print(f"  ВЫВОД: H₀ ОТВЕРГАЕТСЯ на уровне значимости α = {ALPHA}.")
else:
    print(f"  ВЫВОД: нет оснований отвергнуть H₀ на уровне значимости α = {ALPHA}.")

print(f"\n  Ошибка I рода (приложение A.2): отвергнуть H₀ (EX₁ = EX₂), когда на самом деле средние равны.")

# ============================================================
# ЗАДАНИЕ 4.3: Проверка гипотезы о параметре нормального
#              распределения X3
# ============================================================
print("\n" + "=" * 70)
print("ЗАДАНИЕ 4.3: ПРОВЕРКА ГИПОТЕЗЫ О МАТ. ОЖИДАНИИ X3 (НОРМАЛЬНОЕ)")
print("=" * 70)

# H₀: μ = μ₀ (one-sample t-test, приложение A.5)
mu0 = 75.24  # гипотетическое значение среднего (из карточки варианта)

t_stat_x3, p_value_x3 = stats.ttest_1samp(X3, mu0)

print(f"\n  H₀: μ = μ₀ = {mu0}")
print(f"  H₁: μ ≠ {mu0} (двусторонняя альтернатива)")
print(f"  Критерий: одновыборочный t-критерий Стьюдента (приложение A.5)")
print(f"  Выборочное среднее: x̄ = {np.mean(X3):.4f}")
print(f"  Выборочное СКО (несмещ.): σ̂ = {np.std(X3, ddof=1):.4f}")
print(f"  h = {t_stat_x3:.4f}")
print(f"  p-value = {p_value_x3:.6f}")
print(f"  Число степеней свободы: {n - 1}")

if p_value_x3 < ALPHA:
    print(f"  ВЫВОД: H₀ ОТВЕРГАЕТСЯ на уровне значимости α = {ALPHA}.")
else:
    print(f"  ВЫВОД: нет оснований отвергнуть H₀ на уровне значимости α = {ALPHA}.")

print(f"\n  Ошибка I рода (приложение A.2): отвергнуть H₀ (μ = {mu0}), когда на самом деле μ = {mu0}.")

# ============================================================
# ЗАДАНИЕ 4.4: Непараметрический критерий для X1 и X2
#              (Манна–Уитни, приложение A.7)
# ============================================================
print("\n" + "=" * 70)
print("ЗАДАНИЕ 4.4: НЕПАРАМЕТРИЧЕСКИЙ КРИТЕРИЙ МАННА-УИТНИ")
print("=" * 70)

u_stat, p_value_u = stats.mannwhitneyu(X1, X2, alternative='two-sided')

print(f"\n  H₀: распределения X₁ и X₂ одинаковы")
print(f"  H₁: распределения X₁ и X₂ различаются (двусторонняя альтернатива)")
print(f"  Критерий: U-критерий Манна–Уитни (приложение A.7)")
print(f"  U = {u_stat:.4f}")
print(f"  p-value = {p_value_u:.6f}")

if p_value_u < ALPHA:
    print(f"  ВЫВОД: H₀ ОТВЕРГАЕТСЯ на уровне значимости α = {ALPHA}.")
else:
    print(f"  ВЫВОД: нет оснований отвергнуть H₀ на уровне значимости α = {ALPHA}.")

print(f"\n  Ошибка I рода (приложение A.2): отвергнуть H₀ (распределения одинаковы),")
print(f"  когда на самом деле они не различаются.")

# Сравнение с параметрическим тестом
print(f"\n  Сравнение с параметрическим критерием (4.2):")
print(f"    Параметрический p-value = {p_value_t:.6f}")
print(f"    Непараметрический p-value = {p_value_u:.6f}")
if (p_value_t < ALPHA) == (p_value_u < ALPHA):
    print(f"    Выводы СОВПАДАЮТ: оба критерия {'отвергают' if p_value_t < ALPHA else 'не отвергают'} H₀.")
else:
    print(f"    Выводы РАЗЛИЧАЮТСЯ.")

# ============================================================
# ЗАДАНИЕ 4.5: Критерий согласия Пирсона (χ²) для X4
#              (приложение A.8)
# ============================================================
print("\n" + "=" * 70)
print("ЗАДАНИЕ 4.5: КРИТЕРИЙ СОГЛАСИЯ ПИРСОНА ДЛЯ X4")
print("=" * 70)

# X4: экспоненциальное распределение с ЗАДАННЫМ параметром
# λ = 0.106 (из карточки варианта, не оценивается по выборке)
lambda_given = 0.106
scale_given = 1.0 / lambda_given
print(f"\n  Предполагаемое распределение: Exp(λ = {lambda_given})")
print(f"  Параметр λ ЗАДАН в карточке варианта, не оценивается по выборке.")

# Разбиение на интервалы по правилу Стерджеса
k_sturges = int(1 + math.log2(n))
print(f"  Число интервалов (Стерджес): k = {k_sturges}")

# Равновероятностное разбиение
k = k_sturges
prob_per_bin = 1.0 / k
theoretical_quantiles = [0.0]
for i in range(1, k):
    theoretical_quantiles.append(stats.expon.ppf(i * prob_per_bin, scale=scale_given))
theoretical_quantiles.append(np.inf)

# Наблюдаемые частоты
observed = np.zeros(k)
for val in X4:
    for i in range(k):
        if theoretical_quantiles[i] <= val < theoretical_quantiles[i+1]:
            observed[i] += 1
            break

# Ожидаемые частоты (равновероятностные интервалы: pk = 1/k)
expected = np.full(k, n / k)

# Объединение интервалов с малыми ожидаемыми частотами (< 5)
min_expected = n / k
print(f"  Ожидаемая частота в интервале: {min_expected:.2f}")
if min_expected < 5:
    print(f"  ТРЕБУЕТСЯ объединение интервалов (ожидаемая частота < 5)")
    obs_merged = []
    exp_merged = []
    bounds_merged = [0.0]
    i = 0
    while i < len(observed):
        obs_sum = observed[i]
        exp_sum = expected[i]
        j = i + 1
        while j < len(observed) and exp_sum < 5:
            obs_sum += observed[j]
            exp_sum += expected[j]
            j += 1
        obs_merged.append(obs_sum)
        exp_merged.append(exp_sum)
        bounds_merged.append(theoretical_quantiles[j])
        i = j
    observed_final = np.array(obs_merged)
    expected_final = np.array(exp_merged)
    bounds_final = bounds_merged
else:
    observed_final = observed
    expected_final = expected
    bounds_final = theoretical_quantiles

m_final = len(observed_final)

# Статистика χ² (приложение A.8)
chi2_stat = np.sum((observed_final - expected_final)**2 / expected_final)
# Степени свободы: m - 1 (параметр λ ЗАДАН, приложение A.8)
df_chi2 = m_final - 1
p_value_chi2 = 1 - stats.chi2.cdf(chi2_stat, df_chi2)

print(f"\n  H₀: X₄ ~ Exp(λ = {lambda_given})")
print(f"  H₁: X₄ не подчиняется экспоненциальному распределению Exp({lambda_given})")
print(f"  Критерий: χ² Пирсона (приложение A.8)")
print(f"\n  Таблица частот:")
print(f"  {'Интервал':<25} {'n_k (набл.)':<15} {'np_k (ожид.)':<15}")
print(f"  {'-'*55}")
for i in range(m_final):
    print(f"  [{bounds_final[i]:.2f}, {bounds_final[i+1]:.2f})  "
          f"{observed_final[i]:<15.0f} {expected_final[i]:<15.2f}")

print(f"\n  Число интервалов после объединения: m = {m_final}")
print(f"  χ² = {chi2_stat:.4f}")
print(f"  Число степеней свободы: ν = m - 1 = {df_chi2} (параметр λ задан, приложение A.8)")
print(f"  p-value = {p_value_chi2:.6f}")

if p_value_chi2 < ALPHA:
    print(f"  ВЫВОД: H₀ ОТВЕРГАЕТСЯ на уровне значимости α = {ALPHA}.")
else:
    print(f"  ВЫВОД: нет оснований отвергнуть H₀ на уровне значимости α = {ALPHA}.")

print(f"\n  Ошибка I рода (приложение A.2): отвергнуть H₀ (X₄ ~ Exp({lambda_given})), когда на самом деле")
print(f"  X₄ действительно подчиняется этому экспоненциальному распределению.")

# ============================================================
# 6. ИТОГОВЫЙ ВЫВОД
# ============================================================
print("\n" + "=" * 70)
print("ИТОГОВЫЙ ВЫВОД")
print("=" * 70)

print(f"""
Вариант A-5, n = {n}, α = {ALPHA}.

1. Проверка гипотезы о равенстве математических ожиданий X1 и X2
   (параметрический критерий, приложение A.4):
   - Использован двухвыборочный t-критерий Стьюдента.
   - H₀: EX₁ = EX₂.
   - h = {t_stat:.4f}, p-value = {p_value_t:.6f}.
   - Гипотеза H₀ {'ОТВЕРГНУТА' if p_value_t < ALPHA else 'НЕ ОТВЕРГНУТА'}.

2. Проверка гипотезы о математическом ожидании нормального
   распределения X3 (приложение A.5):
   - Использован одновыборочный t-критерий Стьюдента.
   - H₀: μ = {mu0}.
   - h = {t_stat_x3:.4f}, p-value = {p_value_x3:.6f}.
   - Гипотеза H₀ {'ОТВЕРГНУТА' if p_value_x3 < ALPHA else 'НЕ ОТВЕРГНУТА'}.

3. Непараметрический критерий Манна-Уитни для X1 и X2
   (приложение A.7):
   - H₀: распределения X1 и X2 одинаковы.
   - U = {u_stat:.4f}, p-value = {p_value_u:.6f}.
   - Гипотеза H₀ {'ОТВЕРГНУТА' if p_value_u < ALPHA else 'НЕ ОТВЕРГНУТА'}.

4. Критерий согласия Пирсона для X4 (приложение A.8):
   - H₀: X₄ ~ Exp(λ = {lambda_given}).
   - χ² = {chi2_stat:.4f}, ν = {df_chi2}, p-value = {p_value_chi2:.6f}.
   - Гипотеза H₀ {'ОТВЕРГНУТА' if p_value_chi2 < ALPHA else 'НЕ ОТВЕРГНУТА'}.
""")

print("Анализ завершён.")
