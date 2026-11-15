# No AWS Academy não é permitido criar roles: a função usa a LabRole que já existe.
data "aws_iam_roles" "laboratorio" {
  name_regex = "^LabRole$"
}

locals {
  laboratorio = length(data.aws_iam_roles.laboratorio.arns) > 0
  role_funcao = local.laboratorio ? one(data.aws_iam_roles.laboratorio.arns) : aws_iam_role.funcao[0].arn
}

data "aws_iam_policy_document" "confianca" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "funcao" {
  count = local.laboratorio ? 0 : 1

  name               = "${local.nome_funcao}-execucao"
  assume_role_policy = data.aws_iam_policy_document.confianca.json
}

resource "aws_iam_role_policy_attachment" "vpc" {
  count = local.laboratorio ? 0 : 1

  role       = aws_iam_role.funcao[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
