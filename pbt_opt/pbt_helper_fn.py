import os
import subprocess

class pbtHelper(object):
	def __init__(self, bucket_name, data_path, run_path, name, nprocess_gpu):
		self.bucket_name = bucket_name
		self.data_path = data_path
		self.run_path = run_path
		self.machine_name = 'pbtclient'
		self.container_name = 'docker_pbt'
		self.run_dir="pbt_run"
		self.name = name
                self.nprocess_gpu = nprocess_gpu
		self.run_save_path = self.get_run_save_path(self.bucket_name, self.run_path)
		self.data_dir = self.get_data_dir(self.data_path)

		# Get server hostname
		subprocess.call(['export HOSTNAME'], shell=True)
		self.server_id = os.environ["HOSTNAME"]

		# Zone of the server VM
		self.my_zone = subprocess.check_output(['gcloud','compute','instances','list', '--filter', 'name=("%s")' % self.server_id,
											 '--format', 'csv[no-heading](zone)'])[:-1]
	
		# Get a list of names of vms
		command="gcloud compute instances list --filter='tags:{} AND STATUS:RUNNING' --format='csv[no-heading](name)'".format(self.machine_name)
		vms = subprocess.check_output(command, shell=True)
		self.vms_list = vms.split(b'\n')[:-1]

		# Get a list of the zones of the vms in vms_list
		command_zone="gcloud compute instances list --filter='tags:{} AND STATUS:RUNNING' --format='csv[no-heading](zone)'".format(self.machine_name)
		vms_zone = subprocess.check_output(command_zone, shell=True)
		self.zone_list = vms_zone.split(b'\n')[:-1]
		self.vmzn = tuple(zip(self.vms_list, self.zone_list))
		self.computers = self.get_computers(self.vmzn)

		command_ip = "gcloud --format=\"value(INTERNAL_IP)\" compute instances list --filter=\'name:%s\'" % self.server_id
		server_ip = subprocess.check_output(command_ip, shell=True)
		self.server_ip = server_ip.split(b'\n')[0]


	def get_run_save_path(self, bucket_name, run_path):
		return 'gs://{}/{}/'.format(bucket_name, run_path)

	def get_data_dir(self, data_path):
		return '/bucket/{}/'.format(data_path)

	def get_computers(self, vmzn):
		computers=[]
		keys = ['id', 'ip', 'max_processes', 'process_start_cmd', 'wait_for_process_start', 'zone']
		for vm, zn in vmzn:
		    values = [vm, vm, str(self.nprocess_gpu), '/snel/PBT_HP_opt/pbt_opt/run_lfads_client.sh', 'True', zn]
		    dictionary = dict(zip(keys, values))
		    computers.append(dictionary)
		return computers
