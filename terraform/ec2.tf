data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"]
}

# this is the ec2 instance that holds the backend server
resource "aws_instance" "bldr_battle_api_server_ec2" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id = aws_subnet.public_subnet.id

  tags = {
    Name = "bldr-battle-api-server"
  }
}

# assign an elastic ip address to the web server so that the api doesn't break if the ec2 shuts down.
resource "aws_eip" "web_server_eip" {
  instance = aws_instance.bldr_battle_api_server_ec2.id
}

# this is the ec2 instance that holds the redis cache
resource "aws_instance" "bldr_battle_redis_server_ec2" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id = aws_subnet.private_subnet.id

  tags = {
    Name = "bldr-battle-redis-server"
  }
}