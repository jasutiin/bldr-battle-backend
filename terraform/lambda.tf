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