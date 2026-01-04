variable "db_connection_string" {
  type        = string
  description = "The database connection string passed via the -var flag."
  sensitive   = true
}