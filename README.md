# KazRosketPropulsion
Self-directed project on chemical propulsion systems. Goal: deep understanding of solid/hibryd rockets +code tools
Day 30 — Setting up the data pipeline

- Downloaded the complete ThrustCurve.org dataset (1,129 engines, JSON via thrustcurve-db).
- Analyzed the engine data structure: metadata (manufacturer, diameter, 
  propWeightG, totImpulseNs, etc.) + samples — an array of points [time, thrust].
- Wrote and debugged a calculation for a single engine:
  - Split the samples into times and thrusts
  - my_impulse using np.trapezoid (trapezoidal method) — area under the thrust curve
  - Compared it with the stated totImpulseNs: a difference of ~8.5% on the test engine, 
    which can be explained by the coarseness of the data points in the samples
  - my_Isp = impulse / (fuel_mass_kg * g) — obtained an Isp of ~40–44 s for 
    a small powder rocket motor (1/8A0.3, 6 mm, 0.5 g of fuel) — 
    plausible for the micro class
- Wrapped the logic in a `for motor in data` loop: with a filter for missing 
  samples/propWeightG
- Saving the result to `results` (a list)—for now, a list of raw Isp values, 
  not tied to a specific motor

Bugs fixed today:
- `continue` outside the loop (SyntaxError)
- Missing quotes in .get() — confused the dictionary key with the variable name
- Order: the `if not samples` check must come AFTER retrieving the samples, not before
- `.append()` is called with parentheses, not square brackets, and does not return 
  a value — you cannot write `results = results.append(...)`

TODO tomorrow:
- Rewrite results.append() to use a dictionary with manufacturer/diameter/impulseClass/
  my_Isp instead of a list

Translated with DeepL.com (free version)
