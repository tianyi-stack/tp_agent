# Graduate-Level Problem: Driven Anharmonic Oscillator Analysis

## Problem Statement

Consider a one-dimensional oscillator consisting of a particle of mass $m = 1.0 \times 10^{-15}$ kg attached to a spring. The system experiences both harmonic and anharmonic restoring forces, with a potential energy given by:

$$V(x) = \frac{1}{2}kx^2 + \frac{\alpha}{4}x^4$$

where $k = 1.0 \times 10^{-1}$ N/m is the linear spring constant and $\alpha = 1.0 \times 10^{3}$ N/m³ is a small anharmonic parameter ($\alpha \ll k$). The particle is also subject to a time-dependent external driving force:

$$F_{ext}(t) = F_0 \cos(\omega_d t)$$

where $F_0 = 1.0 \times 10^{-12}$ N and the driving frequency $\omega_d = 0.9\omega_0$ (slightly below the natural frequency $\omega_0 = \sqrt{k/m}$).

The system starts from rest at $t = 0$ with an initial displacement $x_0 = 5.0 \times 10^{-11}$ m.

Using the Lagrangian formalism and Euler-Lagrange equations, followed by perturbation theory for the anharmonic correction, **determine the steady-state amplitude of oscillation** after transient effects have died out, and **calculate the first-order frequency correction** due to the anharmonic term for small amplitude oscillations.

Express your final answers in the form:
- Steady-state amplitude: $A_{steady} = $ [numerical value] m
- Frequency correction: $\Delta \omega = $ [analytical expression] rad/s

Given physical constants: $\hbar = 1.055 \times 10^{-34}$ J·s
