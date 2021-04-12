---
layout: post
title:  "Deterministic Sampling for Efficient Uncertainity Transformation"
date:   2021-04-11 19:27:15 -0400
categories: uncertainity_quantification
---

## Motivation
A common requirement in many state estimation and machine learning problems  is the transformation of uncertainity under some nonlinear function. For example, consider a setup where a robot is equipped with a sensor to measure its position. Additionally, assume that the sensor is not perfect and is affected by some noise:

$$x \sim \mathcal{N}(\mu_x, \sigma_x^2),$$

where $$\mu_x \in \mathbb{R}$$ is the true position of the robot, $$x$$ is the position reported by the sensor. The uncertainity in the sensor measurements is quantified by  $$\sigma_x$$: higher the value, higher the uncertainity in the measured position: we say $$x$$ is $$\textit{normally distributed}$$ with $$\textit{mean}$$ $$\mu_x$$ and $$\textit{variance}$$ $$\sigma_x^2$$. 

Suppose we are interested in calculating the squared distance:

$$y = g(x) = x^2.$$

How is the variable $$y$$ distributed? Note that if $$x$$ is normally distributed and $$g(x)$$ is a $$\textit{linear}$$ function of $$x$$ then $$y$$ is normally distributed as well. For a general nonlinear function $$g(x)$$ (as is the case here), very little can be said about the distribution of $$y$$ The figures below show the distribution of $$x$$ and $$y$$:

{:refdef: style="text-align: center;"}
![My Image](/assets/deterministic_sampling_for_efficient_uncertainit_transformation/normal_dist.png){: width="250" }{: height="250" }
*Probability density function for $$x$$*
{: refdef}
{:refdef: style="text-align: center;"}
![My Image](/assets/deterministic_sampling_for_efficient_uncertainit_transformation/y_dist.png){: width="250" }{: height="250" }
*Probability density function for $$y$$*
{: refdef}

Clearly, $$y$$ is not normally distributed. How does one go about calculating the mean and covariance of $$y$$? The mean or \textit{expected value} of $$y$$ is given by:

$$\begin{equation}
\mathbb{E}[y] = \int g(x) \mathcal{N}(x | \mu_x, \sigma_x^2) dx.
\label{eqn:y_mean} 
\end{equation}$$

In this case we have access to the function $$g(x)$$ which is not always the case. Additionally, the form of $$g(x)$$ might not be tractible for computing the mean and covariance analytically. Alternative sampling based methods such as $$\textit{Markov chain Monte Carlo}$$ (MCMC) can be used. In MCMC, many samples are randomly drawn from $$\mathcal{N}(\mu_x, \sigma_x^2)$$ and the corresponding values of $$y$$ are calculated for each of the samples, which are then used to calculate the sample mean and sample covariance. Note that a drawback of MCMC is that the empirical mean and covariance converge to the true mean and covariance $$\textit{asymptotically}$$ which imples that many samples are required. This can be inefficient or computationally prohibitive in many cases.

## Unscented Transform

The unscented transform (UT), originally proposed by Jeffrey Uhlmann, is a function to estimate the mean and covariance estimates of the result of applying a given nonlinear transformation to a probability distribution. A major difference between MCMC and UT is that unlike MCMC, in UT the sample points are chosen deterministically. Essentially, UT "captures" a continuous distribution, which is described using a finite set of statistics, with deterministically chosen sample points, referred to as sigma points. There are many ways to choose sigma points. In generally, $$2n + 1$$ sigma points are necessary and sufficient to describe the mean and covariance of a distribution in $$n$$ dimensions. The nonlinear function is then applied to each sigma point and the mean and covariance of the transformation is calculated using the transformed sigma points. The figure below shows this procedure for a distribution in two dimensions. 

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

## Toy example

Returning to our toy example from earlier

The parameter $$\kappa$$ scales how far away the sigma points are from the mean. A reasonable choise for Gaussian distributions is $$\kappa=2$$. 

|           |    True value    | MCMC (10 samples)  |  MCMC (100 samples)  | MCMC (1000 samples) | UT (3 samples)|
| ----------|:----------:|:-----:|:-----:|:-----:|:-----:|
| $$\mu_y$$ |         1.0      |          12        |            12        |             12      |          12      |
| $$\sigma_y$$ |         1.0      |          12        |            12        |             12      |          12      |
