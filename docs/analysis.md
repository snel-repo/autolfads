##Overview
!!! info
    Estimated time for section: **30 min**

The following section details downloading the results from Google Cloud, and then running several analysis scripts.

##Downloading Data From GCP <a href="https://cpandar.github.io/lfads-pbt/analysis/#download-data-walkthrough"><img src="../img/vidicon.png" alt="IMAGE ALT TEXT HERE" width="20" height="auto" border="10" /></a>
Once LFADS w/ PBT has finished running, we can now download the data back to our local computer for analysis.

!!! warning
    At this point, you can stop all your machines (server and clients). Information on stopping machines can be found [here](https://cpandar.github.io/lfads-pbt/setupAddInfo/#stopping-starting-vms) 

To download data from the bucket, navigate back to [https://console.cloud.google.com/storage](https://console.cloud.google.com/storage).

Click on the newly created zip file, and then click 'Download.' The output of the run should now be downloaded to your local computer.

##Post Processing <a href="https://cpandar.github.io/lfads-pbt/analysis/#post-process-walkthrough"><img src="../img/vidicon.png" alt="IMAGE ALT TEXT HERE" width="20" height="auto" border="10" /></a>
Now that you have downloaded the data back to your local computer, open up the tutorial package ([download here](files/tutorial_package.zip))

Open up `pbt_plot.m` in Matlab. First, set the tutorial_package to your current working folder. 

Then, inside the `pbt_plot.m` script, we need to set the `data_folder` variable to the location of your `pbt_run` folder, which is located inside the `run` folder you downloaded. For instance, on my computer its `C:\\Users\tutorial\output\runs\pbt_run`.

Set the `output_folder` variable to the folder where you want the plots generated. 

Run the `pbt_plot.m` script. This script will show the evolution of HPs over successive generations. These are some of the plots we got from the tutorial run. 

![keep_prob](img/keep_prob.png)

![kl_co_weight](img/kl_ic_weight.png)

![l2 gen scale](img/l2_gen_scale.png)

![learning rate init](img/learning_rate_init.png)

##Compare to true rates

!!! note
    This section is only for users using a synthetic dataset (as in the tutorial_package) where ground truth is available. 

If you used the synthetic dataset derived from Lorenz, then we can compare to the true rates.

First, open the `compare_rates.m` script in the tutorial package. Fill in the first `lfads_output_dir` with the address of the `lfads_output` which is located inside your `run` folder. For instance, on my computer its `C:\\Users\tutorial\output\runs\lfads_output`.

Then, you can run the script, which will generate R^2 value, which represents the error in the inferred rates compared to the true rates, as well as plot the inferred rates of several example neurons against their true underlying rates.

![d](img/r2_output.PNG)

The following plot was generated from this tutorial's run.

![img](img/compare_rates_output.PNG) 
