#!/usr/bin/env python2.7

import work_queue
import sys
import getopt

LENGTH = 4
HASHES = "hashes.txt"
TASKS = int(5000)
SOURCES = ("hulk.py", HASHES)
PORT = 9982

# Utility Functions


# Main Execution

if __name__ == '__main__':

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

	for _ in range(TASKS):
		command = './hulk.py -l {} -s {}'.format(LENGTH, HASHES)
		task = work_queue.Task(command)

		for source in SOURCES:
			task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)

		queue.submit(task)

	while not queue.empty():
		task = queue.wait()
		if task and task.return_status == 0:
			sys.stdout.write(task.output)

		

