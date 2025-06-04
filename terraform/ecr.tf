# ECR Repository for the Backend API
resource "aws_ecr_repository" "api_repository" {
  name                 = "cloud-native-order-processor-api"
  image_tag_mutability = "MUTABLE" 

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project     = "CloudNativeOrderProcessor"
    Service     = "API"
  }
}

# ECR Repository for the Frontend
resource "aws_ecr_repository" "frontend_repository" {
  name                 = "cloud-native-order-processor-frontend" 
  image_tag_mutability = "MUTABLE" 

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project     = "CloudNativeOrderProcessor"
    Service     = "Frontend"
  }
}

# Optional: Output the ECR repository URLs, useful for your CI/CD pipeline or other Terraform modules
output "api_ecr_repository_url" {
  description = "The URL of the ECR repository for the API."
  value       = aws_ecr_repository.api_repository.repository_url
}

output "frontend_ecr_repository_url" {
  description = "The URL of the ECR repository for the Frontend."
  value       = aws_ecr_repository.frontend_repository.repository_url
}