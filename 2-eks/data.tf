data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "microdegree-infra-statefile-backup-1"
    key    = "microdegree/1-network/terraform.tfstate"
    region = "ap-northeast-1"
  }
}