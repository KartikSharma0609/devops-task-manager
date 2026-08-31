resource "aws_security_group" "task_manager" {
  name        = "devops-task-manager-sg"
  description = "Security group for DevOps Task Manager"
  vpc_id      = "vpc-02c013b95e8523152"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["103.251.209.64/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
