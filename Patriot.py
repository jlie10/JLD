#!/usr/bin/env python##############################################################################
# Patriot       www.dessalles.fr/Evolife              Jean-Louis Dessalles #
#                 Telecom Paris  2019                    www.dessalles.fr    #
# together with Julien Panis-Lie                                             #
##############################################################################


""" Emergence of conspicuous patriotism under treason risk.
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
import Evolife.QtGraphics.Evolife_Batch  as EB
 

class Scenario(EDS.Default_Scenario):
    """ Implement a scenario here, by instantiating Default_Scenario.
        See documentation in Default_Scenario.py to see how.
    """
    
    def __init__(self):
        EDS.Default_Scenario.__init__(self, Name='Patriot', CfgFile='___Patriot.evo') # loads 'Patriot.evo'
        
    def genemap(self):
        return [('DemandForPatriotism', 8),		# signal level expected from acquaintances
                ('PatriotSignal', 8),			# signal level if patriot
                ('NonPatriotSignal', 8),		# signal level if non-patriot
                ]
    
    def phenemap(self):
        """ Defines the set of non inheritable characteristics """
        return ['Patriotism']	# determines whether one is patriot or not
            
    def display_(self):
        return [('blue', 'PatriotSignal', 'signal level if patriot'), 
                 ('green', 'DemandForPatriotism', 'signal level expected from acquaintances'),
                 ('red', 'NonPatriotSignal', 'signal level if non-patriot'),
                 ]

    def prepare(self, indiv):
        # print('.', end='', flush=True)
        indiv.score(100, FlagSet=True)
        
    def interaction(self, indiv, partner):
        " Interaction between individuals "
        PerceivedSignal = ET.noise_mult(partner.signal(), self['Noise'])
        PartnerPerceivedSignal = ET.noise_mult(indiv.signal(), self['Noise'])
        
        #indiv.get_friend(PerceivedSignal, partner, PartnerPerceivedSignal)
        # Suppression du gene Demande : bruit ??? 
        #return
        if PerceivedSignal >= indiv.demand() and PartnerPerceivedSignal >= partner.demand():
            indiv.acquainted(partner)
        
    def evaluation(self, Indiv):
        " Score changes due to friends & traitors "
        # signalling cost
        Indiv.signalCost()
        # friends get rewarded for having a friend or penalized for being acquainted with a traitor 
        Solidarity = 0	# benefit from having friends
        for Friend in Indiv.Friends():
            if Friend.traitor():	
                Friend.score(self['TraitorBenefit'])
                Indiv.score(-self['TreasonImpact'])
                Solidarity = 0
                break	# one treason only
            else:
                # cumulative contribution of friends with saturation (varies from 0 to 100)
                Solidarity = 100 - (100 - Solidarity) * (100 - self['FriendImpact']) / 100.0
        Indiv.score(-self['LonelinessPenalty'] + Solidarity * self['Solidarity'] / 100.0)
        # penalty for remaining alone
        # if Indiv.nbFriends() == 0:
            # Indiv.score(Indiv.score() / self['LonelinessPenalty'])
     
    def lives(self, members):
    #	" converts scores into life points "
    	super().lives(members)
        # correction to make negative scores die
    	for indiv in members:
    		if indiv.score() < 0:	indiv.LifePoints = -1
        ### REMARQUE : sans ceci, l'équilibre obtenu ressemble davantage aux prédictions / à mes résultats.


    def update_positions(self, members, groupLocation):
        for indiv in members:	
            indiv.location = (groupLocation + indiv.Phene_value('Patriotism'), 
                # indiv.score(), 'blue', 6)
                indiv.signal(), 'blue', 6)
         
    def Field_grid(self):	
        return [(0, 98, 'green', 1, 100, 98, 'green', 1), (100, 100, 1, 0)]
        

class Individual(EI.EvolifeIndividual):
    "   class Individual: defines what an individual consists of "

    def __init__(self, Scenario, ID=None, Newborn=False):
        super().__init__(Scenario=Scenario, ID=ID, Newborn=Newborn, 
                            MaxFriends=Scenario['MaxFriends'])
        self.Signal = -1
        self.Traitor = None
        
    def patriot(self):
        return self.Phene_value('Patriotism') > 100 - self.Scenario['PatriotRatio']
        
    def traitor(self):
        if self.Traitor is None:
            self.Traitor = False
            if not self.patriot():	
                # Non-patriot have a probability of turning into traitors
                self.Traitor = random.randint(0,100) < self.Scenario['TreasonProbability']
        return self.Traitor
    
    def signal(self):
        " computes signal level "
        if self.Signal < 0:
            if self.patriot():	self.Signal = self.gene_relative_value('PatriotSignal')
            else:	
                self.Signal = min(self.gene_relative_value('NonPatriotSignal'),
                    self.Scenario['TraitorMaxSIgnal'])
        return self.Signal

    def signalCost(self):
        " paying signalling cost "
        #self.score(-self.Scenario['SignallingCost'] * self.signal() / 100.0)		# signalling cost

        if self.patriot(): self.score(-self.Scenario['SignallingCost'] * self.signal() / 100.0)	
        else: self.score(-self.Scenario['SignallingCost'] * self.gene_relative_value('NonPatriotSignal') / 100.0)	
            ######### MODIF 2: cosmetique

    def demand(self):
        return self.gene_relative_value('DemandForPatriotism')
    
class Group(EG.EvolifeGroup):
    " Calls local class when creating individuals "
        
    def createIndividual(self, ID=None, Newborn=True):
        # calling local class
        return Individual(self.Scenario, ID=self.free_ID(Prefix=''), Newborn=Newborn)

        
class Population(EP.EvolifePopulation):
    " Calls local class when creating group "

    def createGroup(self, ID=0, Size=0):
        return Group(self.Scenario, ID=ID, Size=Size)	# local class

    def season_initialization(self):
        for gr in self.groups:
            for agent in gr:
                # agent.lessening_friendship()	# eroding past gurus performances
                if self.Scenario['EraseNetwork']:	agent.forgetAll()
                agent.reinit()
        
    ### ADDED : for launching multiple experiences using BatchMode
def Start(Gbl = None, PopClass = Population, ObsClass = None, Capabilities = 'FGCNP'):
    " Launch function "
    if Gbl == None: Gbl = Scenario()
    if ObsClass == None: Observer = EO.EvolifeObserver(Gbl)	# Observer contains statistics
    Pop = PopClass(Gbl, Observer)
    BatchMode = Gbl.Parameter('BatchMode')
    if BatchMode:
        EB.Start(Pop.one_year, Observer)
    else:
        Views = []
        if 'F' in Capabilities:	Views.append(('Field', 500, 350))	# start with 'Field' window on screen
        if 'T' in Capabilities:	Views.append(('Trajectories', 500, 350))	# 'Trajectories' on screen
        if 'N' in Capabilities:	Views.append(('Network', 500, 150))	# 'Network' on screen
        Observer.recordInfo('DefaultViews',	Views)	# Evolife should start with these window open
        EW.Start(Pop.one_year, Observer, Capabilities=Capabilities, Options=[('Background','green11')])
    if not BatchMode:	print("Bye.......")
    time.sleep(2.1)	
    return


if __name__ == "__main__":
    print(__doc__)

    #############################
    # Global objects			#
    #############################
    Gbl = Scenario()
    Start(Gbl)

__author__ = 'Dessalles'
