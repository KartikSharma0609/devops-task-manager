terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
      bucket = "kartik-devops-task-manager-terraform-state-689505268101"
      key    = "devops-task-manager/terraform.tfstate"
      region = "ap-south-1"
      use_lockfile = true
    }
  }

provider "aws" {
  region = var.aws_region
}
