import json 
import datetime as dt 
import cptdl as dl 
import copy 

def check_extent(extent):
    keys = ['north', 'south', 'east', 'west']
    for key in extent.keys():
        assert key in keys, 'illegal extent key - {}'.format(key)
        arg = keys.pop(keys.index(key))
        assert isinstance(arg, float) or isinstance(arg, int), 'extent arg must be numeric type'
    assert len(keys) == 0, 'missing keys from extent argument - {}'.format(keys)

def check_download_args(args):
    keys = ['fdate', 'first_year', 'final_year', 'predictor_extent', 'predictand_extent', 'lead_low', 'lead_high', 'target', 'filetype']
    keytypes = {'fdate': dt.datetime, 'first_year': int, 'final_year': int, 'predictor_extent': dict, 'predictand_extent': dict, 'lead_low': float, 'lead_high': float, 'target': str, 'filetype': str}
    for key in args.keys():
        assert key in keys, 'illegal extent key - {}'.format(key)
        arg = args[keys.pop(keys.index(key))]
        assert isinstance(arg, keytypes[key]), 'argument of wrong type- is {} when it should be {}'.format(type(arg), keytypes[key])
    assert len(keys) == 0, 'missing keys from extent argument - {}'.format(keys)

def check_tuple(tup):
    assert len(list(tup)) == 2, 'tuples must be of size 2'
    assert isinstance(tup[0], int) and isinstance(tup[1], int) and tup[1] > tup[0], 'tuple must contain two integers, and the second must be larger'

def check_cpt_args(args):
    args = copy.copy(args)
    keys = ['transform_predictand', 'tailoring', 'cca_modes', 'x_eof_modes', 'y_eof_modes', 'crossvalidation_window', 'synchronous_predictors', 'scree', 'drymask', 'validation']
    keytypes = {'transform_predictand': str, 'tailoring': str, 'cca_modes': tuple, 'x_eof_modes': tuple, 'y_eof_modes': tuple, 'crossvalidation_window': int, 'synchronous_predictors': bool, 'drymask': bool, 'scree': bool, 'validation': str}
    for key in args.keys():
        assert key in keys, 'illegal extent key - {}'.format(key)
        if args[key] is None: 
            args[key] = 'None'
        arg = args[keys.pop(keys.index(key))]
        assert isinstance(arg, keytypes[key]), 'argument of wrong type- is {} when it should be {}'.format(type(arg), keytypes[key])
        if keytypes[key] == tuple: 
            check_tuple(arg)


def save_configuration(fname, download_args2, cpt_args2, MOS, predictors, predictand): 
    if MOS is None:
        MOS = "None"
    for predictor in predictors:
        assert predictor in dl.hindcasts.keys() and predictor in dl.forecasts.keys(), 'illegal predictor - {}'.format(predictor)
    assert predictand in dl.observations.keys(), 'illegal predictand - {}'.format(predictand)
    assert MOS in ['CCA', 'PCR', 'None'], 'Illegal MOS selection - {}'.format(MOS)

    download_args = copy.copy(download_args2)
    cpt_args = copy.copy(cpt_args2)

    check_download_args(download_args)
    check_cpt_args(cpt_args)

    tosave = {'MOS': MOS, 'predictors': predictors, 'predictand': predictand}

    # convert illegal json types to legal json types 
    for key in cpt_args.keys():
        if isinstance(cpt_args[key], tuple): 
            cpt_args[key] = [cpt_args[key][0], cpt_args[key][1]]
        elif cpt_args[key] is None: 
            cpt_args[key] = 'None'
        elif isinstance(cpt_args[key], dt.datetime):
            cpt_args[key] = cpt_args[key].strftime('%Y-%m-%d')
    
    for key in download_args.keys():
        if isinstance(download_args[key], tuple): 
            download_args[key] = [download_args[key][0], download_args[key][1]]
        elif download_args[key] is None: 
            download_args[key] = 'None'
        elif isinstance(download_args[key], dt.datetime):
            download_args[key] = download_args[key].strftime('%Y-%m-%d')
    
    tosave['download_args'] = download_args
    tosave['cpt_args'] = cpt_args 
    
    import cptcore as cc 
    import cptio as cio 
    from . import __version__

    tosave['cptio_version'] = cio.__version__
    tosave['cptdl_version'] = dl.__version__
    tosave['cptcore_version'] = cc.__version__
    tosave['cptextras_version'] = __version__
 

    with open(fname, 'w') as f: 
        json.dump(tosave, f, indent=4, sort_keys=True)
    
    return fname 




def load_configuration(fname): 
    with open(fname, 'r') as f: 
        to_unpack = json.load(f)


    import cptcore as cc 
    import cptio as cio 
    from . import __version__

    assert to_unpack['cptio_version'] == cio.__version__, "Environment not compatible with configuration - config requires {} but you have {}".format(to_unpack['cptio_version'], cio.__version__)
    assert to_unpack['cptdl_version'] == dl.__version__, "Environment not compatible with configuration - config requires {} but you have {}".format(to_unpack['cptdl_version'], dl.__version__)
    assert to_unpack['cptcore_version'] == cc.__version__, "Environment not compatible with configuration - config requires {} but you have {}".format(to_unpack['cptcore_version'], cc.__version__)
    assert to_unpack['cptextras_version'] == __version__, "Environment not compatible with configuration - config requires {} but you have {}".format(to_unpack['cptextras_version'], __version__)

    MOS = to_unpack['MOS']
    if MOS == 'None':
        MOS = None 
    assert MOS in [ 'CCA', 'PCR', None]

    for predictor in to_unpack['predictors']:
        assert predictor in dl.hindcasts.keys() and predictor in dl.forecasts.keys(), 'illegal predictor - {}'.format(predictor)
    assert to_unpack['predictand'] in dl.observations.keys(), 'illegal predictand - {}'.format(predictor)

    predictors = to_unpack['predictors']
    predictand = to_unpack['predictand']
    
    cpt_args = to_unpack['cpt_args']
    download_args = to_unpack['download_args']



    # convert illegal json types to legal json types 
    for key in cpt_args.keys():
        if cpt_args[key] == 'None': 
            cpt_args[key] = None
        if key =='fdate' and isinstance(cpt_args[key], str):
            cpt_args[key] = dt.datetime.strptime(cpt_args[key],  '%Y-%m-%d')
        if key in ['cca_modes', 'x_eof_modes', 'y_eof_modes'] and isinstance(cpt_args[key], list): 
            cpt_args[key] =  tuple(cpt_args[key])
    
    for key in download_args.keys():
        if download_args[key] == 'None': 
            download_args[key] = None
        if key =='fdate' and isinstance(download_args[key], str):
            download_args[key] = dt.datetime.strptime(download_args[key],  '%Y-%m-%d')
 
    check_download_args(download_args)
    check_cpt_args(cpt_args)

    return MOS, download_args, cpt_args, predictors, predictand
