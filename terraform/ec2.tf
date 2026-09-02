resource "aws_instance" "task_manager" {
  ami           = var.ami_id
  instance_type = var.instance_type

  subnet_id = var.subnet_id

  vpc_security_group_ids = [
    aws_security_group.task_manager.id
  ]

  key_name = var.key_name

  iam_instance_profile = aws_iam_instance_profile.ec2_ssm.name

  ebs_optimized = true

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  root_block_device {
    delete_on_termination = true
  }

  tags = {
    Name = "devops-task-manager"
  }
}
