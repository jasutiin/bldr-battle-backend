output "api_public_ip" {
  description = "Public Elastic IP address of the API EC2 instance"
  value       = aws_eip.web_server_eip.public_ip
}

output "api_base_url" {
  description = "Base URL for querying the API"
  value       = "http://${aws_eip.web_server_eip.public_ip}"
}

output "api_docs_url" {
  description = "Swagger docs URL for quick verification"
  value       = "http://${aws_eip.web_server_eip.public_ip}/docs"
}
