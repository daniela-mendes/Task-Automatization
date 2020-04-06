import sys


#########################
### A: AGENT BEHAVIOR ###
#########################

def average(task, memoryFactor):
	if len(task) == 1: #only speculative utility
		return task[0][1]
	else:
		num = 0.0
		denom = 0.0
		for i in range(1, len(task)):
			num += (float(task[i][1]) * (task[i][0]**memoryFactor))
			denom += task[i][0]**memoryFactor
		return round(num/denom,4)


class Agent:
	def __init__(self, options):
		self.restart = 0
		if len(options) == 4: #autonomous agent
			self.cycle = int((options[0].split('='))[1])
			self.decision = (options[1].split('='))[1]
			self.restart = int((options[2].split('='))[1])
			self.memoryFactor = float((options[3].split('='))[1])

		else: #len(options) = 6 because multi-agent system
			self.cycle = int((options[0].split('='))[1])
			self.agents = (((options[1].split('='))[1])[1:-1]).split(',')
			self.decision = (options[2].split('='))[1]
			self.restart = int((options[3].split('='))[1])
			self.memoryFactor = float((options[4].split('='))[1])
			self.concurrencyPenalty = int((options[5].split('='))[1])

		self.cycles_left = self.cycle
		self.decide_task = 0 # 0 when no new task; 1 when new/need-update task and goes back to zero after knowing which task to perform
		self.restart_time = self.restart
		self.task_to_perform = () #for perceive(self, input) ----- {'T0': ((A1),(A2),(A3)), 'T1': ((A1),(A2),(A3)), ...}
		self.gain = 0 #gain = gains for each task of each agent
		self.state = {} #state = tasks and utilities of the agent


	def perceive(self, input): # is it 'A' or 'Tx u=y'
		if self.decision == 'rationale':
			if input[0] == 'A':
				self.gain += float((input.strip().split('='))[1]) #strip() removes newline character at the end of the string
				self.state[self.task_to_perform[0]] += ((self.cycle-self.cycles_left,(input.strip().split('='))[1]),)
			else: #input[0] = 'T'
				self.state[(input.strip().split(' '))[0]] = ((0,(input.strip().split('='))[1]),)

		elif self.decision == 'heterogeneous-society':
			if input[0] == 'A':
				self.gain += float((input.strip().split('='))[1]) #strip() removes newline character at the end of the string
				self.state[self.task_to_perform[0]][input.strip().split(' ')[0][1:]-1] += ((self.cycle-self.cycles_left,(input.strip().split('='))[1]),)
				
			else: #input[0] = 'T'
				self.state[(input.strip().split(' '))[0]] = ()
				for i in range(len(self.agents)): #speculative utilities of tasks are the same for all agents
					self.state[(input.strip().split(' '))[0]] += ((0,(input.strip().split('='))[1]),),


	def decide_act(self): #which task shold the agent perform
		if self.decision == 'rationale':
			if len(self.task_to_perform) > 0:
				previous_task = (self.task_to_perform[0],self.state[self.task_to_perform[0]])
			else:
				previous_task = ()

			if self.cycles_left >= self.restart: #in this case, since I have enough steps/cycles left, I have to look into the tasks' utilities
				self.task_to_perform = ('T0',self.state['T0'])
				for task in self.state.items(): # para ver a melhor task
					if task[0] != 'T0':
						if (float(average(task[1], self.memoryFactor)) > float(average(self.task_to_perform[1], self.memoryFactor))):
							self.task_to_perform = task

		elif self.decision == 'heterogeneous-society':
			if len(self.task_to_perform) > 0:
				previous_task = (self.task_to_perform[0],self.state[self.task_to_perform[0]])
			else:
				previous_task = ()

			if self.cycles_left >= self.restart: #in this case, since I have enough steps/cycles left, I have to look into the tasks' utilities
				self.task_to_perform = ('T0',self.state['T0'])
				for task in self.state.items(): # para ver a melhor task
					if task[0] != 'T0':
						for i in range(len(self.agents)):
							if(float(average(task[1][i], self.memoryFactor)) > float(average(self.task_to_perform[1][i], self.memoryFactor))):
								self.task_to_perform[i] = task,

		if self.restart == 0:
			self.cycles_left -= 1
			return

		if self.decision == 'rationale':
			expected_to_perform = float(average(self.task_to_perform[1], self.memoryFactor))*(self.cycles_left-self.restart)
			if len(previous_task) > 0:
				expected_previous = float(average(previous_task[1], self.memoryFactor))*(self.cycles_left-self.restart_time)
			else:
				expected_previous = float('-inf')
		elif self.decision == 'heterogeneous-society':
			for i in range(len(self.agents)):
				expected_to_perform = float(average(self.task_to_perform[1][i], self.memoryFactor))*(self.cycles_left-self.restart)
				if len(previous_task) > 0:
					expected_previous = float(average(previous_task[1][i], self.memoryFactor))*(self.cycles_left-self.restart_time)
				else:
					expected_previous = float('-inf')


		if (expected_previous > expected_to_perform) or (expected_previous == expected_to_perform and int(previous_task[0][1:]) <= int(self.task_to_perform[0][1:])):
			self.task_to_perform = previous_task
			if self.restart_time != 0:
				self.restart_time -=1
		else:
			self.restart_time = self.restart - 1
		
		self.cycles_left -= 1


	def recharge(self):
		output = "{"
		for task in self.state.items():
			if len(task[1]) > 1: #len = 1 means that that task was never executed (only has 1 tuple, which corresponds to the speculative utility)
				output += task[0] + '=' + ("{:.2f}".format(float(average(task[1], self.memoryFactor))))
			else:
				output += task[0] + '=NA'

			if list(self.state.keys())[-1] != task[0]:
				output += ','

		output += "} "

		return ("state=" + output + "gain=" + str(("{:.2f}".format(self.gain))))


#####################
### B: MAIN UTILS ###
#####################

line = sys.stdin.readline()
agent = Agent(line.split(' ')) #line = list with every 'word'/character separated
for line in sys.stdin:
	if line.startswith("end"): break
	elif line.startswith("TIK"): agent.decide_act()
	else: agent.perceive(line)
sys.stdout.write(agent.recharge()+'\n');



