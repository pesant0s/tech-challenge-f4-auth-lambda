# Parâmetros publicados pela plataforma (contrato de infraestrutura da Fase 04).

locals {
  prefixo_ssm = "/${var.prefixo}"
}

data "aws_ssm_parameter" "vpc_id" { name = "${local.prefixo_ssm}/rede/vpc_id" }
data "aws_ssm_parameter" "vpc_cidr" { name = "${local.prefixo_ssm}/rede/cidr" }
data "aws_ssm_parameter" "subnets_privadas" { name = "${local.prefixo_ssm}/rede/subnets_privadas" }
data "aws_ssm_parameter" "nlb_dns" { name = "${local.prefixo_ssm}/nlb/dns" }
data "aws_ssm_parameter" "apigateway_id" { name = "${local.prefixo_ssm}/apigateway/id" }
data "aws_ssm_parameter" "apigateway_execucao_arn" { name = "${local.prefixo_ssm}/apigateway/execucao_arn" }
data "aws_ssm_parameter" "apigateway_endpoint" { name = "${local.prefixo_ssm}/apigateway/endpoint" }

# Lidos no apply e passados como variável de ambiente: sem NAT, a Lambda não alcança o SSM (ADR-010).
data "aws_ssm_parameter" "secret_key" {
  name            = "${local.prefixo_ssm}/segredos/jwt_secret_key"
  with_decryption = true
}

data "aws_ssm_parameter" "token_interno" {
  name            = "${local.prefixo_ssm}/segredos/token_interno"
  with_decryption = true
}

locals {
  subnets_privadas = split(",", data.aws_ssm_parameter.subnets_privadas.value)
  nome_funcao      = "${var.prefixo}-auth"
}
