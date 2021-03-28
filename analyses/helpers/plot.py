import datetime
from tempfile import NamedTemporaryFile

import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.transforms as transforms
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta, weekday
from matplotlib import lines
from matplotlib.image import imread
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter

# https://davidmathlogic.com/colorblind/#%23648FFF-%23785EF0-%23DC267F-%23FE6100-%23FFB000
colorblind_tong = ['#009E73',
                   '#E69F00',
                   '#0072B2',
                   '#D55E00']

colorblind_tol = ['#117733',  # #44AA99
                  '#88CCEE',
                  '#E69F00',
                  '#882255'
                  ]
colorblind_ibm = ['#648FFF',  # blue
                  # '#785EF0', # purple
                  '#DC267F',  # magenta
                  '#FE6100',  # orange
                  '#FFB000']  # yellow

colorblind_green = '#009E73'
colorblind_red = '#D55E00'


def get_size(fig, dpi=100):
    with NamedTemporaryFile(suffix='.png') as f:
        fig.savefig(f.name, bbox_inches='tight', dpi=dpi)
        height, width, _channels = imread(f.name).shape
        return width / dpi, height / dpi


def set_size(fig, size, dpi=100, eps=1e-2, give_up=2, min_size_px=10):
    target_width, target_height = size
    set_width, set_height = target_width, target_height  # reasonable starting point
    deltas = []  # how far we have
    while True:
        fig.set_size_inches([set_width, set_height])
        actual_width, actual_height = get_size(fig, dpi=dpi)
        set_width *= target_width / actual_width
        set_height *= target_height / actual_height
        deltas.append(abs(actual_width - target_width) + abs(actual_height - target_height))
        if deltas[-1] < eps:
            return True
        if len(deltas) > give_up and sorted(deltas[-give_up:]) == deltas[-give_up:]:
            return False
        if set_width * dpi < min_size_px or set_height * dpi < min_size_px:
            return False


def plot_dates(ax, start, end, x, y, xticklabels=True, ls="solid", adjust=False, sci=True, color='#377eb8'):
    start = datetime.datetime.strptime(str(start), "%Y%m%d")
    end = datetime.datetime.strptime(str(end), "%Y%m%d")

    if adjust is not False:
        start = start + relativedelta(weekday=adjust[0])
        end = end + relativedelta(weekday=adjust[1])

    mask = (x <= end) & (x >= start)

    ax.plot(x[mask], y[mask], ls=ls, color=color)

    if not xticklabels:
        ax.set_xticklabels([])
        ax.tick_params(axis='x', labeltop=False, top=False, bottom=False)
    else:
        months_fmt = mdates.DateFormatter('%b')
        ax.xaxis.set_major_formatter(months_fmt)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    if sci:
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    return weekday(start.weekday()), weekday(end.weekday())


