---
layout: post
title:  "Deterministic Sampling for Efficient Uncertainity Transformation"
date:   2021-04-11 19:27:15 -0400
categories: uncertainity_quantification
permalink: uncertainity_quantification
---

## Motivation
A common requirement in many state estimation and machine learning problems  is the transformation of uncertainity under some nonlinear function. For example, consider a setup where a robot is equipped with a sensor to measure its position. Additionally, assume that the sensor is not perfect and is affected by some noise. The measured position can be represented as follows:

$$x \sim \mathcal{N}(\mu_x, \sigma_x^2),$$

where $$\mu_x \in \mathbb{R}$$ is the true position of the robot, $$x$$ is the position reported by the sensor. The uncertainity in the sensor measurements is quantified by  $$\sigma_x$$: higher the value, higher the uncertainity in the measured position. We say $$x$$ is $$\textit{normally distributed}$$ with $$\textit{mean}$$ $$\mu_x$$ and $$\textit{variance}$$ $$\sigma_x^2$$. 

Suppose we are interested in calculating the squared distance:

$$y = g(x) = x^2.$$

How is the variable $$y$$ distributed? Note that if $$x$$ is normally distributed and $$g(x)$$ is a $$\textit{linear}$$ function of $$x$$ then $$y$$ is normally distributed as well. For a general nonlinear function $$g(x)$$ (as is the case here), very little can be said about the distribution of $$y$$. The figures below show the density functions:

{:refdef: style="text-align: center;"}
![My Image](/assets/deterministic_sampling_for_efficient_uncertainit_transformation/normal_dist.png){: width="250" }{: height="250" }
*Probability density function of $$x$$*
{: refdef}
{:refdef: style="text-align: center;"}
![My Image](/assets/deterministic_sampling_for_efficient_uncertainit_transformation/y_dist.png){: width="250" }{: height="250" }
*Probability density function of $$y$$*
{: refdef}

Clearly, $$y$$ is not normally distributed. How does one go about calculating the mean and covariance of $$y$$? The mean of $$y$$ is given by:

$$\begin{equation}
\mathbb{E}[y] = \int g(x) \mathcal{N}(x | \mu_x, \sigma_x^2) dx.
\label{eqn:y_mean} 
\end{equation}$$

In this case we have access to the function $$g(x)$$ which is not always the case. Additionally, the form of $$g(x)$$ might not be tractible for computing the mean and covariance analytically. Sampling based methods such as $$\textit{Markov chain Monte Carlo}$$ (MCMC) can be used. In MCMC, samples are randomly drawn from $$\mathcal{N}(\mu_x, \sigma_x^2)$$ and the corresponding values of $$y$$ are calculated for each of the samples, which are then used to calculate the sample mean and sample covariance. A major drawback of MCMC is that the sample mean and sample covariance converge to the true mean and covariance $$\textit{asymptotically}$$, which imples that many samples are required. This can be inefficient or computationally prohibitive in many cases.

## Unscented Transform

The unscented transform (UT), originally proposed by Jeffrey Uhlmann, is a function to estimate the mean and covariance estimates of the result of applying a given nonlinear transformation to a probability distribution. A major difference between MCMC and UT is that unlike MCMC, in UT, the sample points are chosen deterministically. Essentially, UT "captures" a continuous distribution, which is described using a finite set of statistics, with deterministically chosen sample points referred to as sigma points. There are many ways to choose sigma points. In generally, $$2n + 1$$ sigma points are necessary and sufficient to describe the mean and covariance of a distribution in $$n$$ dimensions. The nonlinear function is then applied to each sigma point and the mean and covariance of the transformation is calculated using the transformed sigma points. The figure below shows this procedure for a distribution in two dimensions. 

{:refdef: style="text-align: center;"}
![My Image](/assets/deterministic_sampling_for_efficient_uncertainit_transformation/ut.png)
{: refdef}

