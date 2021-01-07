This section talks briefly about the cloud services which we will be employing. Note that this section is just a brief overview of running autoLFADS on the cloud, and step-by-step instructions on specifically running autoLFADS on GCP start can be found at [First Time Set-up](create_infra)

##Google Cloud Platform (GCP) Overview

Google Cloud Platform is a suite of cloud computing services, allowing users to access data storage, software, and computational power simply through internet connection. Running autoLFADS on GCP has several advantages over running it on local infrastructure, such as access to computational resources on demand. 

In order to use GCP, you need a Google Account, internet connection, and the ability to pay to rent GPUs. Note that an internet connection is necessary for all the steps to begin an autoLFADS run, but once the run has begun it will continue whether or not the user is connected to GCP. 

##Why use GCP
An autoLFADS run requires several VMs powered by GPUs, which can be expensive. Google Cloud Platform allows us to Google's computational resources and use them over the cloud, negating the ned for any sort of local hardware.

## Pipeline
The general pipeline of running LFADS w/ PBT on GCP is described here. The high level features of the process are described below. We have tried to break down the process in the smallest constituents for the ease of understanding

### Create infrastructure

The steps here are required to be performed once, to create the required infrastructure. It can be done by any user in the project

1. Create the gcloud project with the resource quota for the required number of GPUs 
	
2. Create the server machine (it also hosts the mongo DB)

3. Create the client machines (with all installations - nvidia-driver, docker images) 

4. Create storage buckets to store the raw data and trained models

### Set up infrastructure for the user

The steps here are to be performed by each user, before they use PBT for the first time. It is to be done only once, for each user

5. Add the user to the docker group on all client machines

### Executing PBT -

These steps here are to be done before we run PBT

6. Upload data to the shared storage and mount it on all client machines

7. Start Docker on the client machines

8. Run PBT

In the following sections more details are provided on how to perform each of the above steps

Further information on the architecture is elaborated in the [Architecture](architecture) section. 

Once LFADS w/ PBT is finished training, the estimated rates that come from LFADS can be downloaded back onto the local computer, and then processed and analyzed.
