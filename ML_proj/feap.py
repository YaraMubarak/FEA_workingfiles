import subprocess

def feap(filename, pressure, nlipid=1, ncalc=1):
	""" pressure: numerical value of pressure (in mmHG)
		filename: mesh file names and feap IO file name 
		nlipid: number of lipids
		ncalcium: number of calciums

		returns success flage (T/F) and output file name"""

	# read input
	with open('Iartery1', 'r') as fin:
		template = ''.join(fin.readlines())

	# edit with values
	template = template.replace('p = 133.33*90', 'p = %2.2f*133.33' % pressure)
	template = template.replace('N500_A1', filename)

	# generate lipds
	lipid1 = "! lipid\nmate "
	lipid2 = "\nsolid\nfinite\nucon,plaq\nc1m,50.0\nc2m,5.0\nuend\n\n"

	lipid = ''
	for i in range(nlipid):
		lipid = lipid + lipid1+str(i+4)+lipid2
	template = template.replace(lipid1+'4'+lipid2, lipid)

	# generate calcium
	calc1 = "! calcium\nmate "
	calc2 = "\nsolid\nfinite\nucon,plaq\nc1m,18804.5\nc2m,20.0\nuend\n\n"

	calc = ''
	for j in range(ncalc):
		calc = calc + calc1+str(4+nlipid+j)+calc2
	template = template.replace(calc1+'5'+calc2, calc)	

	# check for pressure (deprecated, using mate 100)
	# matenum = nlipid + ncalc + 3
	# if matenum > 9:
	# 	template = template.replace("mate 9\npres", "mate "+str(matenum+1)+"\npres")

	# write new input file
	fname = 'Iartery_'+filename
	with open(fname, 'w+') as fout:
		fout.writelines(template)

	# run feap
	run = subprocess.Popen(['source ../lib.sh; ../feap -i'+fname], stdout=subprocess.PIPE, shell=True)
	
	stdout, stderr = run.communicate()
	if 'REACHED END TIME' in stdout.decode():
		success = True
	else:
		success = False

	return success, 'O'+fname[1:]
