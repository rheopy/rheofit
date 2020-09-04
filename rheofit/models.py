# -*- coding: utf-8 -*-
"""
Module for rheology data fitting
--------------------------------

Provides functions and fitting procedure to fit rheological data

Currently focusing on flowcurve

Model expressions and LMfit model are provided

Example:

        rheology.rheology_fit.HB -> Model expression (simple function)
        rheology.rheology_fit.HB_model -> lmfit model object

It also provides few convenience functions to rapidly see and plot the result of
the fit.

"""
import lmfit
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Math
import numpy as np


def constantstress(x, ystress=0.1):
    """Constant stress model

    Note:

    .. math::
       \sigma=\sigma_y

    Args:

    Returns:
        stress : Shear Stress, [Pa]
    """
    return ystress


# instantiate model class
constantstress_model = lmfit.Model(constantstress, prefix="constantstress_")
""" Lmfit model from equation :meth:`rheofit.models.constantstress`

Note:

"""
constantstress_model.model_expression = Math("\sigma=\sigma_y")


# set parameters for model class
constantstress_model.set_param_hint("ystress", min=0, vary=True)


def Newtonian(x, eta_bg=0.1):
    """Newtonian model

    Note:

    .. math::
       \sigma=\eta_{bg}\cdot\dot\gamma

    Args:

        eta_bg : viscosity [Pa s]

    Returns:
        stress : Shear Stress, [Pa]
    """
    return eta_bg * x


# instantiate model class
Newtonian_model = lmfit.Model(Newtonian, prefix="newtonian_")
""" Lmfit model from equation :meth:`rheofit.models.Bingham`

Note:

Newtonian_model.set_param_hint('eta_bg', min=0, vary=True)


"""
Newtonian_model.model_expression = Math("\sigma=\eta_{bg}\cdot\dot\gamma")


# set parameters for model class
Newtonian_model.set_param_hint("eta_bg", min=0, vary=True)


def Powerlaw(x, n=0.5, K=0.1):
    """Powerlaw model for the stress data

    Note:

    .. math::
       \sigma=K \cdot \dot\gamma^n

    Args:

        K : consistency index [Pa s]
        n : shear thinning index (1 for Newtonian) []

    Returns:
        stress : Shear Stress, [Pa]
    """
    return K * x ** n


# instantiate model class
Powerlaw_model = lmfit.Model(Powerlaw, prefix="PL_")
""" Lmfit model from equation :meth:`rheofit.models.Bingham`

Note:

Powerlaw_model.set_param_hint('K', min=0, vary=True)
Powerlaw_model.set_param_hint('n', min=0, vary=True)


"""
Powerlaw_model.model_expression = Math("\sigma=K\cdot\dot\gamma^n")


# set parameters for model class
Powerlaw_model.set_param_hint("K", min=0, vary=True)
Powerlaw_model.set_param_hint("n", min=0, vary=True)


def Bingham(x, ystress=1.0, eta_bg=0.1):
    """Bingham model

    Note:

    .. math::
       \sigma=\sigma_y+\eta_{bg}\cdot\dot\gamma

    Args:
        ystress: yield stress [Pa]

        eta_bg : Background viscosity [Pa s]

    Returns:
        stress : Shear Stress, [Pa]
    """
    return ystress + eta_bg * x


# instantiate model class
Bingham_model = lmfit.Model(Bingham, prefix="bingham_")
""" Lmfit model from equation :meth:`rheofit.models.Bingham`

Note:

Bingham_model.set_param_hint('ystress', min=0)

Bingham_model.set_param_hint('eta_bg', min=0, vary=True)


"""
Bingham_model.model_expression = Math(
    "\sigma=\sigma_y + \eta_{bg}\cdot\dot\gamma")


# set parameters for model class
Bingham_model.set_param_hint("ystress", min=0)
Bingham_model.set_param_hint("eta_bg", min=0, vary=True)


def TC(x, ystress=1.0, eta_bg=0.1, gammadot_crit=0.1):
    """Three component model

    Note:

    .. math::
       \sigma=\sigma_y+\sigma_y\cdot(\dot\gamma/\dot\gamma_c)^{0.5}+\eta_{bg}\cdot\dot\gamma

    Args:
        ystress: yield stress [Pa]

        eta_bg : Background viscosity [Pa s]

        gammadot_crit : Critical shear rate [1/s]

    Returns:
        stress : Shear Stress, [Pa]
    """
    return ystress + ystress * (x / gammadot_crit) ** 0.5 + eta_bg * x


