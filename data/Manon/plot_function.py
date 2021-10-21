from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from itertools import cycle
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
from math import log10, floor
import sortednp as snp
import numpy as np

import warnings

def legend_modulus(ax, loc='lower right', second_legend=False, bbox_to_anchor=0):
    handles = [mpl.lines.Line2D([], [], c='k', label=r'$\mathrm{loss~modulus}$'),
              mpl.lines.Line2D([], [], c='k', mfc='k', label=r'$\mathrm{storage~modulus}$')]


    if second_legend :

        if bbox_to_anchor != 0:
            legend = plt.legend(handles=handles, loc=loc, bbox_to_anchor=bbox_to_anchor)
            ax.add_artist(legend)
        else:
            legend = plt.legend(handles=handles, loc=loc)
            ax.add_artist(legend)
    else:
        if bbox_to_anchor != 0:
            ax.legend(loc=loc, handles=handles, bbox_to_anchor=bbox_to_anchor)
        else :
            ax.legend(loc=loc, handles=handles)

def annotate_crit_shear_rates(ax, gammadotc, etas, tauc_TC, position_txt=0.6):
    gammadot2 = tauc_TC / etas
    ax.axvline(gammadotc, c='green', ls='--', marker='')
    ax.axvline(gammadot2, c='purple', ls='--', marker='')
    ax.annotate(r'$\dot{\gamma}_\mathrm{c}$', xy=(gammadotc, position_txt), c='g',
                xycoords=('data', 'axes fraction'), backgroundcolor='w', ha='center')
    ax.annotate(r'$\sigma_{\mathrm{y}} / \eta_\infty$', xy=(gammadot2, position_txt), c='purple',
                xycoords=('data', 'axes fraction'), backgroundcolor='w', ha='center')

def get_crit_shear_rates(df_fit, sample_id, T):
    df_fith = df_fit[(df_fit.sample_ID == sample_id) & (df_fit.temperature == T)]
    gammadotc = float(df_fith['gamma_dotc'])
    tauc_TC = float(df_fith['tauc_TC'])
    etas = float(df_fith['etas'])
    return gammadotc, tauc_TC, etas

def title_fig(microgel_type, solvant, T, wp=None):
    if wp == None:
        return str(microgel_type) + '_in_' + str(solvant) + '_T' + str(T)
    else :
        return microgel_type + '_' + str(wp).replace('.', 'p') + '_in_' + solvant + '_T' + str(T)

def label_sample(micorgel_type, solvant, T):
    return str(microgel_type) + '~in~' + str(solvant) + '~T' + str(T)

def write_sample_info(ax, microgel_type, T, solvant, w_percent=None):
    if w_percent == None:
        ax.text(0, 1.1, r'$\mathrm{T}~' + str(T) + '^\circ \mathrm{C}~~~~\mathrm{' + microgel_type + '}~\mathrm{in~' + solvant + '} $', va='center', transform=ax.transAxes)
    else:
        ax.text(0, 1.1, r'$\mathrm{T}~' + str(T) + '^\circ \mathrm{C}~~~~\mathrm{' + microgel_type + '}~' + str(w_percent) + '~\%~~~~\mathrm{in~' + solvant + '} $', va='center', transform=ax.transAxes)

