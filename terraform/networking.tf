# in this file we are defining the VPC and subnets for our application.
# we could use the vpc module to abstract a lot of this logic,
# but i will not be using that for learning purposes.

locals {
  vpc_cidr     = "10.0.0.0/16"
  public_cidr  = "10.0.101.0/24"
  private_cidr = "10.0.1.0/24"
  az           = "us-west-2a"
}

# create a vpc to group resources together.
resource "aws_vpc" "vpc" {
  cidr_block = local.vpc_cidr

  tags = {
    Name = "bldr-battle-vpc"
  }
}

# create internet gateway and attach it to vpc so clients can access resources inside the vpc.
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "bldr-battle-igw"
  }
}

# create a public subnet for the web server.
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = local.public_cidr
  availability_zone       = local.az
  map_public_ip_on_launch = true

  tags = {
    Name = "bldr-battle-public-subnet"
  }
}

# create a public route table for the web server's ec2 instance.
# this is essentially telling it to go to the internet gateway
# to communicate with the public.
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "bldr-battle-public-route-table"
  }
}

# associate the public route table with public subnet.
resource "aws_route_table_association" "public_rt_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}

# create a private subnet for the redis server.
# we are not creating a private route table because the vpc has a route table
# that associates all subnets with it. this route table is only for things
# inside the vpc, making it private and unaccessible to the public internet.
resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = local.private_cidr
  availability_zone       = local.az
  map_public_ip_on_launch = false

  tags = {
    Name = "bldr-battle-private-route-subnet"
  }
}

resource "aws_security_group" "bldr_battle_api_sg" {
  name        = "bldr-battle-api-sg"
  description = "Allows HTTP/80 inbound and PostgreSQL/5432 outbound"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "bldr-battle-api-sg"
  }
}