# instantiate model class
TC_model = lmfit.Model(TC, prefix="TC_")
""" Lmfit model from equation :meth:`rheofit.models.TC`

Note:

TC_model.set_param_hint('ystress', min=0)

TC_model.set_param_hint('eta_bg', min=0, vary=True)

TC_model.set_param_hint('gammadot_crit', min=0)
"""
TC_model.model_expression = Math(
    "\sigma=\sigma_y+\sigma_y\cdot(\dot\gamma/\dot\gamma_c)^{0.5}+\eta_{bg}\cdot\dot\gamma"
)


# set parameters for model class
TC_model.set_param_hint("ystress", min=0)
TC_model.set_param_hint("eta_bg", min=0, vary=True)
TC_model.set_param_hint("gammadot_crit", min=0)


def TCn(x, ystress=1.0, eta_bg=0.1, gammadot_crit=0.1,n=0.5):
    """Three component model

    Note:

    .. math::
       \sigma=\sigma_y+\sigma_y\cdot(\dot\gamma/\dot\gamma_c)^n+\eta_{bg}\cdot\dot\gamma

    Args:
        ystress: yield stress [Pa]

        eta_bg : Background viscosity [Pa s]

        gammadot_crit : Critical shear rate [1/s]
        
        n: Shear thinning exponent

    Returns:
        stress : Shear Stress, [Pa]
    """
    return ystress + ystress * (x / gammadot_crit) ** n + eta_bg * x


# instantiate model class
TCn_model = lmfit.Model(TCn, prefix="TCn_")
""" Lmfit model from equation :meth:`rheofit.models.TC`

Note:

TCn_model.set_param_hint('ystress', min=0)

TCn_model.set_param_hint('eta_bg', min=0, vary=True)

TCn_model.set_param_hint('gammadot_crit', min=0)

TCn_model.set_param_hint('n', min=0, max=1)
"""
TCn_model.model_expression = Math(
    "\sigma=\sigma_y+\sigma_y\cdot(\dot\gamma/\dot\gamma_c)^{0.5}+\eta_{bg}\cdot\dot\gamma"
)


# set parameters for model class
TCn_model.set_param_hint("ystress", min=0)
TCn_model.set_param_hint("eta_bg", min=0, vary=True)
TCn_model.set_param_hint("gammadot_crit", min=0)
TCn_model.set_param_hint("n", min=0, max=1)


def HB(x, ystress=1.0, K=1.0, n=0.5):
    """Hershel-Bulkley Model

    Note:

    .. math::
       \sigma= \sigma_y + K \cdot \dot\gamma^n

    Args:
        ystress: yield stress [Pa]

        K : Consistency index [Pa s^n]

        n : Shear thinning index []

    Returns:
        stress : Shear Stress, [Pa]
    """
    return ystress + K * x ** n


HB_model = lmfit.Model(HB, prefix="HB_")
""" Lmfit model from equation :meth:`rheofit.models.HB`

Note:
HB_model.set_param_hint('ystress', min=0)

HB_model.set_param_hint('K', min=0, vary=True)

HB_model.set_param_hint('n', min=0.0,max=1,vary=True)
"""

HB_model.model_expression = Math("\sigma=\sigma_y+K\cdot\dot\gamma^n")

HB_model.set_param_hint("ystress", min=0)
HB_model.set_param_hint("K", min=0, vary=True)
HB_model.set_param_hint("n", min=0.0, max=1, vary=True)


def casson(x, ystress=1.0, eta_bg=0.1):
    """Casson Model

    Note:

    .. math::
       \sigma^{0.5}= \sigma_y^{0.5} + \eta_{bg}^{0.5}

    Args:
        ystress: yield stress [Pa]

        eta_bg : Background viscosity [Pa s]

    Returns:
        stress : Shear Stress, [Pa]
    """
    return (ystress ** 0.5 + (eta_bg * x) ** 0.5) ** 2


casson_model = lmfit.Model(casson, prefix="casson_")
""" Lmfit model from equation :meth:`rheofit.models.casson`

Note:
casson_model.set_param_hint('ystress', min=0)

casson_model.set_param_hint('eta_bg', min=0, vary=True)

"""
casson_model.model_expression = Math(
    "\sigma^{0.5}=\sigma_y^{0.5}+\eta_{bg}^{0.5}")

casson_model.set_param_hint("ystress", min=0)
casson_model.set_param_hint("eta_bg", min=0, vary=True)


