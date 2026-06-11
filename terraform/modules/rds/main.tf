resource "aws_db_subnet_group" "default"{
    name = "main_db_subnet_group"
    subnet_ids = var.private_subnet_ids
    tags = {
        Name = "${var.project_name}-${var.environment}-db_subnet_group"
    }
}

resource "aws_security_group" "postgres_sg"{
    name = "postgres-security-group"
    vpc_id = var.vpc_id
    ingress{
        from_port = 5432
        to_port = 5432
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
        Name = "PostgreSQL SG"
    }
}

resource "aws_db_instance" "postgres_dev"{
    identifier = "postgres-dev-instance"
    engine = "postgres"
    engine_version = "15"
    instance_class = "db.t3.micro"
    allocated_storage = 20
    storage_type = "gp2"
    db_name = var.db_name
    username = var.db_username
    password = var.db_password

    db_subnet_group_name = aws_db_subnet_group.default.name
    vpc_security_group_ids = [aws_security_group.postgres_sg.id]

    publicly_accessible = false
    skip_final_snapshot = true
    deletion_protection = false

    tags = {
        Name = "PostgreSQL Dev DB"
    }
}