def plot_intervention(ax, interventions, lang, intervention, interventions_helper, int_ls, int_c, th=2, size=9):
    xsint = []

    trans = transforms.blended_transform_factory(
        ax.transData, ax.transAxes)
    if intervention == "all":
        if lang not in interventions:
            print(f'No interventions for {lang} loaded.')
        else:
            for key in interventions[lang].keys():
                try:
                    if key == "Mobility":
                        ax.axvline(interventions[lang][key], alpha=1, color="black", ls="--", lw=1.5)
                    else:
                        ax.axvline(interventions[lang][key], alpha=0.3, color=int_c[key], ls=int_ls[key])
                except:
                    continue
                delta = 0
                for x in xsint:
                    diff = (abs((interventions[lang][key] - x).total_seconds() // (24 * 60 * 60)))
                    if diff < th:
                        delta += 0.2

                plt.text(interventions[lang][key], 1.02 + delta, interventions_helper[key],
                         transform=trans, ha='center', size=size)
                xsint.append(interventions[lang][key])

    else:
        ax.axvline(interventions[lang][intervention], alpha=0.3)
        plt.text(interventions[lang][intervention], 1.02, interventions_helper[intervention],
                 transform=trans, ha='center', size=size)


def plot_interventions(agg, helper_langs, interventions, interventions_helper, codes, dates, labels, lines_params,
                       getters, title, sci=True, rows=5, cols=3, figsize=(14, 6)):
    fig, ax = plt.subplots(rows, cols,
                           figsize=figsize,
                           sharex=True,
                           gridspec_kw={"hspace": 0.8,
                                        "top": 0.8})

    axs = ax.flatten()

    if len(getters) == 1:
        getters = getters * len(dates)

    plot_idx = 0
    for idx, code in enumerate(codes):
        if code not in agg:
            plot_idx -= 1

            continue
        # print(code)
        idy = 0
        for date, line_params, get_val in zip(dates, lines_params, getters):
            x = get_val(code, agg)
            if idy == 0:
                start, end = plot_dates(axs[idx + plot_idx], date[0], date[1], x.index, x.values, sci=sci)
            else:
                plot_dates(axs[idx + plot_idx].twiny(), date[0], date[1], x.index, x.values,
                           xticklabels=False, ls=line_params, adjust=(start, end), sci=sci)
            idy += 1
        axs[idx + plot_idx].set_title(helper_langs[code], pad=17)
        plot_intervention(axs[idx + plot_idx], interventions, code, "all", interventions_helper, int_ls, int_c)

    lines = [Line2D([0], [0], color="Blue", lw=1.5, ls=l) for l in lines_params]

    axs[0].legend(
        handles=lines,
        labels=labels,
        loc='upper center', bbox_to_anchor=(0.9, 2.2),
        ncol=3, fancybox=False, shadow=False,
        frameon=False, edgecolor=None, fontsize=13
    )

    axs[1].legend(
        handles=[Line2D([0], [0], visible=False)] * len(interventions_helper),
        labels=["{}: {}".format(v, k) for k, v in interventions_helper.items()],
        loc='upper center', bbox_to_anchor=(0.9, 2.2),
        ncol=round(len(interventions_helper) / 2), fancybox=False, shadow=False,
        frameon=False, edgecolor=None, fontsize=8
    )

    fig.suptitle(title, fontsize=18)

    set_size(fig, (14, 7.5))
    # plt.show()
    return fig


def plot_diff_in_diff_coefficients(codes_order, list_df_diff_in_diffs, xlabel, title, sub_titles, x_range=1,
                                   fig_size=(10, 8), p_val=0.05):
    num_plots = len(list_df_diff_in_diffs)
    fig, axes = plt.subplots(num_plots, 1, figsize=fig_size, sharex="col",
                             gridspec_kw={"hspace": 0.15, "wspace": 0.05, "top": 0.9, "bottom": 0.15,
                                          "height_ratios": [11 / 42] * num_plots})

    # axes = [axes[0, 1], axes[1, 1], axes[2, 1], axes[3, 1], axes[0, 0], axes[1, 0], axes[2, 0], axes[3, 0]]

    # plot_diffs_in_diffs(df_pageviews_results, codes_order, axes[0])
    #

    for i, df_diff in enumerate(list_df_diff_in_diffs):
        plot_diffs_in_diffs(df_diff, codes_order, axes[i])

    for i, ax in enumerate(axes):  # [:4]:
        ax.axvline(0, zorder=0, color="black", ls="-", alpha=0.3)
        ax.set_xlim([-x_range, x_range])
        ax.set_xticks([-x_range, -round(x_range / 2, 2), 0, round(x_range / 2, 2), x_range])
        ax.yaxis.tick_right()
        ax.set_ylabel(sub_titles[i])
    axes[-1].set_xlabel(xlabel, size=14)

    axes[0].set_title(title, size=16)

    lines = [
        Line2D([0], [0], color="black", lw=0, marker="x"),
    ]

    axes[0].legend(
        handles=lines,
        labels=[  # "Desktop",
            f"p $>$ {p_val}"],
        loc='upper left', bbox_to_anchor=(-0.01, 1),
        ncol=num_plots, fancybox=True, shadow=False,
        frameon=False, edgecolor=None, fontsize=12,
        borderaxespad=0
    )
    set_size(fig, fig_size)
    # fig.savefig("/scratch/horta/coronawiki/images/diffs_in_diffs_all.pdf", bbox_inches="tight")
    return fig


def plot_dates_ci(ax, start, end, ci, sci=True, real=True, col="preds", fill=True):
    x = ci.inferences.index
    x_pre = ci.pre_data.index
    start = datetime.datetime.strptime(str(start), "%Y%m%d")
    end = datetime.datetime.strptime(str(end), "%Y%m%d")
    mask = (x <= end) & (x >= start)
    mask_pre = (x_pre <= end) & (x_pre >= start)

    if fill:
        ax.fill_between(ci.inferences[mask].index,
                        ci.inferences[mask]["{}_lower".format(col)],
                        ci.inferences[mask]["{}_upper".format(col)],
                        alpha=0.4)
    ax.plot(ci.inferences[mask].index, ci.inferences[mask][col])

    if real:
        ax.plot(ci.pre_data[mask_pre], color="black", ls="--")
        ax.plot(ci.post_data, color="black", ls="--")

    months_fmt = mdates.DateFormatter('%b')
    ax.xaxis.set_major_formatter(months_fmt)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.axvline(ci.pre_data.index[-1], color="black", ls=":", lw=3)

    if sci:
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))


