
from mpi4py import MPI
from repast4py import context as ctx
from repast4py import core,schedule
from repast4py import random as repastrandom
import random as pyrandom
import matplotlib.pyplot as plt

#verboseFlag=True
verboseFlag=False
if verboseFlag:
    N=3
    iterations=10
else:
    N=2400
    iterations=200


context=None


class WLagent(core.Agent):
    TYPE = 0
    def __init__(self, local_id: int, rank: int, money: float):
        super().__init__(id=local_id, type=WLagent.TYPE, rank=rank)
        self.rank=rank
        self.money = money
        self.counterpart_tuple=None
        if verboseFlag:
            print("hello from WL agent "+str(self.id)+" I am in rank "+str(rank)+" my money holding is "+str(self.money))
    def set_counterpart(self):
        n_WLagents=context.size([WLagent.TYPE])
        upper_bound=n_WLagents[WLagent.TYPE]
        counterpart_id=repastrandom.default_rng.integers(0,high=upper_bound,size=1)[0]
        #avoid self exchanges
        #print(self.id==counterpart_id)
        #print(counterpart_id)
        if int(self.id)==int(counterpart_id):
            self.counterpart_tuple=None
        else:
            self.counterpart_tuple=(counterpart_id,WLagent.TYPE,self.rank)
    def interact(self):
        if self.counterpart_tuple:
            if verboseFlag: print(str(self.uid)+" exchanging with "+str(self.counterpart_tuple))
            theCounterpart=context.agent(self.counterpart_tuple)
            moneySum=self.money+theCounterpart.money
            if verboseFlag: print('sum of money holdings ',moneySum)
            share=repastrandom.default_rng.random()
            if verboseFlag: print('share ',share)
            localAgentMoney=moneySum*share
            theCounterpartMoney=moneySum-localAgentMoney
            if verboseFlag: print('money to local agent ',localAgentMoney,' money to second local agent ',theCounterpartMoney)
            self.money=localAgentMoney
            theCounterpart.money=theCounterpartMoney
            #if verboseFlag: print("Local agents' money holdings updated")
        else:
            if verboseFlag: print(str(self.uid)+" self exchanges are not allowed")


class Model:
#    def __init__(self, comm: MPI.Intracomm, params: Dict):
    def __init__(self, comm: MPI.Intracomm):
        # create the schedule
        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_repeating_event(1, 1, self.step,priority_type=schedule.PriorityType.BY_PRIORITY,priority=1.0)
        #self.runner.schedule_repeating_event(1, 1, self.check,priority_type=schedule.PriorityType.BY_PRIORITY,priority=1.5)
        self.runner.schedule_end_event(self.report)
        self.runner.schedule_stop(iterations)
#        self.runner.schedule_end_event(self.at_end)
        # create the context to hold the agents and manage cross process
        # synchronization
        global context
        context = ctx.SharedContext(comm)
        #create random seed for processes
        seed=pyrandom.randint(1,1000000)
        repastrandom.init(seed)
        self.rank = comm.Get_rank()
        print("Random seed "+str(repastrandom.seed))
        #create agents
        for i in range(N):
            awl=WLagent(i, self.rank, 1.0)
            #add walker to the context
            context.add(awl)

    def step(self):
        for aWL in context.agents():
            aWL.set_counterpart()
            aWL.interact()
    def check(self):
        for aWL in context.agents():
            print('tick',str(self.runner.tick()),'agent',str(aWL.uid),' my money holding is ',str(aWL.money))
    def report(self):
        finalMoney=[]
        for aWL in context.agents():
            finalMoney.append(aWL.money)
        print(sum(finalMoney))
        if not verboseFlag:
            plt.hist(finalMoney,200);
            plt.show()


    def start(self):
        if verboseFlag:
            print("hello from the start method")
        self.runner.execute()

def run():
    model = Model(MPI.COMM_WORLD)
    model.start()

if __name__ == "__main__":
    run()
