
from mpi4py import MPI
from repast4py import context as ctx
from repast4py import core,schedule
from repast4py import random as repastrandom
from typing import Tuple
import random as pyrandom

verboseFlag=True
#verboseFlag=False
#agents_counter=0

class WLagent(core.Agent):
    TYPE = 0
    def __init__(self, local_id: int, rank: int, money: float):
        super().__init__(id=local_id, type=WLagent.TYPE, rank=rank)
        self.rank=rank
        self.money = money
        if verboseFlag:
            print("hello from walker "+str(self.id)+" I am in rank "+str(rank)+" my position is "+str(self.money))
        #global agents_counter
        #walker_counter+=1
#    def walk(self):
#        self.pt+=repastrandom.default_rng.random()-0.5
#        self.pt+=repastrandom.default_rng.normal()
#        print("  walked: walker "+str(self.id)+" I am in rank "+str(self.rank)+" my new position is "+str(self.pt)+" uid "+str(self.uid))
    def save(self) -> Tuple:
        return self.uid

#agent_cache = {}

def restore_agent(agent_data: Tuple):
    uid=agent_data
    tmp = Walker(uid[0],uid[2],0.0)
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
        self.runner.schedule_stop(2)
#        self.runner.schedule_end_event(self.at_end)
        # create the context to hold the agents and manage cross process
        # synchronization
        self.context = ctx.SharedContext(comm)
        #create random seed for processes
        #by setting this seed random numbers will be the same in different runs
        #comment the following line if you want different results in different runs
        print('===================================')
        pyrandom.seed(59302785)
        seeds=[]
        for i in range(size):
            seeds.append(pyrandom.randint(1,1000000))
        repastrandom.init(seeds[rank])
        print()
        print("Random seed "+str(repastrandom.seed))
        
        self.allRanks=list(range(size))
        #getting knowledge of other ranks
        otherRanks=list(range(size))
        #remove my rank from the list
        otherRanks.pop(rank)
        print("rank "+str(rank)+" says: ranks different from mine are "+str(otherRanks))
        self.otherRanks=otherRanks


#        print("setting agents to be requested to other ranks")

#        ghostsToRequest=[]
#        ghostsToRequest.append(((0,0,otherRanks[0]),rank))
#        ghostsToRequest.append(((0,0,otherRanks[0]),otherRanks[0]))
#        ghostsToRequest.append(((0,0,otherRanks[1]),otherRanks[1]))

#        print(ghostsToRequest)
#        obtained_ag=self.context.request_agents(ghostsToRequest,restore_agent)
#        print(agent_cache)
#        print(obtained_ag)
#        print(self.context._agent_manager._ghosted_agents)
#        print(self.context._agent_manager._ghost_agents)

#        print(self.context.projections)
#        print(self.context.bounded_projs)
#        print(self.context.non_bounded_projs)

    def createAgents(self):
        print('====== start create agents ======')
        rank=self.rank
        #create a WLagents
        for i in range(5):
            awl=WLagent(i,rank,1)
            #add the walker to the context
            self.context.add(awl)
        print('====== end create agents ======')

    def step(self):
        tick=self.runner.tick()
        activeRank=tick % self.size
        counterpartRank=repastrandom.default_rng.choice(self.allRanks)
        #next variable will allow point-to-point communication below in the code
        chosenFromOtherRanks=False
        interactionBetweenRanks=False
#        print('-- tick '+str(tick)+' active r '+str(activeRank)+' self r '+str(self.rank)+' receiving rank '+str(counterpartRank))
        ##active rank choose his agent and another agent to interact with
        if self.rank == activeRank:
            print('updating rank '+str(self.rank)+' at tick '+str(tick)+' active rank '+str(activeRank))
            localAgentID=repastrandom.default_rng.integers(5,size=1)[0]
            aWL=self.context.agent((localAgentID,0,self.rank))
            counterpartID=repastrandom.default_rng.integers(5,size=1)[0]
            counterpartTuple=(counterpartID,0,counterpartRank)
            if self.rank == counterpartRank:
                if localAgentID == counterpartID:
                    otherAgentsIDs=list(range(5))
                    otherAgentsIDs.pop(localAgentID)
                    counterpartID=repastrandom.default_rng.choice(otherAgentsIDs)
                    counterpartTuple=(counterpartID,0,counterpartRank)
                print('local interaction in rank ',str(activeRank),': agent ',localAgentID,' interacts with agent ',counterpartID)
                aSecondLocalWL=self.context.agent(counterpartTuple)
                moneySum=aWL.money+aSecondLocalWL.money
                print('sum of money holdings ',moneySum)
                share=repastrandom.default_rng.random()
                print('share ',share)
                localAgentMoney=moneySum*share
                secondLocalAgentMoney=moneySum-localAgentMoney
                print('money to local agent ',localAgentMoney,' money to second local agent ',secondLocalAgentMoney)
                aWL.money=localAgentMoney
                aSecondLocalWL.money=secondLocalAgentMoney
                print('The two local agents money was updated')
            else:
                interactionBetweenRanks=True
                print('local agent '+str(aWL.uid)+' interact with '+str(counterpartTuple))
            #add the sender rank id to allow point to point communication below
            tupleToSend=(counterpartTuple,activeRank,interactionBetweenRanks)
            #because destination rank is random, we have to send to all ranks except the active one.
            for aRank in self.otherRanks:
                self.comm.send(tupleToSend,aRank)

        ##All the remote ranks receive info from active rank. The selected rank get the agent, watch his money and send the information to the active rank
        else:
            #print('tick '+str(tick)+' active r '+str(activeRank)+' self r '+str(self.rank)+' receiving rank '+str(counterpartRank))
            data=self.comm.recv(source=activeRank)
            print('tick '+str(tick)+' active r '+str(activeRank)+' self r '+str(self.rank)+' received data '+str(data))
            agTuple=data[0]
            interactionBetweenRanks=data[2]
            if agTuple[2]==self.rank:
                chosenFromOtherRanks=True
                talkingWith=data[1]
                print('this agent is in my rank, talking with rank ',talkingWith)
                tmpWL=self.context.agent(agTuple)
                self.comm.send(tmpWL.money,talkingWith)
                print('information sent to rank ',str(talkingWith),' money ',tmpWL.money)
        ##Active rank receive info on money from the remote rank
        if self.rank == activeRank and interactionBetweenRanks:
            recWallet=self.comm.recv(source=counterpartRank)
            print('information received from rank ',counterpartRank,': money = ',recWallet)
            moneySum=aWL.money+recWallet
            print('sum of meoney holdings ',moneySum)
            share=repastrandom.default_rng.random()
            print('share ',share)
            localAgentMoney=moneySum*share
            remoteAgentMoney=moneySum-localAgentMoney
            print('money to local agent ',localAgentMoney,' money to remote agent ',remoteAgentMoney)
            aWL.money=localAgentMoney
            print("local agent's money updated")
            self.comm.send(remoteAgentMoney,counterpartRank)
            print("remote agent's money info sent to rank ", counterpartRank)
        ##Remote rank receive information from active rank and update his agents's money
        else:
            if chosenFromOtherRanks and interactionBetweenRanks:
                newMoney=self.comm.recv(source=talkingWith)
                print('Information received from rank ',talkingWith,' money ',newMoney)
                tmpWL.money=newMoney
                print('agent ',str(agTuple),' money updated')

    def start(self):
        if verboseFlag:
            print("hello, I am going to run the start function")
        #self.runner.execute()
        if verboseFlag:
            print("start function performed!")
            print()
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