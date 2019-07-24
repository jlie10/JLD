#!/usr/bin/env python##############################################################################
# Sacrifice       www.dessalles.fr/Evolife              Jean-Louis Dessalles #
#                 Telecom Paris  2019                    www.dessalles.fr    #
# together with Julien Panis-Lie                                             #
##############################################################################


""" Could self-sacrifice therefore have a biological function? This project sets the groundwork for investigating the (individual) biological motivations that may underlie self-sacrifice (which need not coincide with its moral motivations, potentially geared towards the collective).
"""



import sys
import random
import time	# for sleep

sys.path.append('../../..')
import Evolife.Tools.Tools as ET
# import Evolife.Other.SocialNetwork.SocialSimulation as SSim
import Evolife.Ecology.Observer as EO
import Evolife.Ecology.Individual as EI
import Evolife.Ecology.Group as EG
import Evolife.Ecology.Population as EP
import Evolife.Ecology.Alliances as EA
import Evolife.Scenarii.Default_Scenario as EDS
import Evolife.QtGraphics.Evolife_Window as EW

class Scenario(EDS.Default_Scenario):
	""" Implement a scenario here, by instantiating Default_Scenario.
		See documentation in Default_Scenario.py to see how.
	"""
	
	def __init__(self):
		EDS.Default_Scenario.__init__(self, Name='Sacrifice', CfgFile='___Sacrifice.evo') # loads 'Sacrifice.evo'
		
	def genemap(self):
		return [('Readiness', 8)]	# Readiness to display patriotism
	
	def phenemap(self):
		""" Defines the set of non inheritable characteristics """
		return ['Patriotism', 'Risk']
			
	def display_(self):
		return [('blue', 'Readiness', 'Readiness to display patriotism'), 
				 ('green', 'Risk', 'Risk taking'),
				 ('red', 'NbSuicides', '# suicides per year'),
				 ]

	def initialization(self):
		self.NbSuicides = 0	# keeps track of suicides
		
	def start_game(self, members):
		for indiv in members:
			for child in indiv.Children.copy():
				if not child in members:	# child is dead
					indiv.Children.remove(child)
					continue
				for sibling in indiv.Children:
					if not sibling in members:	# sibling is dead
						continue
					if sibling != child:	
						child.Siblings.add(sibling)	
		self.NbSuicides = 0	# keeps track of suicides
		super().start_game(members)
		
	def prepare(self, indiv):
		indiv.update_()

	def evaluation(self, indiv):
		# if Obs.Visible():	print('%d-%d' % (len(indiv.Children), len(indiv.Siblings)), end=' ', flush=True) 
		if indiv.suicide():	# most resolute individual may commit suicide
			self.NbSuicides += 1

	def end_game(self, members):
		self.NbSuicides /= self['PopulationSize']
		
	def update_positions(self, members, groupLocation):
		for indiv in members:	
			indiv.location = (groupLocation + indiv.Phene_value('Patriotism'), 
				# indiv.Phene_value('Risk'), 'blue', 6)
				indiv.score(), 'blue', 6)

	# # # def parenthood(self, RankedCandidates, Def_Nb_Children):
		# # # Candidates = super().parenthood(RankedCandidates, Def_Nb_Children)
		# # # # filtering out individuals with score==0 ("dead" by suicide)
		# # # return [C for C in Candidates if C[0].score() > 0]

	def new_agent(self, child, parents):
		" initializes newborns - parents==None when the population is created"
		for P in parents: P.Children.add(child)	# let know parents who is their child
		return True
		 
	def Field_grid(self):	
		return [(0, 98, 'green', 1, 100, 98, 'green', 1), (100, 100, 1, 0)]
		
		
class Individual(EI.EvolifeIndividual):
	"   class Individual: defines what an individual consists of "

	def __init__(self, Scenario=None, ID=None, Newborn=False, maxQuality=100):
		super().__init__(Scenario=Scenario, ID=ID, Newborn=Newborn)
		# if not Newborn:	self.Phene_value('Patriotism', 100.0 * int(self.ID) / maxQuality) 
		self.Children = set()
		self.Siblings = set()
		self.Phene_value('Risk', 0)
		self.score(100, FlagSet=True)
		
	def update_(self):
		self.Phene_value('Risk', self.Phene_value('Patriotism') * self.gene_relative_value('Readiness') / 500.0)
		# if Obs.Visible():	
			# print((self.Phene_value('Patriotism'), self.gene_relative_value('Readiness') ), flush=True)

	def suicide(self):
		if self.score() > 0 and random.randint(0, 100) < self.Phene_value('Risk'):
			self.score(0, FlagSet=True)
			#self.LifePoints = -1 # TEST
			# let children benefit from suicide
			for child in self.Children:	child.score(self.Scenario['ChildrenBonus'])
			for sibling in self.Siblings:	sibling.score(self.Scenario['SiblingBonus'])
			return True
		return False
	
class Group(EG.EvolifeGroup):
	" Calls local class when creating individuals "
		
	def createIndividual(self, ID=None, Newborn=True):
		# calling local class
		return Individual(self.Scenario, ID=self.free_ID(Prefix=''), Newborn=Newborn)

		
class Population(EP.EvolifePopulation):
	" Calls local class when creating group "

	def createGroup(self, ID=0, Size=0):
		return Group(self.Scenario, ID=ID, Size=Size)	# local class

	
if __name__ == "__main__":
	Gbl = Scenario()
	Obs = EO.EvolifeObserver(Gbl)
	Pop = Population(Scenario=Gbl, Evolife_Obs=Obs)
	if Gbl['BatchMode'] == 0:	print(__doc__)
	
	# launching windows
	# See Evolife_Window.py for details
	Capabilities='FGCP'	# F = 'Field'; G = 'Genomes'; C = 'Curves'; 
	Views = []
	if 'F' in Capabilities:	Views.append(('Field', 500, 350))	# start with 'Field' window on screen
	if 'T' in Capabilities:	Views.append(('Trajectories', 500, 350))	# 'Trajectories' on screen
	Obs.recordInfo('DefaultViews',	Views)	# Evolife should start with these window open
	EW.Start(SimulationStep=Pop.one_year, Obs=Obs, Capabilities=Capabilities, 
		Options=[('Background','green11')])
	time.sleep(1.1)


__author__ = 'Dessalles'
