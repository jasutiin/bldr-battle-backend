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

# build lambda deployment package (code + dependencies)
resource "null_resource" "lambda_package" {
  triggers = {
    main_py_hash       = filemd5("${path.module}/../lambda_code/main.py")
    requirements_hash  = filemd5("${path.module}/../lambda_code/requirements.txt")
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = <<-EOT
      $repoRoot = (Resolve-Path "${path.module}/..").Path
      $buildDir = Join-Path $repoRoot "lambda_build"
      $zipPath = Join-Path $repoRoot "function.zip"

      Remove-Item -Recurse -Force $buildDir -ErrorAction SilentlyContinue
      New-Item -ItemType Directory -Path $buildDir | Out-Null
      Remove-Item -Force $zipPath -ErrorAction SilentlyContinue

      docker run --rm --entrypoint /bin/sh -v "$${repoRoot}:/work" -w /work public.ecr.aws/lambda/python:3.13 -c "pip install -r lambda_code/requirements.txt -t lambda_build && cp lambda_code/main.py lambda_build/main.py"
      if ($LASTEXITCODE -ne 0) { throw "Docker packaging failed" }

      Compress-Archive -Path "$buildDir\*" -DestinationPath $zipPath -Force
    EOT
  }
}

resource "aws_lambda_function" "leaderboard_reset_function" {
  filename      = "${path.module}/../function.zip"
  function_name = "bldr_battle_leaderboard_reset_function"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "main.lambda_handler"

  runtime = "python3.13"
  timeout = 180
  memory_size = 512

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

  lifecycle {
    replace_triggered_by = [
      null_resource.lambda_package
    ]
  }

  depends_on = [
    null_resource.lambda_package,
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