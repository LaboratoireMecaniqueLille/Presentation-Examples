import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.family'] = 'serif' # Allows your script to be Jean-Francois-proof
#ps aux | grep python 					 # KILL python process ...
#kill -9 insert_here_the_python_thread_number		 # ... try it if ximea won't open again.
plt.close('all')
import os
import command as cmd
import graphe
np.set_printoptions(threshold='nan', linewidth=500)
from multiprocessing import Process, Pipe, Array, Value
import sys

############################## Parameters #############################################

save_directory="/home/corentin/Bureau/" # path to save repository. 
acquisition_step=50 #Define how many points the compactor waits before saving them
saving_step=1 # Allows you to save 1 point every "saving step": use this parameter for high frequencies and long durations.
save_file= save_directory+"log.txt"

############################## Set origin of time for synchronisation #################

t_0=time.time()
print "t0 = ", t_0
time_0=[t_0]
np.savetxt(save_directory+"t0.txt",time_0) # allows one to manually set the original time and thus keep the same timebase even if the test is interrupted

############################## Pipes Creation #########################################

time_pipe_send, time_pipe_recv = Pipe()
F_pipe_send, F_pipe_recv= Pipe()
dep_pipe_send, dep_pipe_recv = Pipe()
cycle_pipe_send,cycle_pipe_recv=Pipe()
eps_pipe_send, eps_pipe_recv=Pipe()

# the following Pipes are for the output of the compactor
pipe_send,pipe_recv=Pipe()
pipe_send2,pipe_recv2=Pipe()

############################## Create your functions here #############################

def data_acquisition(t_0): # This dummy function send data to 4 differents pipes | t_0 as argument allow the time synchronisation
  i=0
  while True: # Put an infinite loop to keep sending data
    t=time.time()
    time_pipe_send.send(t-t_0) # sending time to the compactor
    F_pipe_send.send(i) # sending force to the compactor
    eps_pipe_send.send(20*np.sin(i/10.)) # sending force to the compactor
    dep_pipe_send.send((i%30)-15) # sending force to the compactor
    i+=1
    time.sleep(0.01) # I put this in this example to avoid too many data
    
############################## Create your Process here ############################### 
    
try: # This loop allows one to handle exceptions, such as Errors or KeyboardInterrupt
  
  Data_acquisition=Process(target=data_acquisition,args=(t_0,)) 
  
  Compactor=Process(target=cmd.pipe_compactor,args=(acquisition_step,[[pipe_send,1],[pipe_send2,1]],time_pipe_recv,F_pipe_recv,eps_pipe_recv,dep_pipe_recv))
# args of the compactor: 
    # acquisition_step: how many values it stack before sending the matrix
    # [[pipe_1,n_1],[pipe_2,n_2],...,[pipe_x,n_x]] : define wich pipes the compactor use for sending the output matrix, and it sends 1 out of n lines of the matrix. It can be usefull if you have high frequency and don't want to plot everything
    # list of all the input Pipe that the Compactor will read : the output comes in the same order than the input
  Save=Process(target=cmd.save,args=(pipe_recv,saving_step,save_file))
  
  Graph=Process(target=graphe.graph,args=(pipe_recv2,['time',0,1],['time',0,2,0,3],['values',0,2,0,3,["time(s)","random unit"]]))
  

  
############################## Start your Process here ################################ 


  Data_acquisition.start()
  Compactor.start()
  Save.start()
  Graph.start()


####


  Data_acquisition.join()
  Compactor.join()
  Save.join()
  Graph.join()



except (KeyboardInterrupt): # If KeyboardInterrupt, this loop is activated
################ This part is used to terminate the processes once they are done. DO NOT FORGET this part or the process will keep running on your computer.

  Data_acquisition.terminate()
  Compactor.terminate()
  Save.terminate()
  Graph.terminate()
  print "terminated"
  
  
############################## How to re-open my saved data? ################################ 
#data=np.loadtxt(save_directory+'log.txt',usecols=(1,2,3,4),comments=(']')) # Only change the usecols parameters, 1 being your first column (not 0)

############################## How to use the shared variables ? ################################ 
### Shared Array:
#shared_array=Array('f', 4) #create a shared array of float ('f'), and of length 4
#shared_array.acquire() # get the associated Lock
#data=shared_array[:] # copy data
#shared_array[0]=118.163210 # change the first number of the shared array
#shared_array.release() # release the Lock 

### Shared Value:
#shared_value=Value('i',0) # create a shared value of type integer ('i') and set initial value to 0
#shared_value.acquire() # get the associated Lock
#data=shared_value.value # copy data
#shared_value.value=210 # change the shared value
#shared_value.release() # release the Lock