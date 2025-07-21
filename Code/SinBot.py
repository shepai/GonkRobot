import ulab.numpy as np
import random
class sinBot:
    def __init__(self, num_legs=2, num_motors_per_leg=2, dt=0.1,imu=False):
        self.num_legs = num_legs
        self.num_motors = num_legs * num_motors_per_leg  # 12 motors total
        self.dt = dt  # Time step for integration
        self.leg_geno=np.array([random.randrange(-100,100)/100 for i in range(3)]) #np.random.uniform(-1,1,(3))
        self.hip_geno=np.array([random.randrange(-100,100)/100 for i in range(3)])
        self.phase=np.array([random.randrange(-100,100)/100 for i in range(4)])#np.random.uniform(-1,1,(4))
        self.geno=np.concatenate((self.hip_geno,self.leg_geno,self.phase))
        self.t=0
    def get_positions(self,inputs,motors=None):
        degrees=np.degrees(self.step(imu_feedback=inputs, velocity_feedback=0))*10
        degrees=np.clip(degrees,0,40)
        #degrees[[2,5,8,11]]=degrees[[1,4,7,10]]
        #degrees[3:9]=-degrees[3:9] #try running this 
        return degrees
    def step(self, imu_feedback, velocity_feedback=0):
        motor_positions=[]
        for i in range(self.num_legs):
            H=self.hip_geno[0]*np.sin(self.hip_geno[1]*self.t - self.phase[i]) + self.hip_geno[2]
            L=self.leg_geno[0]*np.sin(self.leg_geno[1]*self.t - self.phase[i]) + self.leg_geno[2]
            motor_positions.append([H,L])
        self.t+=self.dt
        motor_positions=np.array(motor_positions).flatten()
        return np.array([motor_positions[1],motor_positions[0],motor_positions[3],motor_positions[2]]).flatten()
    def mutate(self,rate=0.2):
        probailities=np.array([random.randrange(0,100)/100 for i in range(self.geno.shape[0])])
        indices = [i for i in range(len(probailities)) if probailities < rate]
        val=np.array([random.randrange(-100,100)/100 for i in range(len(indices))])
        self.add(indices,self.geno,val)#np.random.normal(0,4,self.geno[np.where(probailities<rate)].shape)
        self.set_genotype(self.geno)
    def add(self,indices,array1,array2):
        for i in range(len(indices)):
            array1[indices[i]]+=array2[i]
        return array1
    def equal(self,indices,array1,array2):
        for i in range(len(indices)):
            array1[indices[i]]=array2[indices[i]]
        return array1
    def sex(self,geno1,geno2,prob_winning=0.6):
        probabilities=np.array([random.randrange(0,100)/100 for i in range(len(self.geno))])#np.random.random(len(self.geno))
        indices = [i for i in range(len(probabilities)) if probabilities < prob_winning]
        self.equal(indices,geno2.geno,geno1.geno)
        geno2.set_genotype(geno2.geno)
        return geno2
    def set_genotype(self, values):
        self.t=0
        self.hip_geno=values[0:4]
        self.leg_geno=values[4:8]
        self.phase=values[8:]
        self.hip_geno=np.clip(self.hip_geno,-4,4)
        self.leg_geno=np.clip(self.leg_geno,-4,4)
        self.phase=np.clip(self.hip_geno,-1,1)

if __name__=="__main__":
    a=sinBot()
    print(a.step(0,0))
    a.mutate()
    a.sex(a,a)
    demo_geno=np.array([-0.04198164,  0.90918552, -4.65281121, -2.22457433, -0.22812124,  3.07819192,
                        -0.21745877, -0.47165101,  2.15240473, -1.02080081])
    a.set_genotype(demo_geno)


