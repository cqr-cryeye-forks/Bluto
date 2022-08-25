import re
import subprocess
import sys

from termcolor import colored

from .bluto_logging import info


def updateCheck(VERSION):
	command_check = ["pip list -o"]
	process_check = subprocess.Popen(command_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output_check = process_check.communicate()[0]
	line = output_check.splitlines()
	new_bluto_found = False
	new_version = None
	for i in line:
		if 'bluto' in str(i).lower():
			new_version = re.match(rb'Bluto\s\(.*\)\s-\sLatest:\s(.*?)\s\[sdist]', i)[1]
			new_bluto_found = True
	if new_bluto_found:
		info('Update Available')
		print(colored('\nUpdate Available!', 'red'), colored(f'{new_version}', 'green'))
		print(colored('Would you like to attempt to update?\n', 'green'))
		while True:
			answer = input('Y|N: ').lower()
			if answer in ('y', 'yes'):
				update()
				print('\n')
				break
			elif answer in ('n', 'no'):
				print('\n')
				break
			else:
				print(f'\nThe Options Are yes|no Or Y|N, Not {answer}')
	else:
		print(colored('You are running the latest version:', 'green'), colored(f'{VERSION}\n', 'blue'))


def update():
	command_check = (["pip install bluto --upgrade"])
	process_check = subprocess.Popen(command_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output_check = process_check.communicate()[0]
	lines = output_check.splitlines()
	info(lines)
	if 'Successfully installed' in lines[:-1]:
		print(colored('\nUpdated Successfully!', 'green'))
		sys.exit()
	else:
		print(colored('\nUpdate Failed, Please Check The Logs For Details', 'red'))
