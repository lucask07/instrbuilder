import itertools
import pytest
import instrbuilder
from instrbuilder.instrument_opening import open_by_address

init_file_loc = instrbuilder.__file__
instrument_cmds = init_file_loc.replace('__init__.py', 'instruments/')
print('Instrument commmands (csv files) are at: {}'.format(instrument_cmds))

# create an unconnected instrument for testing 
addr = {'no_interface': 'no_address'}
test_instr = open_by_address(addr = addr, csv_dir = instrument_cmds, 
                            csv_folder = 'tester', instr_class = 'TestInstrument')

def test_idn():
    """ test instrument ID get """
    # if _unconnected_val is unspecified will return the getter_debug_val
    test_instr._cmds['id']._unconnected_val = 'instr_tester'
    assert test_instr.get('id') == test_instr._cmds['id']._unconnected_val

def test_time_div_set(capsys):
    """ test set command without configs dictionary """
    test_instr.set('time_range', 0.1)
    captured = capsys.readouterr()
    assert captured.out == ':TIM:RANG 0.1\n'

def test_trig_level_set(capsys):
    """ test set command with a configs dictionary """
    chan = 1
    value = 0.5
    expected = ':TRIG:LEV {}, CHAN{}\n'.format(value, chan)
    test_instr.set('trigger_level', value,
                    configs = {'chan': chan})
    captured = capsys.readouterr()
    assert captured.out == expected

def test_time_div_get(capsys):
    """ test get that does and should return a float """
    value = 0.77
    #first set it 
    test_instr.set('time_range', value) # in SCPI.py this set _unconnected_val 
    get_value = test_instr.get('time_range')
    assert get_value == value

def test_wrong_type_get(capsys):
    """ test that if a get returns an unexpected value 
        that the returned value is None """
    #first set it 
    test_instr._cmds['time_range']._unconnected_val = 'wrong-type'
    get_value = test_instr.get('time_range')
    assert get_value == None

# test lookup function -- set
def test_trigger_slope_lookup_set(capsys):
    """ test set command with a lookup table mapping configs dictionary """
    test_instr.set('trigger_slope', 'EITHER')
    captured = capsys.readouterr()
    assert captured.out == ':TRIG:SLOP EITH\n'

# test lookup function -- get (converts to long-form)
def test_trigger_slope_lookup_get(capsys):
    """ test set command with a lookup table mapping configs dictionary """
    test_instr.set('trigger_slope', 'EITH')
    captured = capsys.readouterr()
    get_value = test_instr.get('trigger_slope')
    assert get_value == 'EITHER'

# test lookup function -- set (omitted long form should be OK)
def test_trigger_slope_lookup_omit_set(capsys):
    """ test set command with a lookup table mapping configs dictionary """
    test_instr.set('trigger_slope', 'EITH')
    captured = capsys.readouterr()
    assert captured.out == ':TRIG:SLOP EITH\n'