The steps to calculate sigma points for the case where $$n=1$$ are as follows:

* Compute a set of 3 ($$2n + 1$$ with $$n = 1$$) sigma points computed according to:

$$\begin{align*}
x_0 &= \mu_x,\\
x_1 &= \mu_x + \sqrt{1 + \kappa} ~ \sigma_x,\\
x_2 &= \mu_x - \sqrt{1 + \kappa} ~ \sigma_x.
\end{align*}$$

* Pass each of the sigma points through the nonlinear function $$g(\cdot)$$:

$$\begin{align*}
y_i &= g(x_i),~ i=0,1,2.
\end{align*}
$$

* The mean of the output, $$\mu_y$$, is computed as

$$\begin{align*}
\mu_y = \sum_{i=0}^2 \alpha_i y_i,
\end{align*}$$

where

$$\begin{align*}
\alpha_i &= \begin{cases}
\frac{\kappa}{1 + \kappa} &i = 0\\
\frac{1}{2}\frac{1}{1 + \kappa} &\text{otherwise}
\end{cases}
\end{align*}$$

* The variance of the output density, $$\sigma_y$$, is compuated as:

$$\begin{align*}
\sigma_y^2 = \sum_{i=0}^2 \alpha_i (y_i - \mu_y)^2.
\end{align*}
$$

The parameter $$\kappa$$ scales how far away the sigma points are from the mean. A reasonable choise for Gaussian distributions is $$\kappa=2$$. 

## Toy example
Consider the example from earlier with $$ x \sim \mathcal{N}(\mu_x = 0, \sigma_x^2 = 1)$$ and $$y = x^2$$. The following table compares MCMC and UT in terms of sample efficiency. Sigma points are computed using the procedure outlined above.

|           |    True value    | UT (3 samples) | MCMC (10 samples)  |  MCMC (100 samples)  | MCMC (1000 samples) | MCMC (10000 samples) | MCMC (10000 samples) |
| ----------|:----------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| $$\mu_y$$ |         1.0      |          1.0        |            0.83        |         0.99     |          1.04      |  0.97 | 0.99|
| $$\sigma_y^2$$ |         2.0      |         2.0        |            2.74        |         2.03      |          2.06      | 1.85 | 2.0 |  

The true value of mean and covariance were computed analytically. For $$y = x^2$$, the UT captures the mean and the covariance of the transformed variable *exactly*. This is not true for a general nonlinear function. 

#### Remarks
* The above table considers the case of a distribution with a single dimension. In higher dimensions, the calculation of sigma points requires calculating the square root of the covariance matrix which can be expensive. However, Cholesky decomposition can be used to calculate the matrix square root efficiently.

* The distribution captured by the unscented transform is accurate to the third-order. In the example above, $$g(x) = x^2$$ is completely characterized by the first and second-order derivatives and hence is completely captured by the UT. 

* The UT can be shown to be a specific case of the more generally *Gaussian Quadrature* methods.

### References
Jeffery K. Uhlmann, Dynamic Map Building and Localization: New Theoretical Foundations, University of Oxford, PhD thesis, 1995.

E. A. Wan and R. Van Der Merwe, [The unscented Kalman filter for nonlinear estimation](https://ieeexplore.ieee.org/document/882463), Proceedings of the IEEE 2000 Adaptive Systems for Signal Processing, Communications, and Control Symposium (Cat. No.00EX373), Lake Louise, AB, Canada, 2000, pp. 153-158, doi: 10.1109/ASSPCC.2000.882463.

Barfoot, T., [State Estimation for Robotics](https://www.cambridge.org/core/books/state-estimation-for-robotics/AC0E0AC229C55203B3C8F106BCB61F48), Cambridge: Cambridge University Press, (2017).

Gaussian Quadrature, (26 March 2021), In Wikipedia. [Link](https://en.wikipedia.org/wiki/Gaussian_quadrature)