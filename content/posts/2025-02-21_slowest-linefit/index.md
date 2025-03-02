---
title: 'The Slowest Line Fit: Part I'
author: kai
date: 2025-02-21
slug: []
categories: [statistics]
tags:
  -blog
format: hugo-md
description: What's a 'good fit'? And how to we get there?
---

# Introduction
Artificial intelligence (AI), machine learning (ML), and statistics are all phrases that get thrown around with increasing irreverence, making it difficult to nail down exactly what is what. In theory, AI is a category that encompasses ML, but nowadays, colloquially, when people refer to AI they are referring to large language models (LLMs) or some other kind of generative model, muddying the waters that much more. Further, data scientists and statisticians are doing plenty of work that they would probably only consider ML for résumé reasons, but in reality ML and statistics seems to me to be more of an-ever shifting, perspective-dependent Venn diagram rather than any kind of spectrum. 

The point of that is to provide some insurance that if I say something funky, it's only *partially* because I'm an idiot. The other 20% is because it's confusing.

I want to learn more about machine learning. I know a little, but in a haphazard, 'I guess its working' kind of way. And I know a bit about statistics. I'm curious if I could learn a bit about machine learning by explaining it to myself (and hopefully you?) through the lens of one of the simpler things to do in statistics: linear regression.

# What is linear regression?
Line fitting. It's line fitting. I mean, yes, it's so much more, too (you could argue it's the backbone for [most statistical tests](https://lindeloev.github.io/tests-as-linear/)), but I don't want to over-complicate this right from the get go. You have some data, you put a line through it that fits as good as possible. We'll work out the details as we go along.

Some complications, though:

-   What do you mean 'as good as possible'?
-   I have a lot of kinds of data and my paper is flat. How does this work?
-   Some of these data are NOT numbers.
-   These data don't look like a line at all

Even though I was just thinking about these complications right off the dome, they look like they would form a good blog post series, so let's do that, starting from the top and moving our way down.

If you would prefer to get this from a vetted and coherent source rather than from the ravings of a madman, you cannot beat 'An Introduction to Statistical Learning', which you can get online, for free (legally, even!) [here](https://www.statlearning.com/).


# Motivating potato example

{{% showntellcode summary="Setup" %}}
```python
    import pandas as pd
    import numpy as np
    import altair as alt
    from sklearn.linear_model import LinearRegression
    from kai_theme import kai # For themeing
```
{{% /showntellcode %}}

The stress of computers has become too much and we have decided to become potato farmers. The humble potato knows relatively little of 'agile' and 'git' (although the dull memory of technology still haunts it, which is why you can power clocks with potatoes). Alas, old habits die hard and you find your data-hungry mind logging the amount of potatoes you harvested and the inches of rain you received that season[^1]

<div class="center">
{{% tell %}}
Here are your logs for the rain and yield for the first 10 of 50 harvests:
{{% /tell %}}
<div class="show">

|rain|yield|
|----|-----|
|4.07|  124|
|2.23|   37|
|2.68|   49|
|4.36|   77|
|3.27|   90|
|8.01|  137|
|2.51|   90|
|6.79|  139|
|2.71|   66|
|2.98|   61|
</div>
</div>

{{% showntellcode summary="Potato Data Generating Code - Contains Spoilers!" %}}
```python
np.random.seed(1)

def make_potato_data(n):
    e = np.random.normal(0, scale=20, size=n)
    rain = (np.random.beta(a=2, b=4, size=n) * 10).round(2)
    potatoes = (23.2 * rain - 3 + e).clip(0).round()
    return pd.DataFrame({"rain": rain, "yield": potatoes})

tatos = make_potato_data(50)
```
{{% /showntellcode %}}

We might look at these and note that the seasons with the highest amount of rain appeared to have the most potatoes, and the seasons with the lowest amount of rain tended to have the lowest number of potatoes.

<div class="center">
{{% tell %}}
To make this a little clearer, we can plot it:
{{% /tell %}}
{{% show "tatos.svg" "300px" %}}
</div>

{{% showntellcode summary="Plotting Code" %}}
```python
tatos_plt = alt.Chart(tatos).encode(x="rain", y="yield").mark_circle()
tatos_plt.save('tatos.svg')
```
{{% /showntellcode %}}


There definitely seems to be an association between rain an the number of potatoes. These data aren't just beautiful to behold (like all data are), we can also use these data to answer questions like:

- For each additional inch of rain, how many potatoes will I get?
- The forecast says it'll rain 7 inches this season. How many potatoes should I expect?
- I have a potato debt with the potato mafia and I must give them no fewer than 100 potatoes this season or I must change my name and flee. At least how much rain should I hope for?
- How _much_ can we predict about yield via just rain? How much variability _can't_ be predicted via just rain?

All of this can be answered with starting with the humble line. Where is that guy anyway?

# The Humble Line

<div class="center">
{{% tell %}}
Oh my god. He's here but he's shown up terribly drunk. This is embarrassing for both of us.
{{% /tell %}}
{{% show "tatos_bad_fit.svg" 300px %}}
</div>

{{% showntellcode summary = "Plotting Code" %}}
```python
bad_fit = pd.DataFrame({'rain': [0,10], 'yield': [150, 100]})
bad_fit_plt = alt.Chart(bad_fit).encode(x="rain", y="yield").mark_line()
tatos_bad_fit_plt = tatos_plt + bad_fit_plt
tatos_bad_fit_plt.save('tatos_bad_fit.svg')
```
{{% /showntellcode%}}

<div class="center">
{{% tell %}}
We both know that's a really crummy fit, just as we know that this one is probably a little better:
{{% /tell %}}
{{% show "tatos_ok_fit.svg" 300px %}}
</div>

{{% showntellcode summary = "Plotting Code" %}}
```python
ok_fit = pd.DataFrame({'rain': [0,10], 'yield': [50, 150]})
ok_fit_plt = alt.Chart(ok_fit).encode(x="rain", y="yield").mark_line()
tatos_ok_fit_plt = tatos_plt + ok_fit_plt
tatos_ok_fit_plt.save('tatos_ok_fit.svg')
```
{{% /showntellcode %}}

Mind you, it's still not a *great* fit, but it's worth noting that our peepers can tell that something is a good fit. But how to we explain to computers what a good fit is?

Before we dig into this, let's start with some data that plots a little better - the differences in scales between rain and potatoes causes some issues in visualizing, but all the mathematics remain the same. We'll return to our potatoes soon enough.

<div class="center">
{{% tell %}}
You might be able to tell that there's a trend with these data, and that it seems to be roughly one-to-one[^2]. 
{{% /tell %}}
<div class="show">

|   x|     y|
|----|------|
|   1|  1.24|
|   2|  2.20|
|   3|  3.66|
|   4|  5.79|
|   5|  4.88|
|   6|  4.77|
|   7|  5.82|
|   8|  7.33|
|   9|  7.33|
|  10| 10.83|
</div>
</div>
{{% showntellcode summary = "Example Data Generating Code - Contains Spoilers!" %}}
```python
def create_example_data(n):
    x = range(1, n+1)
    y = x + np.random.normal(0, 1, n)
    y = y.round(2)
    return pd.DataFrame({"x": x,"y": y})

ex = create_example_data(10)
```
{{% /showntellcode%}}


<div class="center">
{{% tell %}}

Let's plot it:

{{% /tell %}}
{{% show "ex.svg" "300px" %}}
</div>


{{% showntellcode summary= "Plotting Code" %}}
```python
ex_plt = alt.Chart(ex).encode(
    x=alt.X("x", scale = alt.Scale(domain=(0,12)), title = "x"),
    y=alt.Y("y", scale = alt.Scale(domain=(0,12)), title = "y")
).mark_circle()
ex_plt.save('ex.svg')
```
{{% /showntellcode %}}

<div class = "center">
{{% tell %}}

Now let's put an arbitrary line atop: 

{{% /tell %}}
{{% show ex_rand_fit.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}
```python
ex_line = pd.DataFrame({"x":[0,12], "y":[4,8]})
ex_line_plt = alt.Chart(ex_line).encode(x="x", y="y").mark_line()
ex_rand_fit_plt = ex_plt + ex_line_plt
ex_rand_fit_plt.save('ex_rand_fit.svg')
```
{{% /showntellcode %}}

We can see that this is a good fit, though it could be better. In order to create some kind of metric for determining fit, we might consider adding up the distance between all the points and the line. 

<div class = "center">
{{% tell %}}
That is, adding up all of these lines:
{{% /tell %}}
{{% show ex_ortho.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}
```python
def calc_orth_segment_to_line(points, line):
    # https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Another_formula
    # Given y = mx + k and x0, y0
    # k = y - mx
    # x = (x0 + my0 - mk)/(m^2 + 1)
    # put into eq to get y
    m = (line.y[1] - line.y[0])/(line.x[1] - line.x[0])
    k = line.y[0] - m * line.x[0]
    x = (points.x + m * points.y - m * k) / (m**2 + 1)
    y = m * x + k
    return pd.DataFrame({"x": points.x, "x2": x, "y": points.y, "y2": y,})

ortho_lines = calc_orth_segment_to_line(ex, ex_line)
ortho_lines_plt = alt.Chart(ortho_lines).encode(
    x="x", x2 = "x2", y="y", y2="y2"
).mark_rule()

ex_ortho_plt = ex_plt + ex_line_plt + ortho_lines_plt
ex_ortho_plt.save('ex_ortho.svg')
```
{{% /showntellcode %}}

In theory we could count up the distances of all those lines and then try to find a line that minimizes that distance. Were it that simple! While this is *a* way to fit a line, it isn't common. I'll teach you the most common way first, and then I'll briefly discuss other methods for fitting.

The most common way is known as 'ordinary least squares' (OLS). Ordinary, as it is in contrast to the [myriad other ways you can fit by least squares](https://stats.stackexchange.com/a/251192), and 'least squares' being an incredibly terse way of saying 'minimizing the sum of the squared residuals', which I'll explain later.


<div class="center">
{{% tell %}}
The first thing that differs between the figure above and OLS is that we don't measure the distance perpendicular to the fit, we measure it by 'dropping down' to the line:
{{% /tell %}}
{{% show "ex_line-drop.svg" 300px %}}
</div>

{{% showntellcode summary="Plotting Code"%}}
```python
def calc_drop_segment_to_line(points, line):
    m: float = (line.y[1] - line.y[0])/(line.x[1] - line.x[0])
    k: float = line.y[0] - m * line.x[0]
    y = m * points.x + k
    return pd.DataFrame({"x": points.x, "x2": points.x, "y": points.y, "y2": y})

drop_lines = calc_drop_segment_to_line(ex, ex_line)
drop_lines_plt = alt.Chart(drop_lines).encode(
    x="x", x2 = "x2", y="y", y2="y2"
).mark_rule()
ex_line_drop_plt = ex_plt + ex_line_plt + drop_lines_plt
ex_line_drop_plt.save('ex_line-drop.svg')
```
{{% /showntellcode %}}

We 'drop down' to the line (or up, depending on where the point is in relation to the line) because we presume that the independent variable - here x - is accurately measured. That is, the difference between our prediction (the line) and our observed values (points) is due only to the fault of the y-axis. Note that most of the time, this is actually not true, but it's a little fiction we allow ourselves and it actually works out fairly well. There's nothing special about the x-axis, besides the fact that the independent variable goes there most of the time. If we had switched the axes, we would 'drop to the left' (or right) instead.

While we'll get to higher dimensions in a different post in the future, just know that if you had multiple independent variables, you would draw the line such that the only thing changing as you moved from the line to the point would be your dependent variable. Since the y-axis is our dependent variable, that means 'dropping down'.

If we were to sum up all the (absolute) distances from points to lines, this kind of fit would be known as *Least Absolute Deviations*. It has its place, but we won't cover it here. It has similar benefit to being comparatively robust to outliers, much like the mean absolute deviation is robust to outliers compared to the standard deviation (I wrote [a blog post](https://kai.rbind.io/posts/2025-01-06_deviation-deep-dive-pt2/) about it IF YOU EVEN CARE).

Briefly, we should talk about some terminology. These distances from the points to the line are called *residuals*. This is not to be confused with *errors*. A residual is the difference between an observed value and an estimated value. In the case of our linear modeling, the observed value is the y-value of the point, and the estimated value is the y-value of the line at the same x-value (that is, the point that is 'dropped down' (or up) to). On the other hand, an error is the difference between an observed value and the 'true' value. This is almost never known in practical situations! To make matters more confusing, sometimes the word 'error' is used when 'residual' would be more apt, such as in the phrase 'mean squared error'[^3]. 

With that out of the way, instead of talking about 'drop lines', I can talk about 'residuals'. And instead of taking the absolute sum of these residuals, we're going to sum their squares.

Mathematically speaking, we have some line. If you recall, the formula for a line looks something like:

$$y = mx + b$$

Where $y$ is our dependent variable (in this case, literally `y`, but in the potato example, `yield`), $x$ is our independent variable (here `x`, but in our potato example, `rain`). $m$ is the slope of the line, and $b$ is the y-axis-intercept.


<div class="center">
{{% tell %}}
As a worked example, suppose our line fit (which is not necessarily the *correct* fit) has a slope of 0.5 and an intercept of 2 - that is, $y = 0.5x + 2$:
{{% /tell %}}
{{% show ex_fit-2.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
ex_line_2 = pd.DataFrame({"x":[0,12], "y":[2,8]})
ex_line_2_plt = alt.Chart(ex_line_2).encode(x="x", y="y").mark_line()
ex_fit_2_plt = ex_plt + ex_line_2_plt
ex_fit_2_plt.save('ex_fit-2.svg')
```
{{% /showntellcode %}}

<div class="center">
{{% tell %}}
In this example, there's one point at <span style="color:dodgerblue">(4, 5.79)</span>:
{{% /tell %}}
{{% show ex_ft-pt.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
ft_pt = pd.DataFrame({"x": [4], "y": [5.79]})
ft_pt_plt = alt.Chart(ft_pt).encode(x="x", y="y").mark_circle(
    fill = "dodgerblue", stroke = "dodgerblue", size=100
)
ex_ft_pt_plt = ex_fit_2_plt + ft_pt_plt
ex_ft_pt_plt.save('ex_ft-pt.svg')
```
{{% /showntellcode %}}


<div class="center">
{{% tell %}}
We calculate its residual by first figuring out what the value of y would be given our model (our line):

$$y = 0.5 * (4) + 2 = \textcolor{orangered}4$$
{{% /tell %}}
{{% show ex_pred.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
ft_pred = pd.DataFrame({"x": [4], "y": [4]})
ft_pred_plt = alt.Chart(ft_pred).encode(x="x", y="y").mark_circle(
    fill = "orangered", stroke = "orangered", size=100
)
ex_pred_plt = ex_ft_pt_plt + ft_pred_plt
ex_pred_plt.save('ex_pred.svg')
```
{{% /showntellcode %}}

Conventionally, to distinguish between the actual, <span style = "color: dodgerblue">observed values of y </span> (here 5.79) and the value of <span style="color: orangered">y cranked out by our model</span> (which might be a terrible model, so best not conflate the two), we usually call it "y hat" and give it a hat (ŷ), and say it is a *prediction*[^5] of y. So, while $\textcolor{dodgerblue}{y = 5.79}$, $\textcolor{orangered}{ŷ = 4}$.


<div class="center">
{{% tell %}}
The residual is the difference between the two:
$$\textcolor{dodgerblue}y - \textcolor{orangered}{ŷ} = 5.79 - 4 = 1.79$$
{{% /tell %}}
{{% show ex_res.svg 300px%}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
ft_res = pd.DataFrame({"x": [4], "x2": [4], "y": [4], "y2": [5.79]})
ft_res_plt = alt.Chart(ft_res).encode(x="x", x2="x2", y="y", y2 = "y2").mark_rule()
ex_res_plt = ft_res_plt + ex_pred_plt
ex_res_plt.save('ex_res.svg')
```
{{% /showntellcode %}}



<div class="center">
{{% tell %}}
If we calculate the residuals for every point...
{{% /tell %}}
{{% show ex_ress.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
reses = calc_drop_segment_to_line(ex, ex_line_2)
res_plt = alt.Chart(reses).encode(
    x="x", x2 = "x2", y="y", y2="y2"
).mark_rule()
ex_ress_plt = ex_fit_2_plt + res_plt
ex_ress_plt.save('ex_ress.svg')
```
{{% /showntellcode %}}

Then square them and take the sum, we get some value:

```python
def calc_ss(points, line):
    m = (line.y[1] - line.y[0])/(line.x[1] - line.x[0])
    k = line.y[0] - m * line.x[0]
    y = m * points.x + k
    res = points.y - y
    return sum(res**2)
    
o = calc_ss(ex, ex_line_2)
print(o)
```

```
22.8837
```

So now we have a value. By itself, this means relatively little. However, this value becomes more useful if we use it to compare some other fits.

<div class="center">
{{% tell %}}
For instance, let's consider this pretty terrible fit:
{{% /tell %}}
{{% show bad_ress.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
bad_fit = pd.DataFrame({"x": [0, 12], "y": [4, 1]})
bad_fit_plt = alt.Chart(bad_fit).encode(x="x", y="y").mark_line()
bad_ress = calc_drop_segment_to_line(ex, bad_fit)
drop_lines_plt = alt.Chart(bad_ress).encode(
    x="x", x2 = "x2", y="y", y2="y2"
).mark_rule()
bad_ress_plt = ex_plt + drop_lines_plt + bad_fit_plt
bad_ress_plt.save('bad_ress.svg')
```
{{% /showntellcode %}}

This fit is visually worse, and, as we might expect, its sum of squared residuals is much bigger too:

```python
o2 = calc_ss(ex, bad_fit)
print(o2)
```

```
184.9712
```


<div class="center">
{{% tell %}}
Since we're programming, we can calculate the sum of squares for a variety of slopes and intercepts (also, quick note - I'm using the log of the sum of squares (lss) for color display purposes only):
{{% /tell %}}
{{% show search-space.svg "100%" %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}
```python
def search_space(seq_x, seq_y, data):
    space = pd.DataFrame({
        data.columns[0]: [x for x in seq_x for y in seq_y],
        data.columns[1]: [y for x in seq_x for y in seq_y]
    })
    space["ss"] = [calc_ss(x, data) for x in zip(space.iloc[:, 0], space.iloc[:, 1])]
    space["lss"] = np.log(space["ss"])
    return space

def calc_ss(params, data):
    y = params[1]*data.iloc[:, 0] + params[0]
    res = data.iloc[:, 1] - y
    return sum(res**2)

search_range = np.linspace(-2, 4, 20).round(2)
space = search_space(search_range, search_range, ex)
space_plt = alt.Chart(space).mark_circle(stroke=None, size=70).encode(
    alt.X("x").title("b"), alt.Y("y").title("m"),
    color=alt.Color("lss").scale(scheme="darkgold", reverse=True)
)
space_plt.save("search-space.svg")
```
{{% /showntellcode %}}

Some things to notice:
- The sum of squares seems to be smallest around b = 0, m = 1
- The plot forms a kind of 'funnel' surface

This second point is critical to our application of machine learning, and powers a strategy known as 'gradient descent'. As a brief overview before we dig into it earnestly: gradient descent describes the process in which we find the minimum of the surface. This is important, because it allows us to find the best fit 'automatically'. It also works in much more complex contexts than this. Anywhere we start, we can look at the slope in each dimension and move in the steepest direction downward. Repeated iteratively, we can move closer to the minimum. This, of course, has some caveats, which we'll discuss as we learn about gradient descent more deeply.

# A Gradient Descent into Madness

<div class="center">
{{% tell %}}
Let's orient ourselves. On the following plot, the red dot represents our bad fit:
{{% /tell %}}
{{% show ss_w-bad.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
bad_point_plt = alt.Chart(space).mark_circle(
    stroke = None, color="#f00", size=70
).encode(
    x=alt.datum(4), y=alt.datum(-0.25)
)
ss_w_bad_plt = space_plt + bad_point_plt
ss_w_bad_plt.save("ss_w-bad.svg")
```
{{% /showntellcode %}}

If we fix $b$ at 4 for a moment and just focus on $m$, we can calculate the slope of the line at our the red dot. We can approximate the slope of the line at our point by looking a little bit upstream (+m) and a little bit downstream (-m). Let's say 'a little bit' is 0.01. So,

```python
dy = calc_ss((4, -0.24), ex) - calc_ss((4, -0.26), ex)
dx = -0.24 - -0.26
print(round(dy/dx))
```

```
-485
```

<div class="center">
{{% tell %}}
Ok, so the slope is negative when we go from our current slope (-0.03) to something more positive. We like negative - negative means that our sum of squares is going down, and that means a better fit. We like negative so much, we're going to put an arrow towards the more negative direction to remind ourselves which way it is:
{{% /tell %}}
{{% show "m.svg" 300px %}}
</div>

{{% showntellcode summary="Plotting Code" %}}

```python
m_plt = alt.Chart(space).mark_text(
    size=50, angle=180, stroke = "orangered", fill = "orangered"
).encode(
    x=alt.datum(4), y=alt.datum(-0.25), text=alt.datum("🠃")
)
ss_w_m_plt = space_plt + m_plt
ss_w_m_plt.save("m.svg")
```
{{% /showntellcode %}}

We can also calculate the slope if we hold $m$ constant and vary $b$:

```python
dy = calc_ss((4.01, -0.25), ex) - calc_ss((3.99, -0.25), ex)
dx = 4.01 - 3.99
print(round(dy/dx))
```

```
-55
```

<div class="center">
{{% tell %}}
As before, moving in the positive direction also is a negative slope, so let's put another arrow that way:
{{% /tell %}}
{{% show  "b.svg" 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}

```python
b_plt = alt.Chart(space).mark_text(
    size=50, angle=270, fontWeight=800, stroke = "dodgerblue", fill = "dodgerblue"
).encode(
    x=alt.datum(4),
    y=alt.datum(-0.25),
    text=alt.datum("🠃")
)
ss_w_b_plt = space_plt + m_plt + b_plt
ss_w_b_plt.save("b.svg")
```
{{% /showntellcode %}}

Actually, we can combine the two arrows into a single angled arrow if we do some light trigonometry. The slopes of each tell us the magnitude, and if (after quietly chanting "SOH CAH TOA") we remember that the angle of the arrow is equal to the inverse tangent of the opposite side length divided by the adjacent side length...

```python
round(math.degrees(math.atan(-485/-55)))
```

```
84
```


<div class="center">
{{% tell %}}
So let's just slap a single arrow on there:
{{% /tell %}}
{{% show "mb.svg" 300px%}}
</div>
{{% showntellcode summary = "Plotting Code" %}}
```python
mb_plt = alt.Chart(space).mark_text(
    size=50, angle=270 - 84, stroke = "fuchsia", fill = "fuchsia"
).encode(
    x=alt.datum(4),
    y=alt.datum(-0.25),
    text=alt.datum("🠃")
)
ss_w_mb_plt = space_plt + mb_plt
ss_w_mb_plt.save("mb.svg")
```
{{% /showntellcode %}}

This tiny arrow is a little man pointing you in the direction of better fits. He doesn't know a whole lot - he's never left town, and doesn't know that he's not pointing you towards the absolute minimum - but he's looked around the area a bit and surmises that the way he points is a good start.

So let's follow his directions, why not? The question becomes, for how long should we follow his directions before we get our bearings/ask for directions again? Too soon, and the journey will be incredibly slow - we'll be asking for directions all the time. Too long, and we'll overshoot our goal. There are, of course, many clever tricks for setting this rate just right, as well as changing this rate as you 'follow' - but for the sake of learning, we're going to stick with a single rate the entire time, and just make it kind small. We'll be ok with waiting a bit (although computers are quite fast, so for this simple problem we probably won't have to wait long)

Here will be our general strategy:
1. Start somewhere, figure out the sum of squares at that point.
2. Ask the man for where to go next (mathematicians and less whimsical folks call this 'finding the gradient')
3. Follow that for a distance equal to our learning rate
4. Repeat steps 1-3
5. Stop when we get 'close enough'

We should talk a bit about that last step. Close enough is kind of up to us, but we do need to set a limit, otherwise we'll spiral closer, and closer, and closer to perfection (but alas, never reaching it). Generally, setting 'close enough' should be when our sum of squares values stop changing a whole lot, usually limited by our tastes or time.

<div class="center">
{{% tell %}}
I wrote some code so we can follow our journey from any point, down the gradient, to your stopping point. As an example, this is what gradient descent looks like if we start at our 'bad fit'. For each iteration, the program makes a dot. Towards the end, the dots become very close together, forming almost a line:
{{% /tell %}}
{{% show "with_trace.svg" 300px %}}
</div>

{{% showntellcode summary = "Plotting Code"%}}
```python
def gradient_descent_trace(b, m, data, learning_rate, e, search_space_plt, xlims):
    trace = make_trace(b, m, data, learning_rate, e)
    trace_plt = alt.Chart(trace).mark_circle().encode(
        alt.X("b").scale(domain=xlims),
        y ="m",
        stroke=alt.Stroke("iteration", legend=None).scale(scheme="redblue"),
        fill=alt.Stroke("iteration", legend=None).scale(scheme="redblue")
    )
    return search_space_plt + trace_plt

def make_trace(b, m, data, learning_rate, e):
    coords = [(b, m)]
    while True:
        ss = calc_ss((b, m), data)
        grad = get_gradient(b, m, data)
        b, m = follow(b, m, grad, learning_rate)
        new_ss = calc_ss((b, m), data)
        if abs(ss - new_ss) < e:
            break
        coords.append((b, m))
    trace = pd.DataFrame(coords)
    trace = trace.rename(columns={0:'b', 1:'m'})
    trace["iteration"] = trace.index
    return trace

def get_gradient(b, m, data):
    d = 0.01
    dx = d * 2
    dyb = calc_ss((b+d, m), data) - calc_ss((b-d, m), data)
    dym = calc_ss((b, m+d), data) - calc_ss((b, m-d), data)
    return((dyb/dx, dym/dx))

def follow(b, m, grad, learning_rate):
    new_b = learning_rate * -grad[0] + b
    new_m = learning_rate * -grad[1] + m
    return(new_b, new_m)

with_trace = gradient_descent_trace(4, -0.25, ex, 0.001, 0.000001, space_plt, (-2, 4))
with_trace.save("with_trace.svg")
```
{{% /showntellcode %}}

You can see the points moving down into the 'valley' and then sliding along towards the center, towards the local minimum. So it looks like gradient descent is finding the local minimum, or at least getting close to it. 

Exactly how close, though? We can use vetted linear modeling software to give as a much more precise fit:

```python
fit = LinearRegression().fit(ex.x.values.reshape(-1, 1), ex.y)
b = fit.intercept_.round(2)
m = fit.coef_.round(2)[0]
print(b, m)
```

```
0.7 0.85
```

So it looks like $b = 0.7$ and $m = 0.85$. How did you approximation via gradient descent do?

```python
trace = make_trace(4, -0.25, ex, 0.001, 0.000001)
print(trace.tail(1))
```

```
             b         m  iteration
1454  0.707457  0.850747       1454
```

So it looks like by our 1454th (and final) iteration, $b = 0.71$ and $m = 0.85$. Not too bad!

# So...potatoes

Do you remember when we were still talking about potatoes, and possibly happiness? We got a little sidetracked, but as a quick recap, here's what we learned:

1. How we measure what a 'good fit' is (the sum squared the residuals)
2. One way to find the best fit (gradient descent)[^4]

We can apply the same strategy to our potato data - first, find out what the actual slope and intercept is:

```python
tatos = tatos.rename(columns={'rain':'x', 'yield':'y'})
fit_tatos = LinearRegression().fit(tatos.x.values.reshape(-1, 1), tatos.y)
b = fit_tatos.intercept_.round(2)
m = fit_tatos.coef_.round(2)[0]
print(b, m)
```

```
5.02 20.8
```

As a reminder, this means that the intercept is $b = 5.02$ and slope is $m = 20.8$

<div class="center">
{{% tell %}}
And now I'll make a sum of squares plot roughly centered around the solution. It's not structly necessary, but it sure is fun:
{{% /tell %}}
{{% show search-space_tatos.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}
```python
search_range_rain = np.linspace(-30, 30, 20).round(2)
search_range_yield = np.linspace(-10, 50, 20).round(2)
space = search_space(search_range_rain, search_range_yield, tatos)
space_plt = alt.Chart(space).mark_circle(stroke=None, size=70).encode(
    alt.X("x").title("rain"), alt.Y("y").title("yield"),
    color=alt.Color("lss").scale(scheme="darkgold", reverse=True)
)
space_plt.save("search-space_tatos.svg")
```
{{% /showntellcode %}}


<div class="center">
{{% tell %}}
Now, we use gradient descent to find intercept and slope. We'll start our journey at $b = 0$ and $m = 0$ - our stopping error and our learning rate will stay the same:
{{% /tell %}}
{{% show tatos_trace.svg 300px %}}
</div>
{{% showntellcode summary = "Plotting Code" %}}
```python
tatos_trace_plt = gradient_descent_trace(0, 0, tatos, 0.001, 0.000001, space_plt, (-30, 30))
tatos_trace_plt.save("tatos_trace.svg")
```
{{% /showntellcode %}}

What's funny about this one is it appears to kind of oscillate across the 'canyon' before eventually settling down into the local minimum. We can also check to see how many iterations it took to get there, and what it eventually settled on:

```python
tato_trace = make_trace(0, 0, tatos, 0.001, 0.000001)
print(tato_trace.tail(1))
```

```
            b          m  iteration
264  5.020995  20.798555        264
```

And it looks like we got pretty dang close!

Before we close out, let's consider the practical implications of our line fitting. This tells us that - if this model is correct - with 0 inches of rain, we would still get a yield of 5 potatoes (that is, the y-intercept $b$ is ~5). It also tells us that with each additional inch of rain, we can expect about 21 more potatoes (that is, the slope of the line $m$ is ~21).

# Wrap up
It was a long road to get there, but we've set up some of the fundamentals for machine learning. We were able to determine (using gradient descent) what the equation for the best line fit was for our potato data (at least, best in terms of the metrics we decided - ordinary least squares). Using this fit, we revealed a bit about the nature of the relationship between rain and potato crop yield. Practically, this might allow us to forecast how many potatoes a year with, say, 2 inches of rain will yield.

In the next post, which will hopefully be shorter, we'll extend this concept to more dimensions.

# Sources
Ordinary least squares: 
- https://en.wikipedia.org/wiki/Ordinary_least_squares

Predict vs estimate: 
- https://stats.stackexchange.com/questions/17773/what-is-the-difference-between-estimation-and-prediction

Programming machine learning by Paolo Perrotta
- Excellent, easy, python based introduction to machine learning

Introduction to Statistical Learning:
- https://www.statlearning.com/


[^1]: Now is a good time to tell you that I know nothing about growing potatoes, rain (I am from the desert), and the interaction of potato growth and rain. I am regretting choosing this example but do you know how hard it is to hit a backspace key
[^2]: I'm using new example data because when I show orthogonal lines, I want to emphasize that they touch the line at a right angle, which only works if the units on the x-axis and y-axis are displayed at the same physical scale. Since the rain and yield data are on largely different scales (ie, rain is roughly 10x less than yield), I'd either have to display it verrrrrrrry tall, or the orthogonal lines wouldn't look orthogonal. Hence the more well-behaved example data.
[^3]: For additional information, Wikipedia explains the difference between residuals and errors quite beautifully in the [article on errors and residuals](https://en.wikipedia.org/wiki/Errors_and_residuals).
[^4]: It feels important to note that linear modeling usually never uses gradient descent - it's much less efficient than things like using matrix algebra in [linear least squares](https://en.wikipedia.org/wiki/Linear_least_squares#Fitting_a_line)
[^5]: A prediction is different from an *estimation*. An estimation, as I understand, is the attempt to measure some intrinsic property of a variable - its mean, for instance - while a prediction is interested in spinning up a new hypothetical observation, given some parameters, with the goal of being as close to reality as possible. In my mind, estimation feels more like a summary process, while prediction feels more 'creative' (that is, it is creating new values)

