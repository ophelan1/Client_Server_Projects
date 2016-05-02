Project 02: Distributed Computing
Group: Owen Phelan
=================================
Describe the implementation of hulk.py. How does it crack passwords?

	hulk.py assumes that a password only contains letters and numbers. For a password length n, there are 36^n possible passwords (because every element can be any number or letter). hulk.py generates every single possible password. As it does, it hashes each password to see if it is a match to a line in "hashes.txt", and if it is, then that password is a match, and is printed to stdout. 

Explain how you tested hulk.py and verified that it works properly.

	I tested hulk.py by first printing out the possible passwords it was considering, to make sure that it was correctly iterating through every possibility. Once that was confirmed, I simply ran the program to see if it could find passwords from hashes.txt. As it ran correctly and found passwords of length 3, 4, and 5, and these passwords made sense, 

Describe the implementation of fury.py. How does it:

	Utilize hulk.py to crack passwords?

		fury.py submits the hulk.py command to the work_queue, and then when workers are submitted, they execute this command.

	Divide up the work among the different workers?

		fury.py breakes up the hulk.py task into sub-tasks, and runs these tasks simultaneously so that the program can run much faster. Instead of just running hulk.py for a password length l [ 36^N possibilities ], fury runs hulk.py for password length (l-1) [ 36^(N-1)possibilities ], with every possible prefix. That way, the same task is being completed in 36 different sub-tasks. 

	Keep track of what has been attempted?

		As each task is completed, the return status of the task (including the command) is added to a dictionary called JOURNAL. This dictionary is then saved to a json file. Upon opening, fury.py loads the json dictionary, if it exists, into the JOURNAL variable. The JOURNAL variable will therefore contain all the tasks that are already completed. Each new command (task), is checked against the dictionary, to see if it has already been run. If it has, there is no need to reexecute it, and the program moves on. 

	Recover from failures?
		
		fury.py keeps track of the return status of each task. If the return status is not 0, it will not add the output to the output.

Explain how you tested fury.py and verified that it works properly.

	I tested fury.py by running it on the student machines and using work_queue_status. I monitored as tasks were completed, and checked the PASSWORDS.txt file for the output. Unfortunately, I waited until too late (I know, there was even a warning!) as did a number of other students, so the tasks ran inredibly slowely. 

From your experience in this project and recalling your Discrete Math knowledge, what would make a password more difficult to brute-force: more complex alphabet or longer password? Explain.

	A longer password. Assuming 36 character, each added character makes a password 36x harder to brute-crack. This is much more significant than having a larger alphabet. That math is pretty simple, you would need to make the alphabet for a 1 character password 36 times larger to make that password as complex as a password with 2 "36-possibility" characters.

Please see the [distributed computing project] write-up.

[distributed computing project]: https://www3.nd.edu/~pbui/teaching/cse.20189.sp16/homework10.html
