---
title: 'Deviation Deep Dive: Part II'
author: Kai
date: '2025-01-06'
slug: []
categories: []
tags:
  - blog
format: hugo-md
description: Why standard deviation?
---


``` r
library(tidyverse)
```

## Introduction

In the [last post](https://kai.rbind.io/posts/2024-09-22_deviation-deep-dive-pt1/) we talked about calculating the standard deviation, as well as some rationale for why it's calculated the way it is. One point we glossed over, though, is why we would go through the trouble of squaring the results only to take the square root later - why not a simple absolute function?

When I first went into this, I had assumed that it was because - due to the absolute value function having a sharp point right at 0 - it wasn't differentiable everywhere, so it caused some issues mathematically. Turns out that while this is *partially* true, it's not the *whole* truth.

<img style="float:right; width:40%;" src="abs-vs-sqr.png" />

I dug back through some crusty papers, all the way back to something by Fisher himself (Fisher, 1920). He and another guy were beefing (as always, it seems, for Fisher) about - essentially - if the standard deviation method or the mean absolute deviation were better. I'm going to do my best to explain what I've found here.

Oh, and before I get going, I'm not going to talk about Bessel's correction here (that is, dividing by $n - 1$ instead of just $n$). I'd like to talk about it in the next blog post, but to prevent us from getting too bogged down, I'm going to stick to the matter at hand.

Let's begin.

## What is the mean absolute deviation?

First, let's talk a little bit about how to calculate the mean absolute deviation. I'm going to abbreviate it as MAD, but to be clear in other contexts this could stand for *median* absolute deviation. Some people call it the average absolute deviation to get around this, but I already used MAD so much that I don't want to change it. Plus it's fun! He's angry!

The mean absolute deviation is much easier to describe and conceptualize as compared to the standard deviation:
1. Find the mean
2. Find the difference between the mean and every value
3. Take the absolute value of those differences
4. Sum them
5. Divide them by the number of values

This can be encapsulated by the following equation:

$$
MAD = \frac{1}{N}\sum_{i=1}^{N}\lvert X_{i} - \overline{X}\rvert
$$

Where $N$ is the number of value in the sample, $X_{i}$ is the $i$th value of some sample, and $\overline{X}$ is the mean of the sample.

## A case for the MAD

Some folks (including [Nassim Taleb](https://web.archive.org/web/20140116031136/http://www.edge.org/response-detail/25401)) have made a case for teaching MAD vs SD, for the reasons that it is easier to calculate as well as conceptualize. Personally, when I think about deviation, I find it easier to think about it as 'the average distance from the mean' (which is what MAD is) versus the more convoluted 'the square root of the average squared distance from the mean' (which is what SD is). This also gives more practical advantage to the value of the given deviation - if a population has a mean of 5 and an MAD of 2, you know that the average of values you pull from this distribution will be around 2 units away from the mean[^1].

### MAD isn't just a different SD

This isn't, however, why the standard deviation won out. In the paper written by Fisher I mentioned previously, Fisher argued that the standard deviation was actually *better* than mean absolute deviation. Stephan Gorard (2004) explained this topic beautifully by first showing the MAD and SD were different from one another, with a figure I will adapt below.

``` r
# Sample 10 numbers, from 0 - 100. Do that 10,000 times.
# Gorard only did it 255 times but more is always better. Right?
samples <- replicate(
  10000,
  sample(0:100, 10, replace = TRUE),
  simplify = FALSE
)

# Definitions of mean and standard deviation
mean_deviation <- function(x) {
  sum(abs(x - mean(x))) / length(x)
}

# No Bessel's correction yet - we'll get to that
standard_deviation <- function(x) {
  sqrt(sum((x - mean(x))^2) / length(x))
}

# Calculate MAD and SD for every single sample
mads <- sapply(samples, mean_deviation)
sds <- sapply(samples, standard_deviation)

plotting_data <- data.frame(
  mad = mads,
  sd = sds
)

ggplot(plotting_data, aes(mad, sd)) +
  geom_abline(slope = 1) +
  geom_point(shape = 16, alpha = 0.1) +
  theme_minimal() +
  labs(x = "Mean Absolute Deviation",  y = "Standard Deviation")
```

<img src="index.markdown_strict_files/figure-markdown_strict/unnamed-chunk-3-1.png" width="768" />

Gorard stated that either:
1. SD and MAD must be considered similar enough where you could simply pick your favorite (in which case why not just pick MAD due to being easier to understand and calculate) OR
2. You must admit they are different enough where considering the differences is worthwhile.

Looking at the plot, we note that the relationship isn't 1:1 - in which case it would just be some kind of line or curve - but rather it seems to be a kind of distribution, in which a given MAD might map to multiple SDs and vice-versa. We also note that the MAD is consistently smaller than the SD (due to all the points being above the x = y line).

So, it seems wise to admit that MAD $\neq$ SD. So which is better? This is a bit trickier to answer. Let's start with Fisher's argument.

## Why we like SD

Fisher, in 1920, published a paper in response to a certain Arthur Eddington. Eddington had stated that MAD was both practically and theoretically a better measure of deviation, and Fisher was going to set the record straight. I'm going to be real with you: I don't understand all the math that he did, and what some may call 'elegant', I call 'inscrutable', but we're going to work through it together.

I'm going to spoil the result of the paper so we can use that as the light at the end of the tunnel that we work towards ourselves (or at least one of the results of the paper - I didn't care much to go beyond the first three sections). The result stated that in order to estimate the standard deviation of a population using the MAD, you would need a sample size 14% greater to get the same 'tightness' of standard error. That's the briefest way to say it, but we'll work through it together at length. Starting now.

Just to warn you - like I mentioned previously, I didn't understand all the math, so while I can't *prove* it like he did, we can *verify* his claims using simulations. Yes, it's crude, and as such, tremendously on brand for me.

### Simulating samples

First, let's make a bunch of samples from a normal distribution:

``` r
# 30 values sampled from a normal distribution with mean 0 and standard
# deviation 5.
# Do that 100,000 times.
sd <- 5
n <- 30
n_samples <- 100000
samples <- replicate(n_samples, rnorm(n = n, sd = sd), simplify = FALSE)

# Let's look at some values of a sample:
samples[[1]][1:10]
```

     [1] -3.8199181 -8.9866895  2.1995732  4.3801874 -3.7793879  0.4391249
     [7]  5.2472810  0.8450794 -1.2777123 -2.6700292

``` r
# And a quick plot for good measure:
single_sample <- data.frame(x = samples[[1]])
ggplot(single_sample, aes(x)) +
  geom_histogram() +
  theme_minimal()
```

<img src="index.markdown_strict_files/figure-markdown_strict/unnamed-chunk-5-1.png" width="768" />

### SD

#### Mean

Ok, we have some samples (a lot of them - I just showed you one, we have 99,999 more).

Let's start as Fisher did, by describing the mean, variance, and standard error of the standard deviation. He says a lot of stuff, but in the end he states that for a normal distribution, the probability distribution of sample standard deviation (which we denote as $\sigma_{2}$, to distinguish it from the true population standard deviation $\sigma$):

$$
\frac{n^{(n-1)/2}}{2^{(n-3)/2} \times (\frac{n-3}{2})!} \times \frac{\sigma_{2}^{n-2}d\sigma_{2}}{\sigma^{n-1}}\times e ^{-\frac{n\sigma_{2}^{2}}{2\sigma^{2}}}
$$

Note that $n$ is the size of the sample (for us, 30).

We can calculate the mean of $\sigma_{2}$ using the definition of the expected value (the mean):

$$
E[X] = \int_{-\infty}^{\infty}xf(x)dx
$$

Which turns out to be:

$$
E[\sigma_{2}] = \sqrt{\frac{2}{n}} \times \frac{(\frac{n-2}{2})!}{(\frac{n-3}{2})!} \times \sigma
$$

For reasons I couldn't quite follow, when $n$ is sufficiently large, the distribution tends to be normal. This simplifies the mean of $\sigma_{2}$ to:

$$
E[\sigma_{2}] = (1-\frac{3}{4n})\sigma
$$

We can validate this via our simulated data:

``` r
# Again, NO Bessel's correction here
standard_deviation <- function(x) {
  sqrt(sum((x - mean(x))^2) / length(x))
}

# Calculate the standard deviation for each sample
sds <- sapply(samples, standard_deviation)

# Plot their distribution
ggplot(data.frame(x = sds), aes(x)) +
  geom_histogram() +
  theme_minimal() +
  geom_vline(
    xintercept = mean(sds),
    color = "red"
  ) +
  geom_vline(
    xintercept = (1 - 3/(4*n)) * sd,
    color = "blue",
    linetype = 2
  ) +
  geom_vline(xintercept = sd) +
  labs(x = "Standard Deviation")
```

<img src="index.markdown_strict_files/figure-markdown_strict/unnamed-chunk-6-1.png" width="768" />

In the above figure, I'm showing the distribution of $\sigma_{2}$ for all 100,000 samples. The blue line represents the theoretical mean, and the red line represents the actual mean. They're very close together because this distribution is made of 100,000 samples, so I'm going to agree with Fisher's definition of the mean of $\sigma_{2}$. Something important to notice is that while the mean of the distribution is *close* to the true population value of the standard deviation (black line, $\sigma$, which I set to be 5), even the theoretical mean isn't *exactly* 5. This means that we could take more and more samples and we still wouldn't get the correct estimate. As you can tell by looking at the equation for sample standard deviation (reproduced below just for you)

$$
\sigma_{2} = (1-\frac{3}{4n})\sigma
$$

the mean of the standard deviation of the sample ($\sigma_2$) only gets closer to the population standard deviation ($\sigma$) as the *individual* sample size ($n$) gets larger. This failure to converge to the true value even when you take a bunch of samples is called *bias*, and although it will approach $\sigma$ when $n$ becomes large, when $n$ is small it is doomed to underestimate the true value of $\sigma$. (sidenote)[^2].

#### Variance

The definition of variance is

$$
Var(X) = E[(X - \mu)^{2}]
$$

With some rearranging (described nicely in the [Wikipedia article for variance](https://en.wikipedia.org/wiki/Variance#Definition)), you can show this:

$$
Var(X) = E[X^{2}] - E[X]^{2}
$$

We just found $E[X]$ (or, more precisely, $E[\sigma_{2}$\]), so finding $E[X]^{2}$ is as trivial as squaring $E[X]$. However, we don't know $E[X^{2}]$

This can be found using the same equation we used to find $E[X]$, but instead of multiplying $f(x)$ by $x$, we would multiply it by $x^2$:

$$
E[X^{2}] = \int_{-\infty}^{\infty}x^{2}f(x)dx
$$

Seems hard! Fortunately, Fisher did the work for us, so the answer is:

$$
E[X^{2}] = \frac{n-1}{n}\sigma^{2}
$$

We can now use this to find the variance of $\sigma_{2}$ by plugging them into the variance definition above, which gives:

$$
Var(\sigma_{2}) = \frac{8n - 9}{16n^{2}}{\sigma^{2}}
$$

However, it looks like Fisher dropped the $-9$, maybe assuming that $n$ was large enough that it wouldn't matter. Remember that we assumed $n$ was large enough for $\sigma_{2}$ to approach normality, so this is at least a consistent guess. The difference between the two drops to ~5% at around $n=20$ (which I admit, isn't *nothing*). All that aside, dropping the $-9$ gives us:

$$
Var(\sigma_{2}) = \frac{\sigma^{2}}{2n}
$$

We can verify this using our simulated samples:

``` r
variance <- function(sigmas) {
  mean(sigmas^2) - mean(sigmas)^2
}

theoretical_variance_sd <- (sd^2 * 8 * n - 9)/(16 * n^2)
theoretical_variance_sd_no_nine <- sd^2/(n * 2)
actual_variance_sd <- variance(sds)
vars <- c(actual_variance_sd, theoretical_variance_sd, theoretical_variance_sd_no_nine)
data.frame(
  Name = c("Actual Variance", "Theoretical Variance", "Theoretical Variance (no -9)"),
  Value = round(vars, 4),
  Pct_Actual = round(vars * 100/actual_variance_sd, 2)
)
```

                              Name  Value Pct_Actual
    1              Actual Variance 0.4161     100.00
    2         Theoretical Variance 0.4160      99.98
    3 Theoretical Variance (no -9) 0.4167     100.13

The numbers are around 1% of each-other.

#### Standard Error

Not much else to say, but since we'll need this equation later: taking the square root gives us Fisher's final answer for the standard error of $\sigma_{2}$:

$$
\frac{\sigma}{\sqrt{2n}}
$$

### MAD

#### Mean

Before we get started, we need to talk about translating MAD to SD. We were able to measure the accuracy of our *estimate* of standard deviation ($\sigma_2$) because we know the *actual* standard deviation of the population (since we set it ourselves). However, how do we know what the MAD of the population is?

Turns out, for normally distributed populations, the MAD is $\sqrt{2/\pi}$ the size of the SD (Geary, 1935). To convert MAD to its cognate SD, we can multiply it by $\sqrt{\pi/2}$.

Anyway, Fisher does a lot of confusing math that I really don't understand, but he ultimately lands on the idea that the mean of $\sigma_{1}$ (the symbol we're using for the MAD that has been 'translated' to SD by multiplying it by $\sqrt{\pi/2}$) is:

Which we can verify using our simulated samples:

``` r
mad <- function(x) {
  (sum(abs(x - mean(x))) * sqrt(pi / 2)) / length(x)
}

# Calculate the standard deviation for each sample
mads <- sapply(samples, mad)

# Plot their distribution
plot <- ggplot(data.frame(x = mads), aes(x)) +
  geom_histogram() +
  theme_minimal() +
  geom_vline(
    xintercept = mean(mads),
    color = "red"
  ) +
  geom_vline(
    xintercept = sqrt((n-1)/n) * sd,
    color = "blue",
    linetype = 2
  ) +
  geom_vline(xintercept = sd)
plot
```

<img src="index.markdown_strict_files/figure-markdown_strict/unnamed-chunk-8-1.png" width="768" />

Looks like Fisher was telling the truth on this one, too. Just for fun, let's also add the mean of $\sigma_{2}$ there as well:

``` r
plot +
  geom_vline(xintercept = mean(sds), color = "green")
```

<img src="index.markdown_strict_files/figure-markdown_strict/unnamed-chunk-9-1.png" width="768" />

You'll note that $\sigma_{1}$ is just a hair closer to the true $\sigma$ than $\sigma_{2}$. This small advantage will generally be lost when we add Bessel's correction, but again, we'll cover that next time.

#### Variance

As before, to calculate variance we need to know what $E(X^{2})$ is, and as before, we'll take Fisher's word for it and verify it with brute force.

Fisher says that $\sigma_{1}^{2}$ is:

$$
\frac{(n-1)\sigma^{2}}{n^{2}}(\frac{\pi}{2} + \sqrt{n(n-2)}+sin^{-1}(\frac{1}{n-1}))
$$

When $n$ grows, $sin^{-1}(\frac{1}{n-1})$ converges to $0$, and $\sqrt{n(n-2)}$ converges to $n-1$. Therefore, this simplifies to:

$$
\frac{(n-1)\sigma^{2}}{n}(1 + (\frac{\pi}{2} - 1)\frac{1}{n})
$$

Using the same equation for variance we used previously, we find that:

$$
Var(\sigma_{1}) = E(\sigma_{1}^{2}) - E(\sigma_{1})^{2} = (\frac{n-1}{n^{2}})(\frac{\pi-2}{2})\sigma^{2}
$$

As in the previous variance, Fisher dropped a constant ($n - 1$ becomes $n$), simplifying the equation to:

$$
Var(\sigma_{1}) = (\frac{1}{n})(\frac{\pi-2}{2})\sigma^{2}
$$

Again, we can verify this with our simulated data:

``` r
theoretical_variance_mad <- ((n-1)/n^2) * ((pi - 2)/2) * sd^2
theoretical_variance_mad_no_one <- (1/n) * ((pi - 2)/2) * sd^2
actual_variance_mad <- variance(mads)
vars <- c(actual_variance_mad, theoretical_variance_mad, theoretical_variance_mad_no_one)
data.frame(
  Name = c("Actual Variance", "Theoretical Variance", "Theoretical Variance (no -1)"),
  Value = round(vars, 4),
  Pct_Actual = round(vars * 100/actual_variance_mad, 2)
)
```

                              Name  Value Pct_Actual
    1              Actual Variance 0.4781     100.00
    2         Theoretical Variance 0.4598      96.17
    3 Theoretical Variance (no -1) 0.4757      99.48

#### Standard Error

Finally, the standard error of $\sigma_{1}$ is:

$$
\frac{\sigma}{\sqrt{n}}\sqrt{\frac{\pi-2}{2}}
$$

### Comparing SD and MAD

Fisher essentially states that SD (or $\sigma_{2}$) is able to more efficiently use its data when compared to MAD ($\sigma_{1}$). He does so by comparing their standard errors, which we not so much *derived* but moreso *validated*:

$$
SE(\sigma_{1}) = \frac{\sigma}{\sqrt{n}}\sqrt{\frac{\pi-2}{2}}
$$

$$
SE(\sigma_{2}) = \frac{\sigma}{\sqrt{2n}}
$$

By taking their ratio, we see that $SE(\sigma_{1})$ is larger than $SE(\sigma_{2})$:

$$
\frac{SE(\sigma_{1})}{SE(\sigma_{2})} = \frac{\frac{\sigma}{\sqrt{n}}\sqrt{\frac{\pi-2}{2}}}{\frac{\sigma}{\sqrt{2n}}} = \sqrt{\pi-2}
$$

Smaller standard errors are generally better, and we can see that the classic SD method gives us more bang for our buck in this regard. If we wanted to determine how many more samples we would need to get the same standard error using the MAD method, we can do something like this:

$$
SE(\sigma_{1}) = SE(\sigma_{2})
$$

$$
\frac{\sigma}{\sqrt{n_1}}\sqrt{\frac{\pi-2}{2}} = \frac{\sigma}{\sqrt{2n_2}}
$$

$$
\frac{\sqrt{\pi-2}}{\sqrt{n_1}} = \frac{1}{\sqrt{n_2}}
$$

$$
\sqrt{n_2} = \sqrt{n1}\sqrt{\pi-2}
$$

$$
n_2 = n_1(\pi-2) \approx 1.14n_1
$$

Therefore, to get the same standard error as with the standard deviation method, we would need roughly 14% more samples if we used the MAD method.

## When we don't like SD

Despite being theoretically superior to MAD, SD may not always be the preferred metric. One reason I mentioned previously is didactic: it's marginally easier to teach MAD compared to SD ([Gary Kader demonstrates how the MAD might be 'discovered' in a classroom setting](https://web.archive.org/web/20130518092027/http://learner.org/courses/learningmath/data/overview/readinglist.html)).

Another reason is the comparative robustness of the MAD. In "Robust Statistics", Peter Huber (Huber, 1981) demonstrates that even a minute amount of 'contamination' in the data can MAD to win out over SD in terms of its estimation power. In the following example, I'll create samples just as before, except this time one out of the thirty samples will come from a distribution with a standard deviation 3x larger:

``` r
contaminated_samples <- replicate(
  n_samples,
  c(rnorm(n = n - 1, sd = sd), rnorm(1, sd = sd * 3)),
  simplify = FALSE
)

# Calculate the standard deviation for each sample
sds <- sapply(contaminated_samples, standard_deviation)
mads <- sapply(contaminated_samples, mad)

# Plot their distribution
ggplot(data.frame(x = mads), aes(x)) +
  geom_histogram() +
  theme_minimal() +
  geom_vline(xintercept = mean(mads), color = "red") +
  geom_vline(xintercept = mean(sds), color = "blue") +
  geom_vline(xintercept = sd)
```

    `stat_bin()` using `bins = 30`. Pick better value with `binwidth`.

<img src="index.markdown_strict_files/figure-markdown_strict/unnamed-chunk-11-1.png" width="768" />

We can see that while both estimates of standard deviation are dragged upwards due to the contaminants, $\sigma_{2}$ (SD, blue) is further off the mark (yes, this would be the case even with Bessel's correction). Huber showed that the MAD would win even in cases where only 0.2% (1/500) samples came from this 'highly variant' distribution.

## Conclusion

While SD is differentiable and MAD is not, in my research this appears not to be a huge talking point. Rather, the reason for using standard deviation seems to stem from its theoretical efficiency, combined with many years of tradition. When interacting with real-world data, however, MAD tends to win out due to being robust to outliers, and it tends to be a little more tractable for teaching in the classroom as well as practically wrapping your head around the spread of the data, due to the interpretability of MAD.

In the next post in this series, I'll talk about Bessel's correction and bias.

## Citations

My primary entry point for all downstream citations came from this Wikipedia article:
- Link: https://en.wikipedia.org/wiki/Average_absolute_deviation

A Mathematical Examination of the Methods of determining the Accuracy of an Observation by the Mean Error, and by the Mean Square Error. RA Fisher. 1920.
- Link: https://academic.oup.com/mnras/article/80/8/758/1063878

Revisiting a 90-year-old-debate: the advantages of the mean deviation. S Gorard. 2004.
- Link: https://web.archive.org/web/20221024193801/https://www4.hcmut.edu.vn/%7Endlong/TK/mat/04_standard_deviation_vs_absolute_deviation.pdf

The Ratio of the Mean Deviation to the Standard Deviation as a Test of Normality. RC Geary. 1935.
- Link: https://www.jstor.org/stable/2332693

Robust Statistics. PJ Hubert. 1981.

[^1]: This does NOT mean that half the values will fall within 3 - 7 and half will fall outside that. This is a property of the *median* absolute deviation, which I will not cover here

[^2]: Yes, yes. I see you back there waving your hand. You'd like to talk about Bessel's correction now. Well, that's too bad. I'm not going to talk about it in this blog post. I'll talk about it in the next one. Hold your horses.
