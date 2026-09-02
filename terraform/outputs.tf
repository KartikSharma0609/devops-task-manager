output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.task_manager.id
}

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.task_manager.public_ip
}

output "ec2_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.task_manager.private_ip
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.task_manager.repository_url
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.task_manager.id
}

output "iam_role_name" {
  description = "EC2 IAM role name"
  value       = aws_iam_role.ec2_ssm.name
}
