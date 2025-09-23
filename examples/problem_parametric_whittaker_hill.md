# Graduate-Level Problem: Parametric Stability with Biharmonic Modulation (Whittaker–Hill Analysis)

## Problem Statement

Consider a one-dimensional oscillator of mass $m = 1.0 \times 10^{-15}$ kg attached to a spring with baseline stiffness $k = 1.0 \times 10^{-1}$ N/m, subject to viscous damping with dimensionless ratio $\zeta = 5.0 \times 10^{-3}$. The stiffness is modulated by two harmonics:

$$k(t) = k\big[1 + \varepsilon \cos(\Omega t) + \delta \cos(2\Omega t)\big].$$

The equation of motion is

$$m\,\ddot{x}(t) + 2\,\zeta\,m\,\omega_0\,\dot{x}(t) + k\big[1 + \varepsilon \cos(\Omega t) + \delta \cos(2\Omega t)\big] x(t) = 0,$$

where $\omega_0 = \sqrt{k/m}$. Use the parameter values

- $m = 1.0 \times 10^{-15}$ kg
- $k = 1.0 \times 10^{-1}$ N/m
- $\zeta = 5.0 \times 10^{-3}$
- $\varepsilon = 6.0 \times 10^{-2}$
- $\delta = 2.0 \times 10^{-2}$

Assume an infinitesimal initial displacement $x_0 = 1.0 \times 10^{-12}$ m at $t=0$ to probe linear stability.

Using Floquet theory, proceed as follows:

1. Rescale time via $\tau = (\Omega/2) t$ and map the equation to the Whittaker–Hill form

   $$\frac{d^2 x}{d\tau^2} + \Big[a - 2 q_1 \cos(2\tau) - 2 q_2 \cos(4\tau)\Big] x = 0,$$

   explicitly identifying $a, q_1, q_2$ in terms of $\varepsilon, \delta, \zeta$, and $\Omega/\omega_0$. State clearly how small damping $\zeta$ enters the canonical parameters.

2. In the linear regime (no nonlinearities beyond the biharmonic modulation), compute the largest Floquet characteristic exponent $\mu$ (in s$^{-1}$) for the two cases:
   - (i) $\Omega = \omega_0$
   - (ii) $\Omega = 2\,\omega_0$

   Use high-precision evaluation of Whittaker–Hill/Mathieu characteristic exponents and report $\mathrm{Re}(\mu)$.

3. With $\delta$ fixed at $2.0 \times 10^{-2}$ and $\zeta$ fixed as above, determine the minimal modulation depth $\varepsilon_c$ at $\Omega = 2\,\omega_0$ such that $\mathrm{Re}(\mu)=0$ (onset of the primary instability tongue). Report $\varepsilon_c$ to 4 significant digits.

4. For $\varepsilon = 6.0 \times 10^{-2}$, $\delta = 2.0 \times 10^{-2}$, and $\zeta$ as given, determine the instability window around $\Omega = 2\,\omega_0$, i.e., the lower and upper detuned values $(\Omega/\omega_0)_-$ and $(\Omega/\omega_0)_+$ at which $\mathrm{Re}(\mu)$ crosses zero. Report both to six decimal places.

Express your final answers in the form:
- $\mathrm{Re}(\mu)$ at $\Omega = \omega_0$: [numerical value] s$^{-1}$
- $\mathrm{Re}(\mu)$ at $\Omega = 2\,\omega_0$: [numerical value] s$^{-1}$
- Threshold $\varepsilon_c$ at $\Omega = 2\,\omega_0$ (with $\delta$ fixed): [numerical value]
- Instability window at $\varepsilon = 0.06$: $(\Omega/\omega_0)_- =$ [value], $(\Omega/\omega_0)_+ =$ [value]

Given physical constants: $\hbar = 1.055 \times 10^{-34}$ J·s


