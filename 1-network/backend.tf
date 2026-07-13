terraform {
  backend "s3" {
    bucket         = "microdegree-infra-statefile-backup-1"
    key            = "microdegree/1-network/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "microdegree-terraform-locks"
    encrypt        = true
  }
}