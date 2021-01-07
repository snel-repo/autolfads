##Modifying HPs
While PBT is designed to automatically search for optimal hyperparameters during an AutoLFADS run, there are still adjustments we can make to the HPs prior to the run that can allow for better performance, such as a more optimal initialization value, or adjusting the ranges at which the HPs can vary. Go to the [glossary](../parameters) for in-depth information on all parameters.

##Updating Docker image
If you are re-using client machines created some time ago, there is a chance that the Docker image needs to be updated. The following steps explain how to update the Docker image on all machines. 

1) First, make sure all client machines are started (have a green check next to them). 

2) Open up Cloud Shell and then navigate to `autoLFADS-beta/gclouds_scripts` directory and run the following command.

    sh update_docker_image.sh

3) Next, wait for ~10 minutes for all Docker images to be successfully installed. This can be confirmed with the script `sh check.sh pbtclient`.  

##Creating additional machines
If you would like to add additional machines, you can use the same command when setting up the [initial infrastructure](../create_infra/#create-the-client-machines). Simply navigate back to [compute engine](https://console.cloud.google.com/compute), open up 'Cloud Shell' in top right corner, and pass in parameters into the following command: `sh machine_setup.sh <client_name> <number_of_clients> <zone>`. 

If creating additional client machines, we also need to re-add the user to Docker. 

To do so, first wait until Docker has finished successfully installing on the additional client machines (with `check.sh`), and then run the following command in cloud shell.

    sh add_docker_user.sh pbtclient


