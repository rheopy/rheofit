import collections
import os
import io
import xmltodict
import pandas as pd
import numpy as np


def example_emulsion():
    ''' 
    Example flow curve data for oil in water emulsion
    1400 cp mineral oil in 11%Las solution
    temperature 40C 
    '''

    emulsion_75_1400oil_11Las_40C = '''
    999.89475	131.22475
    891.251	121.57225
    794.32825	112.56525
    707.946	104.258
    630.9575	96.58295
    562.3415	89.495925
    501.187	82.973725
    446.68325	76.9523
    398.109	71.44925
    354.815	66.3825
    316.22775	61.738
    281.83825	57.47005
    251.18875	53.562825
    223.872	49.97115
    199.52725	46.678
    177.829	43.6651
    158.49075	40.8936
    141.253	38.34355
    125.8935	35.99815
    112.202	33.8341
    100.000225	31.832825
    89.12585	29.987525
    79.433425	28.279775
    70.7948	26.694725
    63.095775	25.224025
    56.234175	23.86125
    50.118925	22.594175
    44.6684	21.4186
    39.810875	20.322825
    35.4814	19.299625
    31.622875	18.345225
    28.183875	17.461225
    25.11905	16.63715
    22.387175	15.854425
    19.9526	15.1421
    17.782925	14.46635
    15.84895	13.8322
    14.1254	13.239375
    12.5893	12.68375
    11.2202	12.159
    9.99999	11.673425
    8.9125625	11.22175
    7.94331	10.7851
    7.07947	10.38505
    6.3095775	9.998685
    5.62345	9.64747
    5.0118825	9.31164
    4.4668375	8.98708
    3.9810825	8.69169
    3.548155	8.411305
    3.162275	8.146395
    2.81839	7.8957675
    2.5118925	7.65902
    2.2387325	7.4321325
    1.99527	7.221855
    1.778285	7.0237075
    1.5848975	6.8350625
    1.41254	6.6558
    1.258925	6.481415
    1.12203	6.3202925
    0.99999975	6.16896
    0.89125	6.0223275
    0.794334	5.8852825
    0.70794875	5.75524
    0.63096	5.6274075
    0.562345	5.5108375
    0.501192	5.398845
    0.44668775	5.2893075
    0.3981065	5.1846275
    0.354813	5.08736
    0.31623175	4.99462
    0.281839	4.9035125
    0.2511915	4.8152925
    0.2238725	4.7298725
    0.199528	4.6480125
    0.17782975	4.568455
    0.15849025	4.490795
    0.14125325	4.4134175
    0.12589225	4.33758
    0.11220125	4.26175
    0.09999935	4.186445
    0.0891251	4.1115975
    0.0794312	4.0362175
    0.070794875	3.961225
    0.0630968	3.88675
    0.056236125	3.8126625
    0.0501176	3.7392575
    0.044667425	3.666965
    0.039811625	3.5960975
    0.035480175	3.5267725
    0.03162185	3.4587725
    0.028183125	3.393145
    0.025117975	3.3298475
    0.0223869	3.269595
    0.0199527	3.2101825
    0.017782225	3.1534325
    0.015847575	3.0989675
    0.014125525	3.046845
    0.01258835	2.9974
    0.011219275	2.950915
    0.009999548	2.9067975
    '''
    FC = pd.read_csv(io.StringIO(emulsion_75_1400oil_11Las_40C), names=[
                     'Shear rate', 'Stress'], delimiter='\t').astype('float')
    FC['Stress'] = FC['Stress']
    FC.sort_values('Shear rate', ascending=False, inplace=True)

    return FC


def get_data_dict(data_name):
    '''
    parse xml file into dicionary
    '''
    with open(data_name) as xml_file:
        try:
            xml_file.seek(0)
            data_dict = xmltodict.parse(xml_file.read())
        except:
            xml_file.seek(3)
            data_dict = xmltodict.parse(xml_file.read())
    return data_dict


