resource "aws_ssm_parameter" "cloudwatch_agent_config" {
  name        = "/devops-task-manager/cloudwatch-agent-config"
  description = "CloudWatch Agent configuration for task manager EC2 instance"
  type        = "String"

  value = jsonencode({
    agent = {
      metrics_collection_interval = 60
      run_as_user                 = "root"
    }
    metrics = {
      namespace = "DevOpsTaskManager"
      append_dimensions = {
        InstanceId = "$${aws:InstanceId}"
      }
      metrics_collected = {
        mem = {
          measurement                 = ["mem_used_percent"]
          metrics_collection_interval = 60
        }
        disk = {
          measurement                 = ["used_percent"]
          resources                   = ["/"]
          metrics_collection_interval = 60
        }
        cpu = {
          measurement                 = ["cpu_usage_idle"]
          totalcpu                    = true
          metrics_collection_interval = 60
        }
      }
    }
    logs = {
      logs_collected = {
        files = {
          collect_list = [
            {
              file_path         = "/var/lib/docker/containers/*/*-json.log"
              log_group_name    = "/devops-task-manager/docker"
              log_stream_name   = "{instance_id}"
              retention_in_days = 7
            }
          ]
        }
      }
    }
  })
}

# ... aws_ssm_association and aws_cloudwatch_dashboard blocks stay exactly as before ...

resource "aws_ssm_association" "cloudwatch_agent" {
  name = "AmazonCloudWatch-ManageAgent"

  parameters = {
    action                        = "configure"
    mode                          = "ec2"
    optionalConfigurationSource   = "ssm"
    optionalConfigurationLocation = aws_ssm_parameter.cloudwatch_agent_config.name
    optionalRestart               = "yes"
  }

  targets {
    key    = "InstanceIds"
    values = [aws_instance.task_manager.id]
  }
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "devops-task-manager"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "CPU Utilization (EC2 native)"
          region = var.aws_region
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.task_manager.id]
          ]
          period = 300
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Memory Used %"
          region = var.aws_region
          metrics = [
            ["DevOpsTaskManager", "mem_used_percent", "InstanceId", aws_instance.task_manager.id]
          ]
          period = 300
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Disk Used %"
          region = var.aws_region
          metrics = [
            ["DevOpsTaskManager", "disk_used_percent", "InstanceId", aws_instance.task_manager.id, "path", "/", "device", "nvme0n1p1", "fstype", "xfs"]
          ]
          period = 300
          stat   = "Average"
        }
      },
      {
        type   = "log"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Recent Application Logs"
          region = var.aws_region
          query  = "SOURCE '/devops-task-manager/docker' | fields @timestamp, @message | sort @timestamp desc | limit 20"
        }
      }
    ]
  })
}
