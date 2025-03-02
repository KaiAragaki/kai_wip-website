import pandas as pd
import numpy as np
import altair as alt
from sklearn.linear_model import LinearRegression
from kai_theme import kai # noqa: F401

np.random.seed(1)

def make_potato_data(n):
    e = np.random.normal(0, scale=20, size=n)
    rain = (np.random.beta(a=2, b=4, size=n) * 10).round(2)
    potatoes = (23.2 * rain - 3 + e).clip(0).round()
    return pd.DataFrame({"rain": rain, "yield": potatoes})

tatos = make_potato_data(50)

tatos_plt = alt.Chart(tatos).encode(x="rain", y="yield").mark_circle()
tatos_plt.save('tatos.svg')

bad_fit = pd.DataFrame({'rain': [0,10], 'yield': [150, 100]})
bad_fit_plt = alt.Chart(bad_fit).encode(x="rain", y="yield").mark_line()
tatos_bad_fit_plt = tatos_plt + bad_fit_plt
tatos_bad_fit_plt.save('tatos_bad_fit.svg')

ok_fit = pd.DataFrame({'rain': [0,10], 'yield': [50, 150]})
ok_fit_plt = alt.Chart(ok_fit).encode(x="rain", y="yield").mark_line()
tatos_ok_fit_plt = tatos_plt + ok_fit_plt
tatos_ok_fit_plt.save('tatos_ok_fit.svg')

def create_example_data(n):
    x = range(1, n+1)
    y = x + np.random.normal(0, 1, n)
    y = y.round(2)
    return pd.DataFrame({"x": x,"y": y})

ex = create_example_data(10)

ex_plt = alt.Chart(ex).encode(
    x=alt.X("x", scale = alt.Scale(domain=(0,12)), title = "x"),
    y=alt.Y("y", scale = alt.Scale(domain=(0,12)), title = "y")
).mark_circle()
ex_plt.save('ex.svg')

ex_line = pd.DataFrame({"x":[0,12], "y":[4,8]})
ex_line_plt = alt.Chart(ex_line).encode(x="x", y="y").mark_line()
ex_rand_fit_plt = ex_plt + ex_line_plt
ex_rand_fit_plt.save('ex_rand_fit.svg')

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

ex_line_2 = pd.DataFrame({"x":[0,12], "y":[2,8]})
ex_line_2_plt = alt.Chart(ex_line_2).encode(x="x", y="y").mark_line()
ex_fit_2_plt = ex_plt + ex_line_2_plt
ex_fit_2_plt.save('ex_fit-2.svg')

ft_pt = pd.DataFrame({"x": [4], "y": [5.79]})
ft_pt_plt = alt.Chart(ft_pt).encode(x="x", y="y").mark_circle(
    fill = "dodgerblue", stroke = "dodgerblue", size=100
)
ex_ft_pt_plt = ex_fit_2_plt + ft_pt_plt
ex_ft_pt_plt.save('ex_ft-pt.svg')

ft_pred = pd.DataFrame({"x": [4], "y": [4]})
ft_pred_plt = alt.Chart(ft_pred).encode(x="x", y="y").mark_circle(
    fill = "orangered", stroke = "orangered", size=100
)
ex_pred_plt = ex_ft_pt_plt + ft_pred_plt
ex_pred_plt.save('ex_pred.svg')

ft_res = pd.DataFrame({"x": [4], "x2": [4], "y": [4], "y2": [5.79]})
ft_res_plt = alt.Chart(ft_res).encode(x="x", x2="x2", y="y", y2 = "y2").mark_rule()
ex_res_plt = ft_res_plt + ex_pred_plt
ex_res_plt.save('ex_res.svg')

reses = calc_drop_segment_to_line(ex, ex_line_2)
res_plt = alt.Chart(reses).encode(
    x="x", x2 = "x2", y="y", y2="y2"
).mark_rule()
ex_ress_plt = ex_fit_2_plt + res_plt
ex_ress_plt.save('ex_ress.svg')

