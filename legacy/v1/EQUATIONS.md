# Ecuaciones y límites del modelo

## 1. Longitud de onda en espacio libre

\[
\lambda_0 = \frac{c}{f_0}
\]

Con \(c=299\,792\,458\ \mathrm{m/s}\). A 5 GHz, \(\lambda_0\approx59.96\) mm.

## 2. Ancho inicial del parche

\[
W = \frac{c}{2f_0}\sqrt{\frac{2}{\epsilon_r+1}}
\]

## 3. Permitividad efectiva aproximada

\[
\epsilon_{\mathrm{eff}} =
\frac{\epsilon_r+1}{2}+
\frac{\epsilon_r-1}{2}
\left(1+\frac{12h}{W}\right)^{-1/2}
\]

## 4. Longitud efectiva y corrección de borde

\[
L_{\mathrm{eff}}=\frac{c}{2f_0\sqrt{\epsilon_{\mathrm{eff}}}}
\]

\[
\frac{\Delta L}{h}=0.412
\frac{(\epsilon_{\mathrm{eff}}+0.3)(W/h+0.264)}
{(\epsilon_{\mathrm{eff}}-0.258)(W/h+0.8)}
\]

\[
L=L_{\mathrm{eff}}-2\Delta L
\]

Estas expresiones dan una estimación de diseño inicial para un parche rectangular dominante. No calculan de forma completa el puerto de alimentación, pérdidas del dieléctrico/cobre, rugosidad, acoplamiento, patrón exacto, ganancia realizada ni \(S_{11}\).

## 5. Métrica frontal/trasera

\[
R_{\mathrm{B/F,dB}}=10\log_{10}\left(\frac{P_{\mathrm{back}}}{P_{\mathrm{front}}}\right)
\]

Un valor más negativo indica menor potencia trasera en la definición angular elegida. La métrica debe obtenerse de un patrón electromagnético validado, no de la gráfica conceptual incluida en este prototipo.

## 6. Array futuro

Para elementos en posiciones \(\mathbf r_n\), con pesos complejos \(w_n=a_ne^{j\phi_n}\), el factor de array idealizado es:

\[
AF(\hat{\mathbf r})=\sum_{n=1}^{N}w_n
e^{jk\hat{\mathbf r}\cdot\mathbf r_n},\quad k=\frac{2\pi}{\lambda_0}
\]

El campo del array no es solamente el factor de array: debe combinarse con el patrón del elemento y considerar acoplamiento mutuo y red de alimentación. Para una sola antena, \(N=1\) y no existe todavía optimización de fase entre elementos.
