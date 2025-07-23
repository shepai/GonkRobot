import ulab.numpy as np
from CPML import *


class CTRNNQuadruped:
    def __init__(self, num_legs=4, num_motors_per_leg=3, dt=0.1,imu=False):
        self.num_legs = num_legs
        self.num_motors = num_legs * num_motors_per_leg  # 12 motors total
        self.dt = dt  # Time step for integration
        self.num_neurons=6
        #initialize CTRNN parameters
        self.tau = np.ones(self.num_neurons) * 0.5  # Time constants (modifiable via evolution)
        self.weights = normal(-1, 1, (self.num_neurons, self.num_neurons)) # Synaptic weights .normal(0,2,(self.num_neurons, self.num_neurons))#
        self.biases = np.zeros(self.num_neurons)  # Bias terms
        self.activations = np.zeros(self.num_neurons)  # Neuron activations
        self.outputs = np.zeros(self.num_neurons)  # Motor output (joint angles)

        #frequency and phase offsets for oscillatory behavior
        self.omega = normal(0.8, 1.2, (self.num_motors,))  # Oscillation frequencies
        self.phases = np.linspace(0, 2 * np.pi, self.num_motors, endpoint=False)  # Initial phase
        self.geno=np.concatenate((self.weights.flatten(),self.biases.flatten(),self.tau.flatten(),self.omega.flatten()))

        #IMU Feedback Gains (Proportional control for stability)
        self.Kp_imu = 0.5  # Adjusts hip based on tilt
        self.Kp_vel = 0.3  # Adjusts knee based on forward velocity
        self.height=1
        self.imu=imu
    def sigmoid(self, x):
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))
    def get_positions(self,inputs,motors=None):
        degrees=np.degrees(self.step(imu_feedback=inputs, velocity_feedback=0))/1.5
        degrees=np.clip(degrees,0,180)
        degrees[[2,5,8,11]]=degrees[[1,4,7,10]]
        degrees[3:9]=-degrees[3:9] #try running this 
        return degrees
    def step(self, imu_feedback):
        """Update the CTRNN for one timestep."""
        #imu_feedback = np.array(imu_feedback).flatten()
        # Create fixed input weights if not already done (move this to __init__ ideally)
        input_weights = np.random.uniform(-1, 1, (self.num_neurons, 3)) if self.imu else np.zeros((self.num_neurons, 3))

        # Project IMU feedback into neuron space
        sensory_drive = 0#input_weights @ imu_feedback  # shape: (num_neurons,)

        # Compute neural activations (discrete update of CTRNN)
        net_input = np.dot(self.weights,self.outputs) + self.biases + sensory_drive
        net_input = np.clip(net_input, -500, 500)
        self.activations += self.dt / self.tau * (-self.activations + net_input)
        #arr = np.array([1.0, float('nan'), float('inf'), -float('inf'), 2.0])
        #nan_mask = arr != arr
        #self.activations = arr * (~nan_mask)
        self.outputs = self.sigmoid(self.activations)

        # Add oscillatory gait modulation
        self.phases += self.dt * self.omega
        oscillation = np.sin(self.phases)

        # Compute motor commands (combine CTRNn output and oscillation)
        motor_commands = np.concatenate((self.outputs[0:3],self.outputs[0:3],self.outputs[0:3],self.outputs[0:3])) + 0.5 * oscillation
        return np.clip(motor_commands, 0, 1)*self.height  # Return motor positions (normalized)
    def set_genotype(self, values):
        """Set CTRNN parameters from an evolutionary genotype."""
        num_weights = len(self.weights.flatten())
        num_biases = len(self.biases.flatten())
        num_tau = len(self.tau.flatten())
        num_omega = len(self.omega.flatten())
        #assign genotype values to weights, biases, and time constants
        self.weights = values[0:num_weights].reshape(self.weights.shape)
        self.biases = values[num_weights:num_weights + num_biases]
        self.tau = values[num_weights + num_biases:num_weights + num_biases + num_tau].reshape(self.tau.shape)
        self.omega = values[num_weights + num_biases + num_tau: num_weights + num_biases + num_tau + num_omega].reshape(self.omega.shape)
        #apply value constraints
        self.biases = np.clip(self.biases, -16, 16)  # Cap bias values
        self.tau = np.maximum(self.tau, self.dt)  # Ensure time constants are above dt
        self.weights = np.clip(self.weights, -4, 4)  # Cap weight values
        self.omega = np.clip(self.omega, -1, 1)  # Cap weight values
        self.geno=np.concatenate([self.weights.flatten(),self.biases.flatten(),self.tau.flatten(),self.omega.flatten()])
    def mutate(self,rate=0.2):
        probailities=np.random.random(self.geno.shape)
        self.geno[np.where(probailities<rate)]+=np.random.normal(0,4,self.geno[np.where(probailities<rate)].shape)
        self.set_genotype(self.geno)
    def sex(self,geno1,geno2,prob_winning=0.6):
        probabilities=np.random.random(len(self.geno))
        geno2.geno[np.where(probabilities<prob_winning)]=geno1.geno[np.where(probabilities<prob_winning)]
        geno2.set_genotype(geno2.geno)
        return geno2
    
if __name__=="__main__":
    ctrnn=CTRNNQuadruped()
    for i in range(1000):
        print(ctrnn.step(0))
