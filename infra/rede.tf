# A função só fala com o NLB interno da plataforma, que atende o OS Service na porta 80.
resource "aws_security_group" "funcao" {
  name        = "${local.nome_funcao}-funcao"
  description = "Lambda de autenticacao: saida so para o NLB interno"
  vpc_id      = data.aws_ssm_parameter.vpc_id.value

  tags = { Name = "${local.nome_funcao}-funcao" }
}

resource "aws_vpc_security_group_egress_rule" "nlb" {
  security_group_id = aws_security_group.funcao.id
  description       = "HTTP para o NLB interno"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = data.aws_ssm_parameter.vpc_cidr.value
}
