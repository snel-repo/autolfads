#Overview
The following quick start guide offers a general pipeline for the steps of running AutoLFADS over Google Cloud Platform, and each step can be expanded to offer abbreviated instructions including code and links to detailed sections. Brand new users are recommended to use the more detailed versions of instructions, beginning with [First Time Set-up](../create_infra).


<div class="flowchart">
  <div class="container">
    <div class="card">
      <div class="newUser">
        <span>(First run begin here)</span>
      </div>
      <div class="stepContainer">
        <span>STEP 1 - Set Up Project</span>
        <img src="https://raw.githubusercontent.com/dbasrai/dbasrai.github.io/master/darrow-1.png" width=10px; height=10px;></img>
        <span>10 Minutes</span>
      </div>
      <div class="stepText">
        <p><a href="https://cpandar.github.io/lfads-pbt/create_infra/"><strong>1.1: </strong></a>Create project, set up billing<p>
        <p><a href="https://cpandar.github.io/lfads-pbt/create_infra/#requesting-additional-gpu-quota"><strong>1.2: </strong></a>Request additional quota (if needed)<p>
      </div>
      <div class="wait">
        <span>Up to 48 Hour Wait</span>
      </div>
    </div>

    <div class="card">
      <div class="stepContainer">
        <span>STEP 2 - Set-up Infrastructure</span>
        <img src="https://raw.githubusercontent.com/dbasrai/dbasrai.github.io/master/darrow-1.png" width=10px; height=10px;></img>
        <span>45 Minutes</span>
      </div>
      <div class="stepText">
        <p><a href="https://cpandar.github.io/lfads-pbt/create_infra/#creating-server-vm"><strong>2.1: </strong></a>Clone SNEL repository into cloud shell</p>
       <div class="newUser"><span>(Code in red border should be executed in cloud shell)</span></div>
       <pre class="preRed"><code>git clone https://github.com/snel-repo/autoLFADS-beta.git
</code></pre>
       <p><a href="https://cpandar.github.io/lfads-pbt/create_infra/#creating-server-vm"><strong>2.2: </strong></a>Create server machine</p>
        <pre class="preRed"><code> sh server_set_up.sh tutserver us-central1-c
</code></pre>
        <div class = "wait"><span>Up to 10 Minute Wait</span></div>
        <p><a href="https://cpandar.github.io/lfads-pbt/create_infra/#create-the-client-machines"><strong>2.3: </strong></a>Create client machines</p>
        <pre class="preRed"><code> sh machine_setup.sh tutcliente 4 us-east1-c
</code></pre>
        <pre class="preRed"><code> sh machine_setup.sh tutclientc 4 us-central1-c 
</code></pre>
        <div class = "wait"><span>Up to 20 Minute Wait</span></div>
        <p><a href="https://cpandar.github.io/lfads-pbt/create_infra/#check-if-docker-is-sucessfully-installed"><strong>2.4: </strong></a>Check if Docker is finished installing sucessfully</p>
        <pre class="preRed"><code> sh check.sh pbtclient 
</code></pre>
        <p><a href="https://cpandar.github.io/lfads-pbt/create_bucket"><strong>2.5: </strong></a>Create bucket with folders <code>data</code> and <code>run</code> </p>
      </div>
    </div>

    <div class="card">
      <div class="newUser">
        <span>(New users to already existing project begin here)</span>
      </div>
      <div class="stepContainer">
        <span>STEP 3 - Add User</span>
        <img src="https://raw.githubusercontent.com/dbasrai/dbasrai.github.io/master/darrow-1.png" width=10px; height=10px;></img>
        <span>5 Minutes</span>
      </div>
      <div class="stepText">
        <div class="newUser"><span>(This step can only be done after Docker is finished installing)</span></div>
        <p><a href="https://cpandar.github.io/lfads-pbt/add_user"><strong>3.1: </strong></a>Add user to Docker group</p>
        <pre class="preRed"><code> sh add_docker_user.sh pbtclient
</code></pre>
        <p><a href="https://cpandar.github.io/lfads-pbt/add_user/#pull-autolfads-code-onto-server-vm"><strong>3.2: </strong></a>Clone SNEL repository on server</p>
        <div class="newUser"><span>(Code with blue border should be executed in server shell)</span></div>
        <pre class="preBlue"><code> git clone https://github.com/snel-repo/autoLFADS-beta.git
</code></pre>
      </div>
    </div>

    <div class="card">
      <div class="newUser">
        <span>(Additional run, new dataset begin here)</span>
      </div>
      <div class="stepContainer">
        <span>STEP 4 - Upload Data</span>
        <img src="https://raw.githubusercontent.com/dbasrai/dbasrai.github.io/master/darrow-1.png" width=10px; height=10px;></img>
        <span>5 Minutes</span>
      </div>
      <div class="stepText">
        <p><a href="https://cpandar.github.io/lfads-pbt/data"><strong>4.1: </strong></a>Upload data with prefix <code>lfads</code></p>
      </div>
    </div>

    <div class="card">
      <div class="newUser">
        <span>(Additional run, same dataset begin here)</span>
      </div>
      <div class="stepContainer">
        <span>STEP 5 - Start Run</span>
        <img src="https://raw.githubusercontent.com/dbasrai/dbasrai.github.io/master/darrow-1.png" width=10px; height=10px;></img>
        <span>10 Minutes</span>
      </div>
      <div class="stepText">
        <p><a href="https://cpandar.github.io/lfads-pbt/run_params"><strong>5.1: </strong></a>Link <code>pbt_script_multiVM.py</code> to your data and <br> edit parameters</p>
        <p><a href="https://cpandar.github.io/lfads-pbt/run_autoLFADS"><strong>5.2: </strong></a>Begin AutoLFADS run in tmux</p>
        <pre class="preBlue"><code> tmux
</code></pre>
        <pre class="preBlue"><code> python2 pbt_script_multiVM.py
</code></pre>
      </div>
      <div class="wait">
        <span>Up to 2 Hour Wait</span>
      </div>
    </div>

    <div class="card">
      <div class="stepContainer">
        <span>STEP 6 - Analyze Output</span>
        <img src="https://raw.githubusercontent.com/dbasrai/dbasrai.github.io/master/darrow-1.png" width=10px; height=10px;></img>
        <span>30 Minutes</span>
      </div>
      <div class="stepText">
        <div class="newUser"><span>(You should <a href="../setupAddInfo">stop all machines </a>now)</span></div>
        <p><a href="https://cpandar.github.io/lfads-pbt/analysis/#downloading-data-from-gcp"><strong>6.1: </strong></a>Download output zip file from bucket</p>
        <p><a href="https://cpandar.github.io/lfads-pbt/analysis/#post-processing"><strong>6.2: </strong></a>Run <code>pbt_plot.m</code></p>
      </div>
    </div>

  </div>
</div>