def calc_ss(points, line):
    m = (line.y[1] - line.y[0])/(line.x[1] - line.x[0])
    k = line.y[0] - m * line.x[0]
    y = m * points.x + k
    res = points.y - y
    return sum(res**2)

o = calc_ss(ex, ex_line_2)
print(o)

bad_fit = pd.DataFrame({"x": [0, 12], "y": [4, 1]})
bad_fit_plt = alt.Chart(bad_fit).encode(x="x", y="y").mark_line()
bad_ress = calc_drop_segment_to_line(ex, bad_fit)
drop_lines_plt = alt.Chart(bad_ress).encode(
    x="x", x2 = "x2", y="y", y2="y2"
).mark_rule()
bad_ress_plt = ex_plt + drop_lines_plt + bad_fit_plt
bad_ress_plt.save('bad_ress.svg')

o2 = calc_ss(ex, bad_fit)
print(o2)

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

bad_point_plt = alt.Chart(space).mark_circle(
    stroke = None, color="#f00", size=70
).encode(
    x=alt.datum(4), y=alt.datum(-0.25)
)
ss_w_bad_plt = space_plt + bad_point_plt
ss_w_bad_plt.save("ss_w-bad.svg")

dy = calc_ss((4, -0.24), ex) - calc_ss((4, -0.26), ex)
dx = -0.24 - -0.26
print(round(dy/dx))

m_plt = alt.Chart(space).mark_text(
    size=50, angle=180, stroke = "orangered", fill = "orangered"
).encode(
    x=alt.datum(4), y=alt.datum(-0.25), text=alt.datum("🠃")
)
ss_w_m_plt = space_plt + m_plt
ss_w_m_plt.save("m.svg")

dy = calc_ss((4.01, -0.25), ex) - calc_ss((3.99, -0.25), ex)
dx = 4.01 - 3.99
print(round(dy/dx))

b_plt = alt.Chart(space).mark_text(
    size=50, angle=270, fontWeight=800, stroke = "dodgerblue", fill = "dodgerblue"
).encode(
    x=alt.datum(4),
    y=alt.datum(-0.25),
    text=alt.datum("🠃")
)
ss_w_b_plt = space_plt + m_plt + b_plt
ss_w_b_plt.save("b.svg")

round(math.degrees(math.atan(-485/-55)))

mb_plt = alt.Chart(space).mark_text(
    size=50, angle=270 - 84, stroke = "fuchsia", fill = "fuchsia"
).encode(
    x=alt.datum(4),
    y=alt.datum(-0.25),
    text=alt.datum("🠃")
)
ss_w_mb_plt = space_plt + mb_plt
ss_w_mb_plt.save("mb.svg")

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

fit = LinearRegression().fit(ex.x.values.reshape(-1, 1), ex.y)
b = fit.intercept_.round(2)
m = fit.coef_.round(2)[0]
print(b, m)

trace = make_trace(4, -0.25, ex, 0.001, 0.000001)
print(trace.tail(1))

tatos = tatos.rename(columns={'rain':'x', 'yield':'y'})
fit_tatos = LinearRegression().fit(tatos.x.values.reshape(-1, 1), tatos.y)
b = fit_tatos.intercept_.round(2)
m = fit_tatos.coef_.round(2)[0]
print(b, m)

search_range_rain = np.linspace(-30, 30, 20).round(2)
search_range_yield = np.linspace(-10, 50, 20).round(2)
space = search_space(search_range_rain, search_range_yield, tatos)
space_plt = alt.Chart(space).mark_circle(stroke=None, size=70).encode(
    alt.X("x").title("rain"), alt.Y("y").title("yield"),
    color=alt.Color("lss").scale(scheme="darkgold", reverse=True)
)
space_plt.save("search-space_tatos.svg")

tatos_trace_plt = gradient_descent_trace(0, 0, tatos, 0.001, 0.000001, space_plt, (-30, 30))
tatos_trace_plt.save("tatos_trace.svg")

tato_trace = make_trace(0, 0, tatos, 0.001, 0.000001)
print(tato_trace.tail(1))