def plot_cumm_diff(ax, baseline, starts, ends, x, y, xticklabels=True, ls="-", color="#377eb8"):
    start_pre = datetime.datetime.strptime(str(starts[0]), "%Y%m%d")
    end_pre = datetime.datetime.strptime(str(ends[0]), "%Y%m%d")

    start_pos = datetime.datetime.strptime(str(starts[1]), "%Y%m%d")
    end_pos = datetime.datetime.strptime(str(ends[1]), "%Y%m%d")

    start_baseline = datetime.datetime.strptime(str(baseline[0]), "%Y%m%d")
    end_baseline = datetime.datetime.strptime(str(baseline[1]), "%Y%m%d")

    mask_pre = (x <= end_pre) & (x >= start_pre)
    mask_pos = (x <= end_pos) & (x >= start_pos)
    mask_baseline = (x <= end_baseline) & (x >= start_baseline)
    baseline = np.mean(y[mask_baseline])

    if not xticklabels:
        ax.set_xticklabels([])
        ax.tick_params(axis='x', labeltop=False, top=False, bottom=False)
    else:
        months_fmt = mdates.DateFormatter('%b')
        ax.xaxis.set_major_formatter(months_fmt)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
    cum = (y[mask_pos] - y[mask_pre]).cumsum() / baseline
    print(max(cum))
    print(min(cum))
    ax.plot(x[mask_pos], cum, ls=ls, color=color)


def plot_diffs_in_diffs_interventions(df_results, intervention_order, ax):
    idx = 0
    labels = []
    for intervention in intervention_order:
        row = df_results[(df_results.intervention == intervention)].iloc[0]
        row = dict(row)
        row = dict(row)

        # desktop ci
        ax.plot([row["low"], row["high"]], [idx, idx], color="#e41a1c", zorder=1)

        # desktop mean
        marker = "." if row["pval"] else "x"
        ax.scatter([row["val"]], [idx], color="black", marker=marker, zorder=2)
        ax.axhline(idx + 0.5, lw=0.5, ls=":", color='black', alpha=0.5)

        idx += 1
        labels.append(intervention.replace("Public e", "E"))
    _ = ax.set_yticks(range(0, idx))
    _ = ax.set_ylim([-0.5, 6.5])
    _ = ax.set_yticklabels(labels)


def plot_diffs_in_diffs_all(df_results, codes_order, ax, helper_langs, mobile=True):
    df_results = df_results.reset_index(drop=True)

    idx = 0
    labels = []
    for code in codes_order[::-1]:

        row = df_results[df_results.lang == code].iloc[0]
        row = dict(row)

        if mobile:
            row_m = df_results[df_results.lang == code + ".m"].iloc[0]
            row_m = dict(row_m)

        # desktop ci
        ax.plot([row["low"], row["high"]], [idx, idx], color="#e41a1c", zorder=1)

        # mobile ci
        if mobile:
            ax.plot([row_m["low"], row_m["high"]], [idx + 0.15, idx + 0.15], color="#377eb8", zorder=1)

        # desktop mean
        marker = "." if row["pval"] else "x"
        ax.scatter([row["val"]], [idx], color="black", marker=marker, zorder=2)

        # mobile mean
        if mobile:
            marker = "." if row_m["pval"] else "x"
            ax.scatter([row_m["val"]], [idx + 0.15], color="black", marker=marker, zorder=2)

        ax.axhline(idx + 0.5, lw=0.5, ls=":", color='black', alpha=0.5)

        idx += 1
        labels.append(helper_langs[row["lang"]])

        _ = ax.set_yticks(range(0, idx))
        _ = ax.set_yticklabels(labels)

        ax.set_ylim([-0.5, 11.5])
