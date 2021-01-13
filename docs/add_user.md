In this step, we add users to a Docker group in order to avoid prefacing docker commands with `sudo`. This step needs to be performed once per individual Google Account using AutoLFADS, before they start a run.

##Adding user to docker group <a href="https://snel-repo.github.io/autolfads/add_user/#adding-user-to-docker-group-walkthrough"><img src="../img/vidicon.png" alt="IMAGE ALT TEXT HERE" width="20" height="auto" border="10" /></a>

First, navigate back to the [compute engine](https://console.cloud.google.com/compute) and make sure the 'cloud shell' is open (button in the top right corner).

Again, this step only needs to be done ONCE per Google account. Thus, if prior to this your Google account has already been adding to the docker group, this step does not need to be repeated.

Furthermore, this step can only be done once the client machines are completely finished installing (remember to run check.sh to confirm this.) 

Once the cloud shell is open, run the following command `sh add_docker_user.sh pbtclient`.

For this tutorial, the command would be

    sh add_docker_user.sh pbtclient

!!! warning
    Leaving VMs running when not in use can lead to unintended high bills. Go to [additional information](../setupAddInfo) section to see how to shut off unused VMs. 

###Adding user to docker group walkthrough
<video width="100%" height="auto" controls loop>
  <source src="../media/autoLFADS/add_docker_user.mp4" type="video/mp4">
</video>

##Pull AutoLFADS code onto server VM<a href="https://snel-repo.github.io/autolfads/create_infra/#server-pull-code-walkthrough"><img src="../img/vidicon.png" alt="IMAGE ALT TEXT HERE" width="20" height="auto" border="10" /></a>

Next, we want to directly enter the server VM and copy the AutoLFADS code. In order to enter the server VM, we need to SSH in. First, make sure you're at the compute engine ([console.cloud.google.com/compute](https://console.cloud.google.com/compute)) and can see your list of created VMs. Once you find your server you created (in this tutorial, its named tutserver), click on the button to the right of it labeled 'SSH'.

<video width="100%" height="auto" controls muted autoplay loop>
  <source src="../media/autoLFADS/how_to_ssh.mp4" type="video/mp4">
</video>

You have now SSHed into your server client. Now, inside this newly opened SSH browser window (NOT the cloud shell), we want to clone the repository here in order to obtain the AutoLFADS python script.

Run the following command in the SSH window.

    git clone -b GCP https://github.com/snel-repo/autolfads.git

Now, the server VM should contain the necessary code. 

This completes creating all the necessary cloud infrastructure. 

###Server Pull Code Walkthrough

<video width="100%" height="auto" controls muted autoplay loop>
  <source src="../media/autoLFADS/server_pull_code.mp4" type="video/mp4">
</video>
