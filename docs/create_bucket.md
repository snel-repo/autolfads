#Creating Bucket
The next step is creating a bucket and adding two directories, one to upload your data to, and one to store checkpoints from your run.

Navigate to [console.cloud.google.com/storage](https://console.cloud.google.com/storage) and click 'Create Bucket.' The location type of the bucket should be "multi-region," the storage class should be "standard," and the access control should be "fine-grained."

After you have created your bucket, navigate inside your bucket by clicking on it. Inside your bucket, click "create folder" and name it "data." Then create another folder called "runs."

<video width="100%" height="auto" controls loop>
  <source src="../media/autoLFADS/create_bucket.mp4" type="video/mp4">
</video>

