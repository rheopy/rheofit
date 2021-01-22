import ipywidgets as widgets
import numpy as np
import matplotlib.pyplot as plt
import lmfit

def make_par_widget(model,data=None):
    ''' '''
    if data is not None:
        res_fit=model.fit(data['Stress'],x=data['Shear rate'],weights=1/(0.05*data['Stress']))
        params=res_fit.params
    else:
        params=model.make_params()
    
    
    
    model_name_widget=widgets.Text(description='Model name',value=model.name,
                                   style={'description_width': 'initial'},
                                   layout=widgets.Layout(width='80%'))
    
    par_list_wid=[]
    for name,param in params.items():    
        par_list_wid.append(widgets.HBox([widgets.Text(value=name),
                                          widgets.Text(description='min/val/max',value=str(param.min)),
                                          widgets.Text(value=str(param.value)),
                                          widgets.Text(value=str(param.max)),
                                          widgets.Checkbox(description='fix',value=not(param.vary)),
                                         ]))
                      
    box_layout = widgets.Layout(display='flex',
                                flex_flow='column',
                                align_items='stretch',
                                border='solid')
    
    par_widgets=widgets.VBox([model_name_widget]+par_list_wid,layout=box_layout)
    display(par_widgets)
    return par_widgets

def update_par_widget(par_wid,fit_res):
    params=fit_res.params
    
    for param, wid in zip(params.values(),par_wid.children[1:]):
        wid.children[2].value=str(param.value)

def make_par_from_widget(par_widget):
    params = lmfit.Parameters()
    
    for par_info in par_widget.children[1:]:
        
        params.add(par_info.children[0].value,
                      min=float(par_info.children[1].value),
                      value=float(par_info.children[2].value),
                      max=float(par_info.children[3].value),
                      vary=not(par_info.children[4].value),
                      )

    return params


def plot_fit_res(fit_res, show_par_values=False,exp_err=0.05):
    
    fig, (ax1,ax3) = plt.subplots(2,1, sharex=True)
    ax2 = ax1.twinx()

    ax1.plot(fit_res.userkws['x'],fit_res.data,'o', color='red', mfc='none', label='data')
    ax1.plot(fit_res.userkws['x'],fit_res.eval(x=fit_res.userkws['x']),'-', color='black', label='best fit')

    ax2.plot(fit_res.userkws['x'],fit_res.data/fit_res.userkws['x'],'o', color='blue', mfc='none')
    ax2.plot(fit_res.userkws['x'],fit_res.eval(x=fit_res.userkws['x'])/fit_res.userkws['x'],'-', color='black')
    
    ax3.plot(fit_res.userkws['x'], (fit_res.data-fit_res.eval(x=fit_res.userkws['x']))/fit_res.data,'o', color='blue', mfc='none')
    ax3.fill_between(fit_res.userkws['x'], -exp_err,exp_err,
                     color='blue',alpha=0.2,label='estimated exp error')

    
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax2.set_yscale('log')

    ax1.set_ylabel('$\sigma [Pa]$')
    ax3.set_xlabel('$\dot\gamma [1/s]$')
    ax2.set_ylabel('$\eta [Pa s]$')
    ax3.set_ylabel('relative residuals')
    
    ax3.set_ylim(-0.2,0.2)
    
    ax3.legend()
    
    if show_par_values:
        mod_par_text=''
        for item in fit_res.params:
            mod_par_text+=(f'{item} : {fit_res.params[item].value:.2E} \n')

        mod_par_text+=f'Red chi square: {fit_res.redchi:.2E} \n'

        plt.text(-1, 0.95, mod_par_text, transform=plt.gca().transAxes, fontsize=14,verticalalignment='top')
        fig.suptitle(fit_res.model)
    
    return fig

def plot_confidence(res_fit,expand=1):
    dely = res_fit.eval_uncertainty(x=res_fit.userkws['x'],sigma=3)*expand

    plt.plot(res_fit.userkws['x'], res_fit.data,'o',color='black',label='Data',markersize=5)
    plt.plot(res_fit.userkws['x'], res_fit.best_fit,label='Best fit TC model',color='red')
    plt.fill_between(res_fit.userkws['x'], res_fit.best_fit-dely,res_fit.best_fit+dely,
                     color='blue',alpha=0.2,label='0.9973 Confidence interval')
    plt.yscale('log')
    plt.xscale('log')
    plt.ylabel('$\sigma [Pa]$')
    plt.xlabel('$\dot\gamma [1/s]$')
