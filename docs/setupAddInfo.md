##Stopping, Starting VMs
Leaving VMs running can lead to unintended high bills. VMs can be stopped, deleted, and starting in the [compute engine](https://console.cloud.google.com/compute) by clicking the checkbox to the left of the VM and clicking start/stop/delete buttons at the top of the list of VMs.

![stop machines](img/stop_machines.png)

##Cloud Shell
Many of the commands needed to set-up infrastructure are done using Google Cloud Shell. While the commands needed are listed directly in the tutorial, further information on navigating/using cloud shell can be found here: [https://cloud.google.com/shell/docs/using-cloud-shell](https://cloud.google.com/shell/docs/using-cloud-shell).

Typical commands used for an AutoLFADS or RADICaL run are entering directories with `cd`, copying git repos with `git clone`, and running shell scripts with `sh`.

##Choosing number of clients
In essence, each client VM can have 2-3 workers running on it, and the more total workers means a wider search for optimal hyperparameters. Thus, the more client VMs we create when setting up a run, the wider search for optimal hyperparameters. 

In general for most mid-sized datasets, having 24 workers usually will lead to finding optimal HPs. In this tutorial, we create 8 client VMs, which allows use of 24 workers. This number can be adjusted if the dataset is larger or smaller.

##Allocating Clients Between Multiple Zones
If your AutoLFADS or RADICaL run involves a significant number of different client machines, but you lack the GPU quota in a single region, you can allocate these over a number of regions.

For instance, if you want to create 8 clients machines, but only have a regional quota of 4 GPUs in either region, then you can create 4 in us-central1-c and 4 in us-east1-c by running the following commands consecutively.

`sh machine_setup.sh clientc 4 us-central1-c`

and then

`sh machine_setup.sh cliente 4 us-east1-c`

##Requesting additional GPU quota
Compute Engine enforces quota to prevent unforseen spikes in GPU usage. The quota enforces an upper bound on how many GPUs can be created in each zone. Thus, 24-48 hours before doing a run, you must make sure your quota allows you to have enough GPUs to run your client machines, and if not, request additional quota.
 
Generally, we need to increase our quota of 1) # of GPUs, 2) # of global GPUs, and 3) # of global CPUs.

In order to request quota, navigate to [https://console.cloud.google.com/iam-admin/quotas](https://console.cloud.google.com/iam-admin/quotas), open up the 'Metric' drop down menu, de-select all by clicking 'none.'

First, scroll down to find an appropriate GPU that you will be attaching to your virtual machines. The user can choose any GPU that suits their purpose; the default one used in this tutorial is NVIDIA K80 GPU. Note, the selected GPU works well as 'normal' type, not 'committed' (higher costs) or 'preemptible' (short-lived VMs).

Select the chosen GPU, and then scroll down to the specific region you want to increase quota in. Once you select it, click the 'Edit Quotas,' and fill in the information.

To follow this tutorial exactly, you need at least 4 NVIDA K80 GPUs in us-central1-c, and 4 NVIDIA K80 GPUs in us-east1-c.

<video width="100%" height="auto" controls loop>
<source src="../media/autoLFADS/quota.mp4" type="video/mp4">
</video> 

Next, we want to increase the number of global GPUs. You can deselect all `metrics` again, and then find `GPUs (all regions)`. To follow this tutorial exactly, click `edit quota` and increase this to 8 (or greater).

![gpus](img/GPUs_all_regions.png)

Finally, we want to increase the number of global CPUs. You can deselect all `metrics` again, and then find `CPUs (all regions)`. To follow this tutorial exactly, click `edit quota` and increase this to 64 (or greater).

![cpus](img/CPUs_all_regions.png)             
