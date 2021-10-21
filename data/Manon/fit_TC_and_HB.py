import numpy as np
from plot_function import create_plot, round_physical, merge_physical_data
from scipy.optimize import curve_fit
import math
import matplotlib as mpl
import pandas as pd
import yaml
from math import log10, floor
import matplotlib.pyplot as plt
mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'




# define HB model
def HB(x, tauy, K, n):
     return tauy + K*x**n
# define TC model
def TC(x, tauy, gamma_dotc, etas):
    return tauy + tauy*((x / gamma_dotc)**0.5) + etas * x


def fit_TC_HB(df, sample_ID, T, plot=True, replace=False):
    """
    Cette fonction permet de fitter les données d'un dataframe par les deux modèles HB et TC
    Elle prend en entrée :
        df : dataframe
        sample_ID : entier qui correspond à l'échantillon visé
        T : température
    Elle retourne :



    """

    with open('U:\My Documents\Recherche\Données\Samples\samples.yml') as f:
        # use safe_load instead of load
        samples = yaml.safe_load(f)

    w_pourcent = samples[sample_ID]['concentration']
    solvant = samples[sample_ID]['solvant']
    microgel_type = samples[sample_ID]['microgel_type']

    columns = ['sample_ID', 'w_pourcent', 'solvant', 'microgel_type',
                'temperature', 'tauc_HB', 'err_taucHB', 'K', 'err_K', 'n', 'err_n',
                'tauc_TC', 'err_taucTC', 'etas', 'err_etas', 'gamma_dotc',
                'err_gammadotc', 'gammac', 'err_gammac']

    try :
        df_fit_pkl = pd.read_pickle('df_fit.pkl')
    except FileNotFoundError :
        print('new pickle file')
        df_fit_pkl = pd.DataFrame(columns=columns)

    if replace:
        print('data will be replaced')
        df_fit_pkl = pd.DataFrame(columns=columns)

    # Select data of interest in the dataframe
    dfh = df[(df.temperature == T) &
            (df.sample_ID == sample_ID) &
            (df.sweep_direction == 'inverse') &
            (df.experiment_type == 'flow_curve')]

    if len(dfh) == 0:
        print('empty_data_set')
        return 0

    # Merge all stress data

    Stress = np.array([])
    Shear_rate = np.array([])
    for i in dfh.index :
        dfi = dfh.loc[i]
        stress = np.array(dfi['stress'], dtype=float)
        shear_rate = np.array(dfi['shear_rate'], dtype=float)
        Shear_rate, Stress = merge_physical_data(Shear_rate, shear_rate, Stress, stress)
    try:
        # Do the HB fit
        param_bounds_HB=([0,0,0],[np.inf,np.inf,1])
        popt_HB, pcov_HB = curve_fit(HB, Shear_rate, Stress,bounds=param_bounds_HB)
        std_HB = np.sqrt(np.diag(pcov_HB))

        # Extract parameters from HB fit

        # tauc
        tauc_HB, err_taucHB = round_physical(popt_HB[0], std_HB[0])
        #print(tauc_HB, err_taucHB)

        # K
        K, err_K = round_physical(popt_HB[1] , std_HB[1])
        #print(K, err_K)

        # n
        n , err_n = round_physical(popt_HB[2], std_HB[2])
        #print(n, err_n)
    except RuntimeError:
        print('No fit HB possible for sample ', sample_ID)
        plot = False
        return 0


    try:
        # Do the TC fit
        param_bounds_TC=([0,0,0],[np.inf,np.inf,np.inf])

        popt_TC, pcov_TC = curve_fit(TC, Shear_rate, Stress,bounds=param_bounds_TC)
        std_TC = np.sqrt(np.diag(pcov_TC))

        # Extract parameters from TC fit

        tauc_TC, err_taucTC = round_physical(popt_TC[0], std_TC[0])
        #print(tauc_TC, err_taucTC)

        gamma_dotc, err_gammadotc = round_physical(popt_TC[1], std_TC[1])
        #print(gamma_dotc, err_gammadotc)

        test_if_nul, err_etas = round_physical(popt_TC[2], std_TC[2])

        if test_if_nul == 0:
            etas = round(popt_TC[2], int(floor(log10(abs(popt_TC[2])))))
        else:
            etas = test_if_nul
        #print(etas, err_etas)
        if etas == 0:
            print('no high shear regime, no etas')
            plot=False
            return 0
    except RuntimeError:
        print('No fit TC possible for sample ', sample_ID)
        plot = False
        return 0



    # Create pretty labels

    lab_HB = r'$\mathrm{HB} =' + str(tauc_HB) + '\pm' + str(err_taucHB) + '+' + str(K) + '\pm' + str(err_K) + '* \dot{\gamma_\mathrm{c}}^{'  + str(n) + '\pm' + str(err_n) + '}$'
    lab_TC = r'$\mathrm{TC} = ' + str()

    if plot :
        fig, ax, color , marker = create_plot()

        # plot data
        ax.plot(Shear_rate, Stress, c='gray')

        # plot fits
        min_pow = int(math.log10(min(Shear_rate))) -1
        max_pow = int(math.log10(max(Shear_rate)))
        x = np.logspace(-4, 4, base=10, num=30)
        ax.plot(x, HB(x, tauc_HB, K, n), ls='-', c='purple', marker='',
                label=r'$\sigma_\mathrm{y}^\mathrm{HB} + K \dot{\gamma}^n$')
        ax.plot(x, TC(x, tauc_TC, gamma_dotc, etas), ls='-', c='teal', marker='',
                label=r'$\sigma_\mathrm{y}^\mathrm{TC} + \sigma_\mathrm{y}^\mathrm{TC} \left ( \frac{\dot{\gamma}}{\dot{\gamma_\mathrm{c}}} \right ) ^{1/2} + \eta_\infty \dot{\gamma}$')

        # plot boundaries
        ax.axvline(gamma_dotc, ls='--', c='lightgray', marker='')
        ax.text(gamma_dotc, 0.05, r'$\dot{\gamma_\mathrm{c}}$', size='large', c='lightgray', backgroundcolor='w', ha='center')

        ax.axvline(tauc_TC / etas, ls='--', c='lightgray', marker='')
        ax.text(tauc_TC / etas, 0.05, r'$\sigma_\mathrm{y}^{\mathrm{TC}} / \eta_\infty$', size='large', c='lightgray', backgroundcolor='w', ha='center')

        ax.set(xscale='log', yscale='log')
        ax.set(ylim=(0.01, 1e4), xlim=(1e-4, 2e3))
        #ax.legend()
        x_legend = 4e3
        ax.set(xlabel = r'$\dot{\gamma}~\mathrm{(s^{-1})}$', ylabel = r"$\sigma~\mathrm{(Pa)}$")
        ax.text(x_legend, 510, r'$\sigma_\mathrm{y}^\mathrm{HB} = ' + str(tauc_HB) + '\pm' + str(err_taucHB) + '~\mathrm{Pa}$')
        ax.text(x_legend,220, r'$K = ' + str(K) + '\pm' + str(err_K) + '$')
        ax.text(x_legend,80, r'$n = ' + str(n) + '\pm' + str(err_n) + '$')

        ax.text(x_legend, 9, r'$\sigma_\mathrm{y}^\mathrm{TC} = ' + str(tauc_TC) + '\pm' + str(err_taucTC) + '~\mathrm{Pa}$')
        ax.text(x_legend,3, r'$\dot{\gamma_\mathrm{c}} = ' + str(gamma_dotc) + '\pm' + str(err_gammadotc) + '~\mathrm{s^{-1}}$')
        ax.text(x_legend,1, r'$\eta_\infty = ' + str(etas) + '\pm' + str(err_etas) + '~\mathrm{Pa.s}$')

        ax.text(0, 1.05, r'$' + str(w_pourcent) + '~\%$', transform=ax.transAxes)
        #ax.text(0.5, 1.05, r'$\mathrm{' + str(solvant) + '}$', va='center', transform=ax.transAxes)
        #ax.text(0.2, 1.05, r'$\mathrm{T = ~}' + str(T) + '^\circ \mathrm{C}$', transform=ax.transAxes)
        plt.savefig('fits_sample_' + str(sample_ID) + '_T' + str(T) + '.pdf', bbox_inches = 'tight')
        plt.savefig('fits_sample_' + str(sample_ID) + '_T' + str(T) + '.png', bbox_inches = 'tight', dpi=200)

    # Add critical shear rate
    gammac = gamma_dotc *  etas / tauc_TC
    # Error propagation
    err_gammac = err_gammadotc * etas / tauc_TC + err_taucTC * gamma_dotc * etas / (tauc_TC * tauc_TC) + err_etas * gamma_dotc / tauc_TC
    # Remove numbers that are not physical
    gammac, err_gammac = round_physical(gammac , err_gammac)


    dict_fits = {'tauc_HB' : tauc_HB, 'err_taucHB' : err_taucHB,
                              'K': K, 'err_K': err_K, 'n' : n, 'err_n': err_n,
                              'tauc_TC': tauc_TC, 'err_taucTC': err_taucTC,
                              'etas' : etas, 'err_etas': err_etas,
                              'gamma_dotc' : gamma_dotc, 'err_gammadotc': err_gammadotc,
                              'gammac' : gammac, 'err_gammac' : err_gammac}

    print(sample_ID)
    print(dict_fits)


    df_fit_pkl = df_fit_pkl.append(dict(zip(df_fit_pkl.columns,[int(sample_ID), w_pourcent, solvant, microgel_type,
                                                        T, tauc_HB, err_taucHB, K, err_K, n, err_n,
                                                        tauc_TC, err_taucTC, etas, err_etas,
                                                        gamma_dotc, err_gammadotc, gammac, err_gammac])), ignore_index=True)

    df_fit_pkl.to_pickle('df_fit.pkl', compression='infer', protocol=5, storage_options=None)

    return dict_fits
