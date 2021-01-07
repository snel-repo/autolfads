##Overview
The rest of this tutorial focuses on showing a step-by-step example run on training an LFADS model w/ PBT on Google Cloud Platform. This tutorial goes through the steps of how to prepare your data, train an LFADS model using TPUs on Google Cloud Platform, download the data back to your local computer, and then finally run a post-processing step on the data. 

In this example run we use sample Lorenz data, and you can follow along using either this same sample Lorenz data or by using your own neural data. However, note this tutorial is ONLY usable for binned neural spikes in the format ```[Neurons x Trial Length x Num Trials]``` in a .mat file.

##Download Tutorial Repo
The first step is downloading the tutorial files onto your local computer, either by downloading the zip file [here](google.com) or using the commmand ```github clone github.com```

This tutorial contains utilities for preparing and post-processing your data, as well as the sample Lorenz data we will be running through LFADS. If you are using your own .mat neural data instead of the sample Lorenz data, copy your neural  spiking data into the ```tutorial``` folder.

##Convert ```.mat``` to ```.h5``` <a href="https://cpandar.github.io/lfads-pbt/setup/#prepare-data-walkthrough"><img src="../img/vidicon.png" alt="IMAGE ALT TEXT HERE" width="20" height="auto" border="10" /></a>

!!! tip
    Any section in this tutorial that contains a <img src="../img/vidicon.png" alt="IMAGE ALT TEXT HERE" width="20" height="auto" border="10" /> image has a corresponding video walkthrough.

Preparing your data involves partitioning your data into testing and validation sets, and then converting that data from a .mat file to .h5 file. We use a simple matlab utility to accomplish this. 
 
###Using Your Own Data
If you are planning on going through this tutorial using sample Lorenz data, you can skip to the next [section](setup/#run-h5-conversion-script).

Else, if you are planning on using your own data, first make sure your data is in the downloaded ```tutorial``` directory. 

!!! warning 
	Your neural spiking data MUST be in the format ```Neurons x Trial Length x Num Trials``` in a .mat file

Then, open the ```example_script.m``` file. We have to just make some slight modifications to point the script towards your data. (Again, these modifications are only necessary if you are using your only data and not sample Lorenz data). 

First, on ```line 2```, you should edit the line to read ```spikes = load('your_data.mat');``` with your_data.mat being the path to your neural spiking data. You can then delete the entire ```line 3```. To be edited.

###Run ```.h5``` Conversion Script 
Open the ```example_script.m``` in Matlab.

Run the first two cells of the example_script. This should prepare the data, creating the .h5 file with validation and training sets. 

####Prepare Data Walkthrough

<video width="100%" height="auto" controls loop>
  <source src="../media/preparedatagyf.mp4" type="video/mp4">
</video>

##Accessing Google Cloud Platform
Go to [https://console.cloud.google.com/](https://console.cloud.google.com/) and sign in with your Google account. 

If this is your first time logging into Google Cloud Platform, first we need to create a project. Navigate to the ['Compute Engine'](https://console.cloud.google.com/compute) and then fill out the details needed to create a project.

Next, you have to link your account to a billing account by entering a credit card. Navigate back to the ['dashboard'](https://console.cloud.google.com) and then click 'Billing,' located on the right side. Now we are ready to start a run.

!!! info
    Pricing Details!! Pricing Details!! Free trial
    https://cloud.google.com/tpu/docs/pricing

