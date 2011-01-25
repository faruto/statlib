from datetime import datetime
import numpy as np
import re
import pandas as pn

import statlib.dlm as dlm
reload(dlm)
from statlib.dlm import *

def load_table():
    path = 'westharrison/data/Table3.3.data.txt'
    sep = '\s+'

    lines = [re.split(sep, l.strip()) for l in open(path)]

    y_data = []
    f_data = []
    saw_f = False
    for line in lines:
        if line[0] == 'Y':
            continue
        elif line[0] == 'F':
            saw_f = True
            continue

        # drop year
        if saw_f:
            f_data.extend(line[1:])
        else:
            y_data.extend(line[1:])

    y_data = np.array(y_data, dtype=float)
    f_data = np.array(f_data, dtype=float)

    dates = pn.DateRange(datetime(1975, 1, 1), periods=len(y_data),
                         timeRule='Q@MAR')

    Y = pn.Series(y_data, index=dates)
    F = pn.Series(f_data, index=dates)

    return Y, F

def ex_310():
    y, x = load_table()

    discount_factors = np.arange(0.05, 1.01, 0.05)

    rows, columns = 3, 3
    rng = y.index

    rmse = []
    mad = []
    like = []
    var_est = []
    pred_var = []

    fig, axes = plt.subplots(3, 3, sharey=True, figsize=(12, 12))

    for i, disc in enumerate(discount_factors):
        model = dlm.DLM(y, x, mean_prior=mean_prior,
                        var_prior=var_prior, discount=disc)

        rmse.append(model.rmse)
        mad.append(model.mad)
        like.append(model.pred_like)

        var_est.append(model.var_est[-1])
        pred_var.append(model.var_est[-1] + model.mu_scale[-1] / disc)

        continue
        ax = axes[i / rows][i % rows]

        # plot posterior
        model.plot_mu(prior=False, ax=ax)

        ax.set_title(str(disc))
        ax.set_ylim([0.4, 0.48])

    like = np.array(like).prod(axis=1)
    llr = np.log(like / like[-1])

    fig = plt.figure(figsize=(12, 12))

    ax1 = fig.add_subplot(311)
    ax1.plot(discount_factors, rmse, label='RMSE')
    ax1.plot(discount_factors, mad, label='MAD')
    ax2 = fig.add_subplot(312)
    ax2.plot(discount_factors, llr, label='LLR')
    ax1.legend()
    ax2.legend()

    # plot s_42 and q_42
    ax3 = fig.add_subplot(313)
    ax3.plot(discount_factors, var_est, label='S')
    ax3.plot(discount_factors, pred_var, label='Q')
    ax3.legend()

if __name__ == '__main__':
    y, x = load_table()

    mean_prior = (0.45, 0.0025)
    var_prior = (1, 1)

    model = DLM(y, x, mean_prior=mean_prior,
                var_prior=var_prior, discount=0.9)
