# Communication Theory — Assignment 1 Study Notes & Guide
**Course:** Communication Theory  
**Assignment:** 1 — Uniform vs. K-means Quantization  
**Group Members:**
1. Mazen Altelbany (64-12371)
2. Suhad Eyhab Rasheed (64-31506)
3. Sama Ismael Ahel (64-19880)

---

## 1. Group Information & Determining $a$:
The assignment specifies:
> *"Generate a random input vector of 10000 samples randomly in the range from $[-a, a]$ where $a$ is the largest number of the group members IDs."*

Our group IDs and their digits:
1. **Mazen Altelbany:** `64-12371` $\rightarrow$ digits $\{1, 2, 3, 4, 6, 7\}$
2. **Suhad Eyhab Rasheed:** `64-31506` $\rightarrow$ digits $\{0, 1, 3, 4, 5, 6\}$
3. **Sama Ismael Ahel:** `64-19880` $\rightarrow$ digits $\{0, 1, 4, 6, 8, \mathbf{9}\}$

The maximum single digit is **9**.  
Therefore:
$$\mathbf{a = 9} \implies \text{Signal range is } [-9, 9]$$

---

## 2. Theory & Code Breakdown

### Signal Generation
- Uniform distribution between $[-a, a] = [-9, 9]$.
- Number of samples $N = 10000$.
- Theoretical signal power:
  $$P_{\text{signal}} = \frac{1}{2a} \int_{-a}^{a} x^2 \, dx = \frac{a^2}{3} = \frac{9^2}{3} = 27$$

### Uniform Quantization
- Step size: $\Delta = \frac{2a}{L}$.
- Representation levels (midpoints):
  $$\hat{x}_k = -a + \left(k - 0.5\right)\Delta, \quad k = 1, \dots, L$$
- Each sample $x$ is mapped to interval $k = \lfloor (x - (-a))/\Delta \rfloor + 1$.
- Theoretical quantization noise variance:
  $$\sigma_e^2 = \frac{\Delta^2}{12} = \frac{(2a/L)^2}{12} = \frac{a^2}{3L^2} = \frac{27}{L^2}$$
- Theoretical SQNR:
  $$\text{SQNR} = 10 \log_{10}\left(\frac{P_{\text{signal}}}{\sigma_e^2}\right) = 10 \log_{10}\left(\frac{27}{27/L^2}\right) = 10 \log_{10}(L^2) = 20 \log_{10}(L) \approx 6.02 \times R \text{ dB}$$
  where $R = \log_2(L)$ is the number of bits.

### K-means Quantization
- Uses MATLAB built-in `kmeans(x, L, 'Replicates', 5)`.
- Implements the Lloyd-Max clustering algorithm:
  1. Nearest neighbor partition: Assigns each point to the closest centroid.
  2. Centroid update: Recalculates each centroid as the average of points in that cluster.
  3. Repeats until convergence.

---

## 3. Comparison & Discussion
1. **Why do Uniform and K-means give nearly identical results here?**
   - The input signal is uniformly distributed over $[-9, 9]$.
   - For a uniform distribution, the theoretically optimal centroids are equally spaced midpoints.
   - Because $N = 10000$ is large, K-means converges directly to these equal midpoints.
2. **What would happen if the input was Gaussian (Normal) or Speech Laplacian?**
   - A uniform quantizer would still place levels evenly, causing high distortion in the dense center and wasting levels on rare tails.
   - K-means would cluster more levels near 0 (where most samples are) and fewer levels far out, achieving much lower error and higher SQNR.
