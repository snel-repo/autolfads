##Tmux
'Tmux' is a terminal multiplexer allowing the user to access multiple separate terminal sessions inside a single terminal window. This allows us to run run LFADS w/ PBT without fear of accidentally closing the terminal and ending the run prematurely. 

Here are some important commands that allow use to navigate to and from the tmux terminal with the LFADS w/ PBT run.

* When you are in the 'tmux' terminal (green bar at the bottom), press ```^b``` (ctrl-b) and then ```d``` to detach from the tmux terminal. 

* When you have detached, you can reattach with the following line ```tmux a -t <name>``` with name being the tmux session name. 

* When you are detached and want to instead look at the actual states of the clients, you can use the following command:
```tmux -L pbt_server a -t lf*0```.

For a list of quick commands with tmux, use the [tmux cheat sheet](https://gist.github.com/MohamedAlaa/2961058)
...



