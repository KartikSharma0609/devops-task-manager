variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
  default     = "ami-0ac7b260cf76d8865"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "subnet_id" {
  description = "Subnet ID for the EC2 instance"
  type        = string
  default     = "subnet-01112699a2813b67c"
}

variable "vpc_id" {
  description = "VPC ID for the security group"
  type        = string
  default     = "vpc-02c013b95e8523152"
}

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
  default     = "devops-task-manager-key"
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to access SSH"
  type        = string
  default     = "103.251.209.64/32"
}

variable "ecr_repository_name" {
  description = "ECR repository name"
  type        = string
  default     = "devops-task-manager"
}

variable "iam_role_name" {
  description = "IAM role name for EC2"
  type        = string
  default     = "EC2-DevOpsTaskManager-SSM"
}
