import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt 
url = "https://cdn.jsdelivr.net/npm/thrustcurve-db@latest/thrustcurve-db.json"
data = requests.get(url).json()

results =  []
for motor in data:
    samples = motor.get("samples")
    prop_weight_g = motor.get("propWeightG")
    manufacturer = motor.get("manufacturer")
    diameter_rocket = motor.get("diameter")
    impulse_class = motor.get("impulseClass")
    if not samples or not prop_weight_g: 
        continue
    total_impulse = motor.get("totImpulseNs")
    g = 9.81
    times = []
    thrusts = []
    prop_weight_g_kg = prop_weight_g / 1000
    for t , f in samples:
        times.append(t)
        thrusts.append(f)

    my_impulse = np.trapezoid(thrusts,times)

    my_Isp = total_impulse / (prop_weight_g_kg * g)
    results.append({
    "manufacturer": manufacturer,
    "diameter": diameter_rocket,
    "impulseClass": impulse_class,
    "my_Isp": my_Isp,
    "total_impulse": total_impulse,
})
df = pd.DataFrame(results)
df = df[df['my_Isp'] < 300]
df.to_csv('motors.csv' , index = False)
print(len(df))
print(df.head())
import os
print(os.path.abspath('motors.csv'))
coeffs = np.polyfit(df['diameter'], df['my_Isp'], 1)
x_line = np.linspace(df['diameter'].min(), df['diameter'].max(), 100)
y_line = np.polyval(coeffs, x_line)
df.plot.scatter(x='diameter', y='my_Isp', color='darkblue', grid=True)
plt.plot(x_line , y_line , color = 'red')
plt.show()
