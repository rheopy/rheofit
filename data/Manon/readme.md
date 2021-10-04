# Data from litterature

## YML file (data_from_litterature.yml)

This one contains information about the samples and experiments for each paper

Example of an entry : 

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

## Python file (extract_all_data.py)

Just pickles every useful information about the figures by grabbing the yml file and the different csv ones

## Jupyter notebook 

To make the plots

## Naming convention

Fig#AuthorYear

If 'S' in figure number, then the plot can be found in the supplementary materials of the paper
