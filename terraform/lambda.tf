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

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_ssm_read_policy" {
  name = "lambda-ssm-read-policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["ssm:GetParameter"]
        Resource = "arn:aws:ssm:us-west-2:*:parameter/boulderbattle/db_pooler_url"
      },
      {
        Effect = "Allow"
        Action = ["kms:Decrypt"]
        Resource = "*"
      }
    ]
  })
}

# package the lambda function code
data "archive_file" "archive_ldrbrd_reset_code" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_code"
  output_path = "${path.module}/../function.zip"
  excludes    = [
    ".env",
    ".env.example",
    ".gitignore"
  ]
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

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_ssm_read_policy,
  ]
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

resource "aws_lambda_permission" "allow_eventbridge_invoke" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.leaderboard_reset_function.function_name
  principal     = "events.amazonaws.com"
}