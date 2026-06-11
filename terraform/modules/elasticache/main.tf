resource "aws_elasticache_subnet_group" "main" {
  name = "cache-subnet-group"
  description = "Subnet group for Redis"
  subnet_ids = var.private_subnet_ids
}

resource "aws_security_group" "cache_sg"{
    name = "cache-security-group"
    vpc_id = var.vpc_id
    ingress{
        from_port = 6379
        to_port = 6379
        protocol = "tcp"
        cidr_blocks = [var.vpc_cidr]
    }
    egress{
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
        Name = "Cache SG"
    }
}

resource "aws_elasticache_cluster" "elasticache_cluster" {
    cluster_id = "${var.project_name}-${var.environment}-redis"
    engine = "redis"
    node_type = "cache.t3.micro"
    num_cache_nodes = 1
    port = 6379
    subnet_group_name = aws_elasticache_subnet_group.main.name
    security_group_ids = [aws_security_group.cache_sg.id]
}