def dicttopanda(datadict):
    ''' Covert dictionary from rheoml to list of pandas table'''

    datasource = datadict['RheoML_Dataset']['ExperimentalData']
    pandalist = []
    counter = 0

    if isinstance(datasource, list) == False:
        datasource = [datasource]
    for experiment in datasource:
        datatable = []

        if 'DMA' in experiment.keys():
            for line in experiment['DMA']:
                linelist = []
                columns = []

                for cellkey in line.keys():
                    linelist.append(float(line[cellkey]['#text']))
                    columns.append(cellkey)
                datatable.append(linelist)
            pandatable = pd.DataFrame(np.array(datatable), columns=columns)

        if 'RVM' in experiment.keys():

            for line in experiment['RVM']:
                linelist = []
                columns = []

                if isinstance(experiment['RVM'], list) == False:
                    line = experiment['RVM']

                for cellkey in line.keys():
                    linelist.append(float(line[cellkey]['#text']))
                    columns.append(cellkey)
                datatable.append(linelist)
            pandatable = pd.DataFrame(np.array(datatable), columns=columns)
        pandalist.append(pandatable)
    return pandalist


class rheology_data(object):
    '''Container for rheology data from trios rheometer software.

    Accept excel file exported with the option multitab.
    The main utility of this class is for test consisting of Multiple
    steps. The rheology_data class accept index and return the nth
    step result as a tuple with (step_name, Pandas Dataframe)

    The rheology_data class can also be added to append the steps of the
    second object to the steps of the first.
    This is usefull to combine consecutive tests when exported as
    multiple files (Rheology advantage software)

    Attributes:
        filename (str): name of data file (xls from trios)

    '''

    def __init__(self, filename, source='trios_multitab_xls'):
        '''
        Assuming Shear stress label 'Stress' And Shear rate label 'Shear rate'
        Args:
            filename (str): name of data file
            source (str): Options 'trios_multitab_xls' (default), 'pandas_export_excel'
        '''
        if source == 'trios_multitab_xls':
            self.filename = str(filename)

            data_file_object = pd.ExcelFile(filename)
            table_name_list = data_file_object.sheet_names

            self.data = collections.OrderedDict()

            for table_name in table_name_list:
                if table_name == 'Details':
                    self.Details = pd.read_excel(data_file_object,
                                                 sheet_name='Details',
                                                 header=None,
                                                 names=['key', 'value']).set_index('key')

                    try:
                        sample_notes = [self.Details.loc['Sample notes'].value]

                        for key, value in self.Details.iloc[self.Details.index.get_loc('Sample notes')+1:self.Details.index.get_loc('Geometry name')].iterrows():
                            sample_notes.append(key)

                        sample_notes = [
                            x for x in sample_notes if str(x) != 'nan']
                        self.sample_notes = sample_notes
                    except:
                        self.sample_notes = ''

                    try:
                        self.instrument_serial = self.Details.loc['Instrument serial number'].value
                    except:
                        self.instrument_serial = ''

                    try:
                        self.geometry_name = self.Details.loc['Geometry name'].value
                    except:
                        self.geometry_name = ''

                    try:
                        self.instrument_type = self.Details.loc['Instrument type'].value
                    except:
                        self.instrument_type = ''

                    try:
                        self.run_date = self.Details.loc['Run date'].value
                    except:
                        self.run_date = None

                else:
                    try:
                        self.data[table_name] = data_file_object.parse(
                            table_name, skiprows=1).drop(0).reset_index().astype('float')
                    except:
                        print('step ' + table_name + ' not loaded')

        elif source == 'pandas_export_excel':
            self.filename = str(filename)

            data_file_object = pd.ExcelFile(filename)
            table_name_list = data_file_object.sheet_names

            self.data = collections.OrderedDict()

            for table_name in table_name_list:
                if table_name == 'Details':
                    self.Details = pd.read_excel(data_file_object,
                                                 sheet_name=table_name)
                else:
                    try:
                        self.data[table_name] = data_file_object.parse(
                            table_name).astype('float')
                    except:
                        print('step ' + table_name + ' not loaded')

        elif source == 'file_like_object':
            self.filename = 'from filelike object'

            data_file_object = pd.ExcelFile(filename)
            table_name_list = data_file_object.sheet_names

            self.data = collections.OrderedDict()

            for table_name in table_name_list:
                if table_name == 'Details':
                    self.Details = pd.read_excel(data_file_object,
                                                 sheet_name='Details',
                                                 header=None,
                                                 names=['key', 'value']).set_index('key')

                    try:
                        sample_notes = [self.Details.loc['Sample notes'].value]

                        for key, value in self.Details.iloc[self.Details.index.get_loc('Sample notes')+1:self.Details.index.get_loc('Geometry name')].iterrows():
                            sample_notes.append(key)

                        sample_notes = [
                            x for x in sample_notes if str(x) != 'nan']
                        self.sample_notes = sample_notes
                    except:
                        self.sample_notes = ''

                    try:
                        self.instrument_serial = self.Details.loc['Instrument serial number'].value
                    except:
                        self.instrument_serial = ''

                    try:
                        self.geometry_name = self.Details.loc['Geometry name'].value
                    except:
                        self.geometry_name = ''

                    try:
                        self.instrument_type = self.Details.loc['Instrument type'].value
                    except:
                        self.instrument_type = ''

                    try:
                        self.run_date = self.Details.loc['Run date'].value
                    except:
                        self.run_date = None

                else:
                    try:
                        self.data[table_name] = data_file_object.parse(
                            table_name, skiprows=1).drop(0).reset_index().astype('float')
                    except:
                        print('step ' + table_name + ' not loaded')

        else:
            raise ValueError('''data not loaded''')

    @property
    def tidy(self):
        for (stepnum, stepdata) in enumerate(self):
            stepdata[1]['Stepnum'] = stepnum
            stepdata[1]['stepname'] = stepdata[0]
            stepdata[1]['filename'] = self.filename
            if stepnum == 0:
                fulldata = stepdata[1]
            else:
                fulldata = pd.concat(
                    [fulldata, stepdata[1]], ignore_index=True, sort=False)
        return fulldata

    def __getitem__(self, i):
        return list(self.data.items())[i]

    def __repr__(self):
        if self.filename is None:
            ret_string = 'No data'
        else:
            ret_string = 'rheology_data('+self.filename+')'
        return ret_string

    def __add__(self, other):
        self.data.update(other.data)
        return self