def carreau(x, eta_0=1.0, gammadot_crit=1.0, n=0.5, prefix="carreau"):
    """carreau Model

    Note:

    .. math::
       \sigma=\dot\gamma \cdot \eta_0 \cdot (1+(\dot\gamma/\dot\gamma_c)^2)^{(n-1)/2}

    Args:
        eta_0: low shear viscosity [Pa s]

        gammadot_crit: critical shear rate [1/s]

        n : shear thinning exponent

    Returns:
        stress : Shear Stress, [Pa]
    """
    return x * eta_0 * (1 + (x / gammadot_crit) ** 2) ** ((n - 1) / 2)


carreau_model = lmfit.Model(carreau, prefix="carreau_")
""" Lmfit model from equation :meth:`rheofit.models.carreau`

Note:
carreau_model.set_param_hint('eta_0', min=0)

carreau_model.set_param_hint('gammadot_crit_carreau', min=0, vary=True)

carreau_model.set_param_hint('n',min=0, max=1)
"""
carreau_model.model_expression = Math(
    "\sigma=\dot\gamma \cdot \eta_0 \cdot (1+(\dot\gamma/\dot\gamma_{c_carreau})^2)^{(n-1)/2}"
)

carreau_model.set_param_hint("eta_0", min=0)
carreau_model.set_param_hint("gammadot_crit", min=0, vary=True)
carreau_model.set_param_hint("n", min=0, max=1)


def cross(x, eta_inf=0.001, eta_0=1.0, n=0.5, gammadot_crit=1.0):
    """cross Model

    Note:

    .. math::
       \sigma= \dot\gamma \eta_{inf} + \dot\gamma (\eta_0 - \eta_{inf})/(1 + (\dot\gamma/\dot\gamma_c)^n)

    Args:
        ystress: yield stress [Pa]

        K : Consistency index [Pa s^n]

        n : Shear thinning index []

    Returns:
        stress : Shear Stress, [Pa]
    """
    return x * eta_inf + x * (eta_0 - eta_inf) / (1 + (x / gammadot_crit) ** n)


cross_model = lmfit.Model(cross, prefix="cross_")
""" Lmfit model from equation :meth:`rheofit.models.HB`

Note:
cross_model.set_param_hint('eta_0', min=0)

cross_model.set_param_hint('eta_inf', min=0, vary=True)

cross_model.set_param_hint('n', min=0.0,max=1,vary=True)

cross_model.set_param_hint('gammadot_crit', min=0.0 ,vary=True)

"""

cross_model.model_expression = Math(
    "\sigma= \dot\gamma \eta_{inf} + \dot\gamma (\eta_0 - \eta_{inf})/(1 + (\dot\gamma/\dot\gamma_c)^n)"
)

cross_model.set_param_hint("eta_0", min=0)
cross_model.set_param_hint("eta_inf", min=0, vary=True)
cross_model.set_param_hint("n", min=0.0, max=1, vary=True)
cross_model.set_param_hint("gammadot_crit", min=0.0, vary=True)


def show_parameter_table(result):
    """ Convenience function to convert lmfit fit parameter result information
        a panda dataframe for easy display and concatenation.

        Args:

        result: Lmfit.fitresult object

        Returns:

        Pandas datafrme with estimated parameters and some quality of fit metrics
    """
    table_list = (
        pd.DataFrame.from_dict(result.params.valuesdict(), orient="index")
        .rename(columns={0: result.model.name})
        .transpose()
    )
    # table_list['aic']=result.aic
    table_list["bic"] = result.bic
    # table_list['chisqr']=result.chisqr
    table_list["redchi"] = result.redchi

    return table_list


def fit_FC(model, data):
    """ Convenience function to fit a flow curve
        Args:

        model: rheology model (e.g. HB_model)

        data: pandas DataFrame with column 'Shear rate' and 'Stress'

        Returns:

        lmfit.fitresult
    """
    return model.fit(data["Stress"], x=data["Shear rate"], weights=1 / data["Stress"])


def plot_fit_fc(result, show_table=True):
    """ Convenience function to plot data and fit of a flow curve
        Args:

        result: lmfit.fitresult

        show_table: default=True (show fit parameter table)

        Returns:

        None and display plot on current ax
    """

    kwarg = {"yscale": "log", "xscale": "log"}
    result.plot_fit(ax_kws=kwarg, yerr=False)
    plt.xlabel("Shear rate [1/s]")
    plt.ylabel("Stress [Pa]")
    if show_table:
        display(show_parameter_table(result))
