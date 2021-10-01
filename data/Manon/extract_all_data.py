import pandas as pd
import yaml
import numpy as np
from plot_function import *
from scipy.optimize import curve_fit
import glob

# define TC model
def TC(x, tauy, gamma_dotc, etas):
    return tauy + tauy*((x / gamma_dotc)**0.5) + etas * x

def fit_TC(df):
    df['tauc_TC'] = np.nan ; df['err_taucTC'] = np.nan
    df['gamma_dotc'] = np.nan ; df['err_gammadotc'] = np.nan
    df['etas'] = np.nan ; df['err_etas'] = np.nan
    fig, ax, color, m = create_plot()
    ax.set(xscale='log', yscale='log',
           xlabel=r'$\dot{\gamma}~\mathrm{(1/s)}$',
           ylabel=r'$\tau~\mathrm{(Pa)}$')
    for i in df.index:
        c=next(color)
        dfi = df.loc[i]
        stress = np.array(dfi['stress'], dtype=float)
        #phi=dfi.phi
        shear_rate = np.array(dfi['shear_rate'], dtype=float)


        ax.plot(shear_rate, stress, c=c)
        try:
            # Do the TC fit
            param_bounds_TC=([0,0,0],[np.inf,np.inf,np.inf])

            popt_TC, pcov_TC = curve_fit(TC, shear_rate, stress,bounds=param_bounds_TC)
            std_TC = np.sqrt(np.diag(pcov_TC))

            # Extract parameters from TC fit

            tauc_TC, err_taucTC = round_physical(popt_TC[0], std_TC[0])
            df.at[i, 'tauc_TC'] = tauc_TC
            df.at[i, 'err_taucTC'] = err_taucTC


            gamma_dotc, err_gammadotc = round_physical(popt_TC[1], std_TC[1])
            df.at[i, 'gamma_dotc'] = gamma_dotc
            df.at[i, 'err_gammadotc'] = err_gammadotc

            etas, err_etas = round_physical(popt_TC[2], std_TC[2])
            df.at[i, 'etas'] = etas
            df.at[i, 'err_etas'] = err_etas

            # plot the fits to check if they make sense
            ax.plot(shear_rate, TC(shear_rate, tauc_TC, gamma_dotc, etas ), ls='--', c=c, marker='')
        except RuntimeError:
            print('No fit TC possible')

csv_files = glob.glob('*.csv')


papers_info = yaml.safe_load(open(glob.glob('data*.yml')[0]))
for file in csv_files:
    name = file.replace('.csv', '')

    df_raw = pd.read_csv( name + '.csv')

    df = pd.DataFrame(columns=['ID', 'solvent_viscosity', 'phi', 'shear_rate', 'stress'])
    ID = name
    solvent_viscosity = papers_info[name]['solvent_viscosity']
    for i, column_name in enumerate(df_raw.columns):
        if i%2 == 0:
            phi = float(column_name)
            if papers_info[name]['unit_x'] == 's-1':
                shear_rate = np.array(df_raw[column_name], dtype=float)
            elif papers_info[name]['unit_x'] == '0.158s-1':
                shear_rate = np.array(df_raw[column_name], dtype=float) / 0.158
            shear_rate = shear_rate[~np.isnan(shear_rate)]
        else:
            if papers_info[name]['unit_y'] == 'Pa':
                stress =  np.array(df_raw[column_name])
            elif papers_info[name]['unit_y'] == 'dynes/cm2':
                stress = 0.1* np.array(df_raw[column_name])
            elif papers_info[name]['unit_y'] == '0.0825Pa':
                stress =  np.array(df_raw[column_name]) * 0.0825
            stress = stress[~np.isnan(stress)]



            df = df.append(dict(zip(df.columns,
                                    [ID, solvent_viscosity, phi, shear_rate, stress])),
                                    ignore_index=True)

    fit_TC(df)
    df.to_pickle('df_' + name + '.pkl')
