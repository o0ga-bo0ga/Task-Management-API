variable "project_name" {}
variable "environment" {}
variable "vpc_cidr" {}
variable "availibility_zones" { type = list(string) }
variable "public_subnet_cidrs" { type = list(string) }
variable "private_subnet_cidrs" { type = list(string) }