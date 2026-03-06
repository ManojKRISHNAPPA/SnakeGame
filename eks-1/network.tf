############################
# VPC
############################
resource "aws_vpc" "itkannadigaru_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "itkannadigaru_vpc"
  }
}

############################
# Subnets (2 public subnets)
############################
resource "aws_subnet" "itkannadigaru_subnet" {
  count = 2

  vpc_id     = aws_vpc.itkannadigaru_vpc.id
  cidr_block = cidrsubnet(aws_vpc.itkannadigaru_vpc.cidr_block, 8, count.index)

  availability_zone       = element(["us-west-2a", "us-west-2b"], count.index)
  map_public_ip_on_launch = true

  tags = {
    Name = "itkannadigaru_subnet-${count.index}"
  }
}

############################
# Internet Gateway
############################
resource "aws_internet_gateway" "itkannadigaru_igw" {
  vpc_id = aws_vpc.itkannadigaru_vpc.id

  tags = {
    Name = "itkannadigaru_igw"
  }
}

############################
# Route Table
############################
resource "aws_route_table" "itkannadigaru_rt" {
  vpc_id = aws_vpc.itkannadigaru_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.itkannadigaru_igw.id
  }

  tags = {
    Name = "itkannadigaru_route_table"
  }
}

############################
# Route Table Association
############################
resource "aws_route_table_association" "itkannadigaru_rt_assoc" {
  count = 2

  subnet_id      = aws_subnet.itkannadigaru_subnet[count.index].id
  route_table_id = aws_route_table.itkannadigaru_rt.id
}

############################
# Security Groups
############################

# EKS Cluster Security Group
resource "aws_security_group" "itkannadigaru_cluster_sg" {
  vpc_id = aws_vpc.itkannadigaru_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "itkannadigaru-cluster-sg"
  }
}

# Worker Node Security Group
resource "aws_security_group" "itkannadigaru_node_sg" {
  vpc_id = aws_vpc.itkannadigaru_vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "itkannadigaru-node-sg"
  }
}