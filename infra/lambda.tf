resource "aws_cloudwatch_log_group" "funcao" {
  name              = "/aws/lambda/${local.nome_funcao}"
  retention_in_days = 7
}

resource "aws_lambda_function" "auth" {
  function_name    = local.nome_funcao
  description      = "Autentica o cliente por CPF/CNPJ e emite o JWT"
  role             = local.role_funcao
  runtime          = "python3.12"
  handler          = "handler.handler"
  filename         = var.caminho_pacote
  source_code_hash = filebase64sha256(var.caminho_pacote)
  memory_size      = var.memoria_mb
  timeout          = var.timeout_segundos

  # Subnet privada para alcançar o NLB interno e, por ele, o OS Service.
  vpc_config {
    subnet_ids         = local.subnets_privadas
    security_group_ids = [aws_security_group.funcao.id]
  }

  environment {
    variables = {
      OS_SERVICE_URL              = "http://${data.aws_ssm_parameter.nlb_dns.value}:80"
      TOKEN_INTERNO               = data.aws_ssm_parameter.token_interno.value
      SECRET_KEY                  = data.aws_ssm_parameter.secret_key.value
      ALGORITHM                   = "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES = "60"
      LOG_LEVEL                   = "INFO"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.vpc, aws_cloudwatch_log_group.funcao, aws_vpc_security_group_egress_rule.nlb]

  tags = { Name = local.nome_funcao }
}
