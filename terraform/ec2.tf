data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"]
}

# this is the ec2 instance that holds the backend server
resource "aws_instance" "bldr-battle-api-server" {
  ami           = data.aws_ami.ubuntu
  instance_type = "t3.micro"
  subnet_id = aws_subnet.public_subnet

  tags = {
    Name = "bldr-battle-api-server"
  }
}

# this is the ec2 instance that holds the redis cache
resource "aws_instance" "user-profile-redis-server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id = aws_subnet.private_subnet

  tags = {
    Name = "bldr-battle-redis-server"
  }
}