# AutoLFADS on Google Cloud Platform

This tutorial is a programming-beginner friendly, step-by-step walkthrough on applying AutoLFADS, a deep learning tool that can be trained to uncover dynamics from single trial neural population data, using the computational resources of Google Cloud Platform. 


## Quick introduction

AutoLFADS is the combination of Latent Factor Analysis via Dynamical Systems (LFADS), a deep learning method to infer latent dynamics from single-trial neural population data, with Population Based Training (PBT), an automatic hyperparameter tuning framework. 

Specifically, this tutorial focuses on running AutoLFADS on Google Cloud Platform (GCP), which allows the use of AutoLFADS using computational resources available for rent on the cloud. Thus, as long as the user has access to GCP and the ability to pay for the usage of GPUs, then this tutorial can be used to apply AutoLFADS to neural population data without any need for local hardware.  

## Requirements for this tutorial

This tutorial is specifically designed for researchers and scientists with neural population data who are interested in using powerful deep-learning technology to uncover dynamics underlying neural populations. Fundamentally, this tutorial is designed so that significant programming knowledge or experience with deep-learning technology are NOT required.

In order to use this tutorial, it is suggested that:

* Have neural population data in the format `neurons x trial-length x number of trials`, with sequence length <100 timesteps. 
* Have access to Matlab and basic familiarity with it
* Have a Google account and can pay for the usage of GPUs on the Google Cloud platform. For an estimated rate, a 2.5 hour AutoLFADS run with 8 GPUs (example run in tutorial) will cost ~$7. For more detailed pricing on GPUs, go to [https://cloud.google.com/compute/gpus-pricing](https://cloud.google.com/compute/gpus-pricing).

## Requesting GPU quota

Google Cloud Platform enforces a GPU quota to prevent unforseen spikes in usage. Requesting additional quota must be done 24-48 hours in advance of a run. If interested in running AutoLFADS through GCP, it is recommended to first request additional GPU quota. Instructions are detailed in the [First Time Set-up](create_infra/#requesting-additional-gpu-quota) section. 
