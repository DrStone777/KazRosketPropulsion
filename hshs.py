import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from scipy.stats import pearsonr

url = "https://cdn.jsdelivr.net/npm/thrustcurve-db@latest/thrustcurve-db.json"
data = requests.get(url).json()


results = []
for motor in data:
    samples = motor.get("samples")
    prop_weight_g = motor.get("propWeightG")
    manufacturer = motor.get("manufacturer")
    diameter_rocket = motor.get("diameter")
    impulse_class = motor.get("impulseClass")
    prop_info = motor.get("propInfo")
    total_impulse = motor.get("totImpulseNs")

    # Защита от плохих данных 

    # 1. Проверяем массу: исключаем None и нулевой вес (защита от деления на 0)
    if prop_weight_g is None or prop_weight_g <= 0:
        continue

    # 2. Проверяем samples: это должен быть не пустой список, содержащий точки
    if not samples or not isinstance(samples, list) or len(samples) < 2:
        continue

    
    if total_impulse is None:
        continue

    g = 9.81
    times = []
    thrusts = []
    prop_weight_g_kg = prop_weight_g / 1000

    
    try:
        for t, f in samples:
            times.append(float(t)) 
            thrusts.append(float(f))

        calculated_impulse = np.trapezoid(thrusts, times)

      
        calculated_Isp = total_impulse / (prop_weight_g_kg * g)

        results.append(
            {
                "manufacturer": manufacturer,
                "diameter": diameter_rocket,
                "impulseClass": impulse_class,
                "calculated_Isp": calculated_Isp,
                "calculated_impulse": calculated_impulse,
                "propellant_type": prop_info,
            }
        )
    except (ValueError, TypeError, ZeroDivisionError):
       continue


df = pd.DataFrame(results)
df.dropna(subset=["propellant_type"], inplace=True)
df = df[df["calculated_Isp"] < 300]
df.to_csv("motors.csv", index=False)

top_fuels = df['propellant_type'].value_counts().head(7).index
df["clean_fuel"] = np.where(df['propellant_type'].isin(top_fuels),df['propellant_type'],'Other')

df["fuel_cat"] = df['clean_fuel'].astype("category")
df["color_codes"] = df["fuel_cat"].cat.codes
df_clean = df[df["clean_fuel"] != "Other"]
print(len(df))
print(df.head())
print(os.path.abspath("motors.csv"))


coeffs = np.polyfit(df["diameter"], df["calculated_Isp"], 1)
x_line = np.linspace(df["diameter"].min(), df["diameter"].max(), 100)
y_line = np.polyval(coeffs, x_line)

ax = df.plot.scatter(
    x="diameter", 
    y="calculated_Isp",
    c= "color_codes" ,
    cmap = 'tab10' ,  
    grid=True
    )
plt.plot(x_line, y_line, color = "red")
cbar = ax.collections[-1].colorbar
cbar.set_ticks(range(len(df['fuel_cat'].cat.categories)))
cbar.set_ticklabels(df['fuel_cat'].cat.categories)
plt.show()

from scipy.stats import pearsonr

for fuel in df["clean_fuel"].unique():
    df_sub = df[df["clean_fuel"] == fuel]
    if len(df_sub) > 2:
        r, p = pearsonr(df_sub["diameter"], df_sub["calculated_Isp"])
        print(f"Топливо:{fuel} R = {r:.3f}, R² = {r**2:.3f}, p-value = {p:.4f}")


print(df.describe()) 
print(df['clean_fuel'].value_counts()) 
summary = df.groupby('clean_fuel').agg({
    'calculated_Isp': ['mean', 'std', 'count'],
    'diameter': 'mean'
}).round(2)
print("\n=== Сравнение топлив ===")
print(summary)