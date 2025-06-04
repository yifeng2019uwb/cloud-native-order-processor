resource "aws_ecr_repository" "api_repository" {
  name                 = "cloud-native-order-processor-api"
  image_tag_mutability = "MUTABLE" # Or "IMMUTABLE" for stricter tag management

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project     = "CloudNativeOrderProcessor"
    Service     = "API"
  }
}

# Optional: Output the ECR repository URL, useful for your CI/CD pipeline
output "ecr_repository_url" {
  description = "The URL of the ECR repository for the API."
  value       = aws_ecr_repository.api_repository.repository_url
}