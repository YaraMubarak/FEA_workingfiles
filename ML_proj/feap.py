import subprocess

def feap(pressure, filename):
	""" pressure: numerical value of pressure (in mmHG)
		filename: mesh file names and feap IO file name 

		returns success flage (T/F) and output file name"""

	# read input
	with open('Iartery0', 'r') as fin:
		template = ''.join(fin.readlines())

	# edit with values
	template = template.replace('p = 133.33*90', 'p = %2.2f*90' % pressure)
	template = template.replace('N500_A2', filename)


	# write new input file
	fname = 'Iartery_'+filename
	with open(fname, 'w+') as fout:
		fout.writelines(template)

	# run feap
	run = subprocess.Popen(['./feap -i'+fname], stdout=subprocess.PIPE, shell=True)
	
	stdout, stderr = run.communicate()
	if stdout.decode()[-20:].strip()=='REACHED END TIME':
		success = True
	else:
		success = False

	return success, 'O'+fname[1:]

print(feap(70, 'N500_A1'))