
from mpi4py import MPI
from repast4py import context as ctx
from repast4py import core,schedule
from repast4py import random as repastrandom
from typing import Tuple
import random as pyrandom

verboseFlag=True
#verboseFlag=False
#agents_counter=0
numberOfAgentsInEachRank = 5
stopAt=4
allRanks=0
agentsToBeRequested=[]
messagesAfterInteraction=[]

class WLagent(core.Agent):
    TYPE = 0
    def __init__(self, local_id: int, rank: int, money: float):
        super().__init__(id=local_id, type=WLagent.TYPE, rank=rank)
        self.rank=rank
        self.money = money
        self.counterpartTuple=None
        if verboseFlag: print("hello from WL agent "+str(self.id)+" I am in rank "+str(rank)+" my money holding is "+str(self.money))
        #global agents_counter
#    def walk(self):
#        self.pt+=repastrandom.default_rng.random()-0.5
#        self.pt+=repastrandom.default_rng.normal()
#        print("  walked: walker "+str(self.id)+" I am in rank "+str(self.rank)+" my new position is "+str(self.pt)+" uid "+str(self.uid))
    def set_counterpart(self):
        counterpartRank=repastrandom.default_rng.choice(allRanks)
        counterpartID=repastrandom.default_rng.integers(numberOfAgentsInEachRank,size=1)[0]
#        counterpartTuple=(counterpartID,0,counterpartRank)
        self.counterpartTuple=(1,0,counterpartRank)
        print('agent',self.uid,'requests',self.counterpartTuple)
        if self.uid[2]!=counterpartRank:
            #does not ask for an agent already requested
            if (self.counterpartTuple,counterpartRank) in agentsToBeRequested:
                print('sorry this agent was already in the LIST')
                counterpartTuple=None
            else:
                agentsToBeRequested.append((self.counterpartTuple,counterpartRank))
    def interact(self):
        if self.counterpartTuple[2]==self.uid[2]:
            print('local interaction')
    def save(self) -> Tuple:
        return (self.uid,self.money)


def restore_agent(agent_data: Tuple):
    tupleFromSaveFunction=agent_data
    uid=tupleFromSaveFunction[0]
    money=tupleFromSaveFunction[1]
    tmp = WLagent(uid[0],uid[2],money)
    return tmp

class Model:
#    def __init__(self, comm: MPI.Intracomm, params: Dict):
    def __init__(self, comm: MPI.Intracomm):
        self.comm=comm
        size = comm.Get_size()
        rank = comm.Get_rank()
        self.size=size
        self.rank=rank
        # create the schedule
        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_event(0,self.createAgents)
        self.runner.schedule_repeating_event(1, 1, self.step)
        self.runner.schedule_stop(stopAt)
#        self.runner.schedule_end_event(self.at_end)
        # create the context to hold the agents and manage cross process
        # synchronization
        self.context = ctx.SharedContext(comm)
        #create random seed for processes
        #by setting this seed random numbers will be the same in different runs
        #comment the following line if you want different results in different runs
        if verboseFlag: print('===================================')
        pyrandom.seed(59302785)
        seeds=[]
        for i in range(size):
            seeds.append(pyrandom.randint(1,1000000))
        repastrandom.init(seeds[rank])
        if verboseFlag: print()
        if verboseFlag: print("Random seed "+str(repastrandom.seed))

        global allRanks
        allRanks=list(range(size))

        
        self.allRanks=list(range(size))
        #getting knowledge of other ranks
        otherRanks=list(range(size))
        #remove my rank from the list
        otherRanks.pop(rank)
        if verboseFlag: print("rank "+str(rank)+" says: ranks different from mine are "+str(otherRanks))
        self.otherRanks=otherRanks

    def createAgents(self):
        if verboseFlag: print('====== start create agents ======')
        rank=self.rank
        #create a WLagents
        for i in range(numberOfAgentsInEachRank):
            awl=WLagent(i,rank,1)
            #add the walker to the context
            self.context.add(awl)
        if verboseFlag: print('====== end create agents ======')

    def step(self):
        tick=self.runner.tick()
        activeRank=tick % self.size
        #activeRank=0
        counterpartRank=repastrandom.default_rng.choice(self.allRanks)
        #next variable will allow point-to-point communication below in the code
        chosenFromOtherRanks=False
        interactionBetweenRanks=False
#        print('-- tick '+str(tick)+' active r '+str(activeRank)+' self r '+str(self.rank)+' receiving rank '+str(counterpartRank))
        ##active rank choose his agent and another agent to interact with
        global agentsToBeRequested
        agentsToBeRequested=[]
        if self.rank == activeRank:
            if verboseFlag: print('updating rank '+str(self.rank)+' at tick '+str(tick)+' active rank '+str(activeRank))
            localAgentID=repastrandom.default_rng.integers(numberOfAgentsInEachRank,size=1)[0]
            aWL=self.context.agent((localAgentID,0,self.rank))
            for aWL in self.context.agents():
                aWL.set_counterpart()
            print(agentsToBeRequested)
        self.context.request_agents(agentsToBeRequested,restore_agent)
        print('rank',str(self.rank))
        print('ghosts',self.context._agent_manager._ghost_agents)
        print('ghosted',self.context._agent_manager._ghosted_agents)
        #if fully parallel leaves only a ghost
        global messagesAfterInteraction
        messagesAfterInteraction=[]
        if self.rank == activeRank:
            for aWL in self.context.agents():
                aWL.interact()
        


    def start(self):
        if verboseFlag: print("hello, I am going to run the start function")
        #self.runner.execute()
        if verboseFlag:
            if verboseFlag: print("start function performed!")
            if verboseFlag: print()
        pass
#            print('===================================')
#            print()
    def run(self):
        self.runner.execute()

def run():
    model = Model(MPI.COMM_WORLD)
    model.start()
    model.run()

if __name__ == "__main__":
    run()
