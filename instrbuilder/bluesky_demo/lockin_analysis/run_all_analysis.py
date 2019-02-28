# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

'''
run all of the analysis code that produces each 
figure in the paper submitted to TIM

The folder without sqlite databases has many files. 
The OS file open limit may cause problems. 

SYSTEM SETUP: (in terminal MacOS or Ubuntu)
ulimit -Sn 4095

MATPLOTLIB figures require latex and dvipng

'''

import runpy
# tuple: name of analysis file, paper figure number
analysis_files = [('freq_res_sr810_analysis.py', 3), ('phase_res_ada2200_analysis.py', 4),
				  ('snr_sr810_analysis.py', 5), ('snr_ada2200_analysis.py', 6),
				  ('dynamic_reserve_sr810_analysis.py', 8), ('dynamic_reserve_ada2200_analysis.py', 9)]

for af in analysis_files:
	print('-'*60)
	print('Analysis file: {}'.format(af[0]))
	print('Paper figure: {}'.format(af[1]))
	print('-'*60)
	#exec(open('./{}'.format(af[0])).read())
	runpy.run_path(af[0])
