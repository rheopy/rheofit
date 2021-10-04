# Data from litterature

## Naming convention

Fig#AuthorYear   | If 'S' in figure number, then the plot can be found in the supplementary materials of the paper

## YML file (data_from_litterature.yml)

This one contains information about the samples and experiments for each paper

Example of an entry : 

```yaml
Fig2_Dekker2018:
  figure_number: 2
  title: Scaling of flow curves Comparison between experiments and simulations
  year: 2018
  doi: 10.1016/j.jnnfm.2018.08.006
  author: Riande I. Dekker and Maureen Dinkgreve and Henri de Cagny and Dion J. Koeze and Brian P. Tighe and Daniel Bonn
  sample: castor oil concentrated emuslions
  unit_x: s-1
  unit_y: Pa
  solvent_viscosity: 0.00089 #Pa.s for water at 25°C
```

## Python file (extract_all_data.py)

- pickles every useful information about the figures by grabbing the yml file and the different csv ones
- do the TC fits
- store info in dataframe that looks like 

![example_of_DF](https://user-images.githubusercontent.com/16650466/135865565-6bb232ca-70b3-47e4-8819-a395f63ea5ea.PNG)

for each of the figures

### Columns signification

- ID : string, naming convention for the figure
- solvent_viscosity : float, extracted from the yml file in Pa.s
- phi : float, packing fraction without dimention
- shear_rate : array, extracted from csv file in s-1
- stress : array, extracted from csv file in Pa
- tauc_TC : float, yield stress from TC fit in Pa
- err_taucTC : float, estimated from fit parameters in Pa
- gamma_dotc : float, critical shear rate from TC fit in s-1
- err_gammadotc : float, estimated from fit parameters in s-1
- etas : float, solvent viscosity from fit TC in Pa.s
- err_etas : float, estimated fron TC fit in Pa.s


## Jupyter notebook 

To make the plots

TODO : add description of plots here
