import os
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    eks_cluster_name = "demo-eks-cluster"
    eks_scaling_configs = {
        "airbyte": [2, 2, 3],
        "general": [4, 4, 5],
        "logging": [0, 0, 1],
        "ml": [1, 1, 2],
    }
    
    rds_instances = ["<postgres-instance-name>"]
    bastion_host_id = "<bastion-id>"

    eks_client = boto3.client('eks', region_name='us-east-2')
    rds_client = boto3.client('rds', region_name='us-east-2')
    bastion_client = boto3.client('ec2', region_name='us-east-2')

    action = event["type"]

    if action == "start":
        print ("Going to Scale up EKS : ", eks_cluster_name ) 
        try:
            for node_group in eks_scaling_configs:
                eks_client.update_nodegroup_config(
                    clusterName = eks_cluster_name,
                    nodegroupName = node_group,
                    scalingConfig = {
                        'minSize': eks_scaling_configs[node_group][0],
                        'desiredSize': eks_scaling_configs[node_group][1],
                        'maxSize': eks_scaling_configs[node_group][2]
                    }
                )
        except ClientError as e:
            print (e)

        # Going to start RDS Instances
        try:
            for rds_instance in rds_instances:
                print ("Going to Start RDS : ", rds_instance)
                rds_client.start_db_instance(DBInstanceIdentifier=rds_instance)     
        except ClientError as e:
            print (e)
  
        print ("Going to Start Bastion host : ", bastion_host_id) 
        try:
            bastion_client.start_instances(InstanceIds=[bastion_host_id], 
            AdditionalInfo='string', DryRun=False)
        except ClientError as e:
            print (e)  

    elif action == "stop":
        print ("Going to Scale down EKS : ", eks_cluster_name ) 
        try:
            for node_group in eks_scaling_configs:
                eks_client.update_nodegroup_config(
                    clusterName = eks_cluster_name,
                    nodegroupName = node_group,
                    scalingConfig = {
                        'minSize': 0,
                        'desiredSize': 0,
                        'maxSize': 1
                    }
                )
        except ClientError as e:
            print (e)

        # Going to stop RDS Instances
        try:
            for rds_instance in rds_instances:
                print ("Going to Stop RDS : ", rds_instance)
                rds_client.stop_db_instance(DBInstanceIdentifier=rds_instance)  
        except ClientError as e:
            print (e)        
        

        print ("Going to Stop Bastion host : ", bastion_host_id)  
        try:
            bastion_client.stop_instances(InstanceIds=[bastion_host_id],
            Hibernate=False,
            DryRun=False,
            Force=False
        )
        except ClientError as e:
            print (e)
