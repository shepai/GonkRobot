import ulab.numpy as np
import random

class simple:
    def __init__(self,num_legs=2, num_motors_per_leg=2,dt=0.05,imu=False):
        self.pattern= np.array([[0 for i in range(4)] for i in range(10)])
        self.T=0
        self.dt=dt
        self.geno=self.pattern.flatten()
    def get_positions(self,inputs=0,motors=None):
        self.T+=self.dt
        if int(self.T)>=len(self.pattern): self.T=0
        return self.pattern[int(self.T)]
    def mutate(self,rate=0.2):
        probailities=np.array([random.randrange(0,100)/100 for i in range(self.geno.shape[0])])
        indices = [i for i in range(len(probailities)) if probailities < rate]
        val=np.array([random.randrange(-100,100)/100 for i in range(len(indices))])
        self.add(indices,self.geno,val)#np.random.normal(0,4,self.geno[np.where(probailities<rate)].shape)
        probailities=np.random.random(self.geno.shape)
        self.geno[np.where(probailities<rate)]=np.random.choice((-20,20,0),size=self.geno[np.where(probailities<rate)].shape)
        self.pattern=self.geno.reshape((10,4))
    def sex(self,geno1,geno2,prob_winning=0.6):
        probabilities=np.random.random(len(self.geno))
        geno2.geno[np.where(probabilities<prob_winning)]=geno1.geno[np.where(probabilities<prob_winning)]
        geno2.set_genotype(geno2.geno)
        return geno2
    def set_genotype(self,values):
        self.geno=np.array(values)
        self.pattern=self.geno.reshape((len(values)//4,4))
