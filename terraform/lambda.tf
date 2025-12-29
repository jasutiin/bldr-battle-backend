data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# package the lambda function code
data "archive_file" "archive_ldrbrd_reset_code" {
  type        = "zip"
  source_file = "${path.module}/../lambda_code/main.py"
  output_path = "${path.module}/../lambda_code/function.zip"
}

resource "aws_lambda_function" "leaderboard_reset_function" {
  filename      = data.archive_file.archive_ldrbrd_reset_code.output_path
  function_name = "bldr_battle_leaderboard_reset_function"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "main.lambda_handler"

  runtime = "python3.13"

  environment {
    variables = {
      ENVIRONMENT = "production"
      LOG_LEVEL   = "info"
    }
  }

  tags = {
    Environment = "production"
    Application = "example"
  }
}

module "eventbridge" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false # using the default bus and not creating a new one is sufficient

  rules = {
    bldr_battle_leaderboard_reset = {
      description         = "Trigger for a leaderboard reset lambda"
      schedule_expression = "rate(1 minute)" # run every minute for testing
      # schedule_expression = "cron(0 12 * * ? *)" # run everyday at 12pm
    }
  }

  targets = {
    bldr_battle_leaderboard_reset = [
      {
        name  = "bldr-battle-leaderboard-reset-cron"
        arn   = aws_lambda_function.leaderboard_reset_function.arn
        input = jsonencode({"key1": "justine"})
      }
    ]
  }
}