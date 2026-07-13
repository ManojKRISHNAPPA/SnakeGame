terraform {
  backend "s3" {
    bucket         = "microdegree-infra-statefile-backup-1"
    key            = "microdegree/2-eks/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "microdegree-terraform-locks"
    encrypt        = true
  }
}