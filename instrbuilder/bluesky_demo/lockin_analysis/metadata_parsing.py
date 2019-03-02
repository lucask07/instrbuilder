# Lucas J. Koerner
# 2019
# koerner.lucas@stthomas.edu
# University of St. Thomas

import datetime

def print_meta(header, script_name = ''):
    # start of the experiment: header['start']
    # end of the experiment: header['stop']
    print('-'*70)
    print('METADATA for: {}'.format(script_name))
    print('-'*70)

    print('Parsing metadata for UID: {}; with exit status: {}'.format(header.start['uid'], header.stop['exit_status']))
    # time of experiment
    print('Experiment start time: {}'.format(datetime.datetime.fromtimestamp(header.start['time']).strftime('%Y-%m-%d %H:%M:%S') ))
    # experiment duration
    print('Experiment duration: {} [seconds]'.format(header.stop['time'] - header.start['time']))

    # Bluesky plan info 
    print('Bluesky plan type: {} '.format(header.start['plan_type']))
    print('Bluesky plan name: {} '.format(header.start['plan_name']))

    try:
        # number of configuration keys
        print('Metadata has {} stored function generator configuration values'.format(len(list(header.start['fg_config']))))
        
        # names of instruments were changed during the experiments, fix here
        if 'fg_function' in header.start['fg_config'].keys():
            prefix = 'fg_'
        elif 'fgen_function' in header.start['fg_config'].keys():
            prefix = 'fgen_'
        else: 
            prefix = 'error'
        # example Function generator configuration values 
        print('Example FG config values:')
        for cfg_key in ['function', 'freq', 'v', 'offset', 'load']:
            print('  Config value: {} = {}'.format(cfg_key, header.start['fg_config'][prefix + cfg_key]['value']))
    except:
        print('This experiment does not have function generator configuration values')

    try:    
        # number of configuration keys
        print('Metadata has {} stored lock-in configuration values'.format(len(list(header.start['lia_config']))))
        print('Example lock-in config values:')
        
        # names of instruments were changed during the experiments, fix here
        if 'srs_lockin_freq' in header.start['lia_config'].keys():
            prefix = 'srs_'
        elif 'lockin_freq' in header.start['lia_config'].keys():
            prefix = ''
        else: 
            prefix = 'error'
        for cfg_key in ['lockin_freq', 'lockin_tau', 'lockin_in_config', 'lockin_sensitivity']:
            print('  Config value: {} = {}'.format(cfg_key, header.start['lia_config'][prefix + cfg_key]['value']))
    except:
        print('This experiment does not have SRS lockin configuration values')

    try:
        # number of configuration keys
        print('Metadata has {} stored ADA2200 configuration values'.format(len(list(header.start['ada2200_config']))))
        print('Example ADA2200 config values:')
        for cfg_key in ['ADA2200_sync_control', 'ADA2200_clock_config']:
            print('  Config value: {} = {}'.format(cfg_key, header.start['ada2200_config'][cfg_key]['value']))
    except:
        print('This experiment does not have ADA2200 configuration values')

    # Multimeter 
    try:
        # number of configuration keys
        print('Metadata has {} stored DMM configuration values'.format(len(list(header.start['dmm_config']))))
        print('Example DMM config values:')
        
        # names of instruments were changed during the experiments, fix here
        if 'dmm_curr_bw' in header.start['dmm_config'].keys():
            prefix = 'dmm_'
        elif 'my_multi_curr_bw' in header.start['dmm_config'].keys():
            prefix = 'my_multi_'
        else: 
            prefix = 'error'

        for cfg_key in ['volt_range', 'volt_aperture', 'trig_source']:
            print('  Config value: {} = {}'.format(cfg_key, header.start['dmm_config'][prefix + cfg_key]['value']))
    except:
        print('This experiment does not have Multimeter configuration values')

    # Power Supply
    try:
        # number of configuration keys
        print('Metadata has {} stored power supply configuration values'.format(len(list(header.start['pwr_config']))))
        print('Example Power Supply config values:')

        for cfg_key in ['rigol_pwr1_v', 'rigol_pwr1_i']:
            print('  Config value: {} = {}'.format(cfg_key, header.start['pwr_config'][cfg_key]['value']))
    except:
        print('This experiment does not have Power Supply configuration values')    

    print('-'*70)
    print('END METADATA')
    print('-'*70)