class data_package(object):
    def __init__(self, data_path, exp_files_dict=None, procedure=None):

        self.procedure = procedure

        if exp_files_dict is None:
            self.source = 'Trios'
            filelist = [item for item in os.listdir(
                data_path) if '.xls' in item]

            data_dict = {}
            for file in filelist:
                data_dict[file] = data_path + file

            self.data_dict = data_dict
            self._len = len(data_dict)

        elif isinstance(exp_files_dict, dict):
            self.source = 'Advantage'
            self.data_dict = exp_files_dict

    @property
    def data_table(self):
        return pd.DataFrame.from_dict(
            {'filename': list(self.data_dict.keys()),
             'filepath': list(self.data_dict.values())})

    def __getitem__(self, index):

        def _concat_rheology_data(list):
            result = list[0]
            for item in list[1:]:
                result += item
            return result

        if isinstance(index, slice):
            return [self[ii] for ii in range(*index.indices(len(self)))]

        elif isinstance(index, int):
            if self.procedure is not None:
                if self.source == 'Trios':
                    return self.procedure(
                        rheology_data(self.data_table.iloc[index]['filepath']))
                if self.source == 'Advantage':
                    return self.procedure(
                        _concat_rheology_data(
                            [rheology_data(item) for item in
                             self.data_table.iloc[index]['filepath']]))

            else:
                if self.source == 'Trios':
                    return rheology_data(self.data_table.iloc[index]['filepath'])
                if self.source == 'Advantage':
                    return self._concat_rheology_data(
                        [rheology_data(item) for item in
                         self.data_table.iloc[index]['filepath']])

    def __len__(self):
        return self._len


if __name__ == "__main__":
    print('ok')
    pass
