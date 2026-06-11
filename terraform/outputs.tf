output "db_endpoint" {
  value = module.rds.db_endpoint
}

output "db_port" {
  value = module.rds.db_port
}

output "redis_endpoint" {
  value = module.elasticache.redis_endpoint
}

output "redis_port" {
  value = module.elasticache.redis_port
}