resource "aws_ecr_repository" "task_manager" {
  name = var.ecr_repository_name
}
