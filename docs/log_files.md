Log files available after a run contain a variety of information on the run, including hyperparameter evolution, best workers, etc. This section briefly explores how to find and use these files.

##Where to find log files
Log files will show up in the [bucket](https://console.cloud.google.com/storage) you created. Then, enter the ```runs``` folder, and navigate to the created ```pbt_run``` folder.  Inside here, there exist two main types of log files, the first created from the server machine, and the second created from individual worker runs.

##Server log files
Immediately inside the ```pbt_run``` folder are the log files created by the server. They contain many important information related to overall output of the run.

Important log files include:

`best_worker.sofar`, which lists the best worker until that point in the run.

`best_worker.done`, which lists the best overall worker once the run is complete.

`decision_log.csv`, which shows the result of binary tournament for all workers in all generations. For more information on binary tournament, refer to the [binary tournament](../introductionAddInfo) section. 

`hp_log.csv`, which shows the evolution of HPs across all workers and all generations.
 
##Worker log files
Inside the ```pbt_run``` folder, there exist many folders to reach the specific worker in a specific generation, which follow the format ```gX_WY```, or Generation X, Worker Y. For instance, generation 3 worker 4 would have a full named `g003_w04`. We can navigate inside these specific workers folders to look at a variety of log files related to a specific worker's output.

These files include:

`hp_history.csv`, a history of the hyper-parameters for that worker (shows the HP evolution for the particular worker)

`gradnorms.csv`, the norm of the gradient in each epoch in that generation, for the worker

`perf_history.csv`, the performance history over all completed generations for that particular worker

`hyperparameters.txt`, the hyperparameters for the worker for that generation

`fitlog.csv`, the training and validation loss

and various model checkpoint files

##Client log files
Client log files log the output from each process, and any errors within the client will be recorded here.

To access these, go to the `client_log` folder which is inside the `run` folder. This is available only when the run is over. 
