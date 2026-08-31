resource "aws_instance" "task_manager" {
  ami           = "ami-0ac7b260cf76d8865"
  instance_type = "t3.micro"

  subnet_id = "subnet-01112699a2813b67c"

  vpc_security_group_ids = [
    aws_security_group.task_manager.id
  ]

  key_name = "devops-task-manager-key"

  iam_instance_profile = "EC2-DevOpsTaskManager-SSM"

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
