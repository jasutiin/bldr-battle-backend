data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"]
}

resource "aws_iam_role" "ssm_role" {
  name = "EC2-SSM-SessionManager-Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_policy_attach" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.ssm_role.name
}

resource "aws_iam_instance_profile" "ssm_profile" {
  name = "EC2-SSM-SessionManager-Profile"
  role = aws_iam_role.ssm_role.name
}

# this is the ec2 instance that holds the backend server
resource "aws_instance" "bldr_battle_api_server_ec2" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id = aws_subnet.public_subnet.id
  iam_instance_profile = aws_iam_instance_profile.ssm_profile.name

user_data = <<-EOF
    #!/bin/bash
    
    sudo apt update -y
    sudo apt install -y docker.io
    sudo usermod -aG docker ubuntu
    
    CNXN_STR="${var.db_connection_string}"
    
    /usr/bin/docker run -d \
      --name bldr-battle-backend \
      -p 80:8080 \
      -e SUPABASE_CONNECTION_STRING="$CNXN_STR" \
      stenuji/bldr-battle-server:latest
  EOF

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
  iam_instance_profile = aws_iam_instance_profile.ssm_profile.name

  tags = {
    Name = "bldr-battle-redis-server"
  }
}