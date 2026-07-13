variable "project" {
  type    = string
  default = "microdegree"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "azs" {
  type    = list(string)
  default = ["ap-northeast-1a", "ap-northeast-1c", "ap-northeast-1d"]
}