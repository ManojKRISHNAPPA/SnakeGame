
############################
# IAM Role - EKS Cluster
############################
resource "aws_iam_role" "itkannadigaru_eks_cluster_role" {
  name = "itkannadigaru_eks_cluster_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  role       = aws_iam_role.itkannadigaru_eks_cluster_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

############################
# IAM Role - Worker Nodes
############################
resource "aws_iam_role" "itkannadigaru_eks_node_role" {
  name = "itkannadigaru_eks_node_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "node_worker_policy" {
  role       = aws_iam_role.itkannadigaru_eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_cni_policy" {
  role       = aws_iam_role.itkannadigaru_eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "node_registry_policy" {
  role       = aws_iam_role.itkannadigaru_eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

############################
# EKS Cluster
############################
resource "aws_eks_cluster" "itkannadigaru" {
  name     = "itkannadigaru-cluster"
  role_arn = aws_iam_role.itkannadigaru_eks_cluster_role.arn

  vpc_config {
    subnet_ids         = aws_subnet.itkannadigaru_subnet[*].id
    security_group_ids = [aws_security_group.itkannadigaru_cluster_sg.id]
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy
  ]
}

############################
# EKS Node Group
############################
resource "aws_eks_node_group" "itkannadigaru" {
  cluster_name    = aws_eks_cluster.itkannadigaru.name
  node_group_name = "itkannadigaru-node-group"
  node_role_arn   = aws_iam_role.itkannadigaru_eks_node_role.arn

  subnet_ids = aws_subnet.itkannadigaru_subnet[*].id

  scaling_config {
    desired_size = 3
    max_size     = 5
    min_size     = 3
  }

  instance_types = ["t2.medium"]

  remote_access {
    ec2_ssh_key               = var.ssh_key_name
    source_security_group_ids = [aws_security_group.itkannadigaru_node_sg.id]
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_worker_policy,
    aws_iam_role_policy_attachment.node_cni_policy,
    aws_iam_role_policy_attachment.node_registry_policy
  ]
}