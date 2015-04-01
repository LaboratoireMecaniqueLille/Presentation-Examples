import time
import command as cmd
import graphe
import IOcomedi as ioc
from multiprocessing import Process, Pipe#, Array, Value
import command as cmd

#----------Parameters-----------
acquisition_step=100
saving_step=1
log_file='/home/corentin/Bureau/log.txt'

#---------- Acquisition function-----------
def receiving(pipe_send_sensor,pipe_send_time):
  t0=time.time()
  i=-1000
  while True:
    t,value=sensor.get()
    out.set_(i)
    pipe_send_sensor.send(value)
    pipe_send_time.send(t-t0)
    i+=1
    if i>2000:
      i=-1000

   
#------------ Opening Pipes ---------

pipe_send_sensor , pipe_recv_sensor = Pipe()
pipe_send_time, pipe_recv_time = Pipe()
pipe_send, pipe_recv=Pipe()
pipe_send2, pipe_recv2=Pipe()

try:
  sensor=ioc.In(device='/dev/comedi0', subdevice=0, channel=0, range_num=0, gain=1, offset=0)
  out=ioc.Out(1,1,1,device='/dev/comedi0', subdevice=1, channel=0, range_num=0, gain=0.5, offset=0)
  Receiving=Process(target=receiving, args=(pipe_send_sensor,pipe_send_time))
  Compactor=Process(target=cmd.pipe_compactor,args=(acquisition_step,[[pipe_send,1],[pipe_send2,1]],pipe_recv_time,pipe_recv_sensor))
  Graph=Process(target=graphe.graph,args=(pipe_recv,['time',0,1,0,2],['values',0,1,['Time (s)', 'Effort mV)']])) #['values',0,1,3,4,['Time (s)', 'Effort mV)']]
  Save=Process(target=cmd.save,args=(pipe_recv2,saving_step,log_file))

  Receiving.start()
  Compactor.start()
  Graph.start()
  Save.start()
  
  Receiving.join()
  Compactor.join()
  Graph.join()
  Save.join()


except (KeyboardInterrupt): 

  Receiving.terminate()
  Compactor.terminate()
  Graph.terminate()
  Save.terminate()

    