def merge_physical_data(x1, x2, y1, y2):
    # Create the variable if they don't exist yet
    try:
        x1
    except NameError:
        x1 = np.array([])
    try:
        y1
    except NameError:
        y1 = np.array([])
    # Change datatype in given arrays in case there are ints or stuff
    x1 = np.asarray(x1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    y1 = np.asarray(y1, dtype=float)
    y2 = np.asarray(y2, dtype=float)
    # The merge and sort action for x
    merged_x, ind = snp.merge(x1, x2, indices = True)
    # The merge and sort action for y
    ind_1 = ind[0]
    ind_2 = ind[1]
    merged_y = np.zeros(len(merged_x))
    count_1 = 0
    count_2 = 0
    for i in range(0, len(merged_x)):
        if i in ind_1:
            merged_y[i] = y1[count_1]
            count_1 += 1
        elif i in ind_2:
            merged_y[i] = y2[count_2]
            count_2 += 1
    return merged_x, merged_y

def round_physical(x, err_x):
    n = int(floor(log10(abs(err_x))))
    return round(x, -n), round(err_x, -n)

def round_significative(x):
    return round(x, -int(floor(log10(abs(x)))))

def create_plot(two_sided=False, colors = ['#6F4C9B', '#5568B8', '#4D8AC6',
               '#60AB9E', '#77B77D', '#A6BE54',
               '#D1B541', '#E49C39', '#DF4828', '#990D38'], markers = ['o', 'v', '^', 's', 'D', '*'], figsize=(5, 3.4)):
    """
    Crée un environnement de plot

    Parameters
    ----------
    twosided : bool
        allows to change the size of the figure accordingly.
    colors : list of strings
        a default list exists but this allows to change it if u want
    markers : list of strings
        a default list of markers exists, but u can change it if needed
    Returns
    -------
    fig, ax : matplotlib objects to be used as normal

    """
    color = cycle(colors)
    marker = cycle(markers)
    if two_sided :
        fig = plt.figure(figsize=(3.4, 3.4))
    else :
        fig = plt.figure(figsize=figsize)
    # The first & third items are for padding and the second items are for the
    # axes. Sizes are in inches.
    h = [Size.Fixed(1.0), Size.Scaled(1.), Size.Fixed(.2)]
    v = [Size.Fixed(0.7), Size.Scaled(1.), Size.Fixed(.5)]

    divider = Divider(fig, (0.0, 0.0, 1., 1.), h, v, aspect=False)
    # the width and height of the rectangle is ignored.

    ax = Axes(fig, divider.get_position())
    ax.set_axes_locator(divider.new_locator(nx=1, ny=1))

    fig.add_axes(ax)
    return fig, ax, color, marker

def get_fit_amp_sweep(x, y, graph=True):
    warnings.simplefilter("ignore")
    x = x[:, np.newaxis]
    # Fit Ransac
    ransac = sklearn.linear_model.RANSACRegressor(residual_threshold=x.std()/20,
                                                  base_estimator = sklearn.linear_model.LinearRegression(positive=True))
    ransac.fit(x[:], y[:])
    pente = ransac.estimator_.coef_[0]
    while pente != 0:
        ransac.fit(x[:], y[:])
        pente = ransac.estimator_.coef_[0]
    inlier_mask = ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)
    # Prédiction des deux fits
    line_X = np.linspace(x.min(), x.max(), 100)
    line_X = line_X[:, np.newaxis]
    line_y_ransac = ransac.predict(line_X)



    if graph:
        #print("R²")
        #print(ransac.estimator_.score(line_X, line_y_ransac))
        y0 = ransac.estimator_.intercept_
        slop = ransac.estimator_.coef_[0]

        print("Ordonnée à l'origine", y0)
        print("Pente", slop)
        lw = 1
        plt.scatter(x[inlier_mask], y[inlier_mask], color='yellowgreen', marker='.',
                    label='Inliers')
        plt.scatter(x[outlier_mask], y[outlier_mask], color='gold', marker='.',
                    label='Outliers')
        #plt.plot(line_X, line_y_ransac, color='cornflowerblue', linewidth=lw,
        # label='RANSAC regressor')
        plt.plot(np.linspace(x[0], x[-1], 20),
                y0 + slop * np.linspace(x[0], x[-1], 20),
                lw=1, ls='-', color='teal', label='yo', marker='')
        plt.legend(bbox_to_anchor=(1.1, 1.1))._legend_box.align='left'
        plt.xscale('log')
        plt.yscale('log')
        #plt.xlabel(r'$p~\mathrm{(m)}$')
        #plt.ylabel(r'$F~\mathrm{(N)}$')
        #plt.title('V = ' + str(V))
        return y0, slop


def get_fit_end_recover(x, y, graph=True):
    #warnings.simplefilter("ignore")
    x = x[:, np.newaxis]
    # Fit Ransac
    ransac = sklearn.linear_model.RANSACRegressor(residual_threshold=x.std()/20,
                                                  base_estimator = sklearn.linear_model.LinearRegression(positive=True))
    ransac.fit(x[:], y[:])
    pente = ransac.estimator_.coef_[0]
    inlier_mask = ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)
    # Prédiction des deux fits
    line_X = np.linspace(x.min(), x.max(), 100)
    line_X = line_X[:, np.newaxis]
    line_y_ransac = ransac.predict(line_X)
    y0 = ransac.estimator_.intercept_
    slop = ransac.estimator_.coef_[0]
    return y0, slop
