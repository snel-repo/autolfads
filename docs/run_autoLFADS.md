Now, we are ready to begin our run. All previous steps must be completed to this point. 

!!! warning
    Note that if you are doing an additional run, make sure that the folder you set your `run_path` to is completely empty. Also if you have a .zip file in your bucket named the same as your `run_path`, you must delete it before starting a new run.  

##Beginning AutoLFADS in tmux <a href=https://snel-repo.github.io/autolfads/run_autoLFADS/#walkthrough><img src="../img/vidicon.png" alt="IMAGE ALT TEXT HERE" width="20" height="auto" border="10" /></a>

First, make sure you're SSHed into your server VM. Then, make sure you're in the directory `autolfads/pbt_opt` directory. If not, you can navigate with the following command:

    cd autolfads/pbt_opt

Then, we want to make sure to begin our run in a tmux terminal. This allows us to exit from the SSH terminal without terminating our run.

First, type the following command into your SSH window (NOT cloud shell). 

    tmux

Then, making sure you're still in the `autolfads/pbt_opt` directory, run the following command to begin your AutoLFADS or RADICaL run.

    python2 pbt_script_multiVM.py 

Your run should begin. If any errors pop-up, double check that the Docker images are finished pulling on the client machines with `sh check.sh`, and that mongoDB is running with `service mongod status`. If prompted for an SSH keygen, just hit `enter` to accept the default keygen. 

!!! warning
    Active VMs can rack up costs when left unattended. Remember to shut them down when not in use. For information on how to stop, pause, and start VMs, go to this [section](../setupAddInfo/#stopping-starting-vms).

###Walkthrough
<video width="100%" height="auto" controls loop>
  <source src="../media/autoLFADS/autoLFADS_run.mp4" type="video/mp4">
</video> 

##Checking on your run
At this point, you can do whatever with your local machine (including closing the Google Cloud Platform in your browser). In order to check back in on your run, first navigate to [console.cloud.google.com/compute](https://console.cloud.google.com/compute) and then SSH back into your server. 

Once back in your server, we need to enter our tmux terminal. The command is:

    tmux a -t <tmux_session_name>

`tmux_session_name` is by default `0` if you didn't specify a name. You can also check all your tmux sessions with the command `tmux ls`. 

To detach from your tmux terminal, the command is `ctrl+b` and then `d`. 
