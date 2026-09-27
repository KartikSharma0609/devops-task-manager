resource "aws_sns_topic" "alerts" {
  name = "devops-task-manager-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "high_disk" {
  alarm_name          = "task-manager-high-disk-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "disk_used_percent"
  namespace           = "DevOpsTaskManager"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Triggers when disk usage exceeds 85%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.task_manager.id
    path       = "/"
    device     = "nvme0n1p1"
    fstype     = "xfs"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "task-manager-high-memory-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "mem_used_percent"
  namespace           = "DevOpsTaskManager"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Triggers when memory usage exceeds 85%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.task_manager.id
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "task-manager-high-cpu-usage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "cpu_usage_idle"
  namespace           = "DevOpsTaskManager"
  period              = 300
  statistic           = "Average"
  threshold           = 10
  alarm_description   = "Triggers when CPU idle drops below 10% (i.e. CPU usage above 90%)"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.task_manager.id
  }
}

resource "aws_cloudwatch_metric_alarm" "instance_status_check" {
  alarm_name          = "task-manager-instance-status-check-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed_Instance"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "Triggers if the instance fails its status check"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.task_manager.id
  }
}
