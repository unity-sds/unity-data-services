data "aws_iam_role" "lambda_processing" {
  name = split("/", var.lambda_processing_role_arn)[1]
}

resource "aws_iam_policy" "uds_lambda_processing_policy" {
  name        = "${var.prefix}-uds_lambda_processing_policy"
  description = "IAM policy for Lambda to access S3 bucket and publish to SNS topic in another account"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sts:AssumeRole",
        ],
        "Resource": "arn:aws:iam::*:role/*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "uds_lambda_processing_policy_attachment" {
  role       = data.aws_iam_role.lambda_processing.name
  policy_arn = aws_iam_policy.uds_lambda_processing_policy.arn
}
