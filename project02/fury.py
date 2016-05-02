#!/usr/bin/env python2.7

import work_queue
import sys
import getopt

ALPHABET = string.ascii_lowercase + string.digits
LENGTH = 4
HASHES = "hashes.txt"
TASKS = int(5000)
SOURCES = ("hulk.py", HASHES)
PORT = 9982

# Utility Functions


# Main Execution

if __name__ == '__main__':

	try:
		with open('journal.json', 'r') as fp:
		JOURNAL = json.load(fp)
	except OSError:
   	JOURNAL = 0

	try:
		options, arguments = getopt.getopt(sys.argv[1:], "l:p:")
	except getopt.GetoptError as e:
		usage(1)

	for option, value in options:
		if option == "-l":
			LENGTH = int(value)
		elif option == "-p":
			PORT = int(value)
	
	queue = work_queue.WorkQueue(PORT, name = "fury-owen", catalog = True)
	queue.specify_log("fury.log")

	for pre in ALPHABET:
		command = './hulk.py -l {} -s {} -p {}'.format(LENGTH - 1, HASHES, pre)
		if command not in JOURNAL:
			task = work_queue.Task(command)

			for source in SOURCES:
				task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)
			queue.submit(task)

	while not queue.empty():
		task = queue.wait()
		if task and task.return_status == 0:
			sys.stdout.write(task.output)
			sys.stdout.flush()

		JOURNAL[task.command] = task.output.split()
		with open('journal.json.new', 'w') as stream:
		    json.dump(JOURNAL, stream)
		os.rename('journal.json.new', 'journal.json')

		

