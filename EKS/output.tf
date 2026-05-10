output "cluster_id" {
  value = aws_eks_cluster.qvprasanna.id
}

output "node_group_id" {
  value = aws_eks_node_group.qvprasanna.id
}

output "vpc_id" {
  value = aws_vpc.qvprasanna_vpc.id
}

output "subnet_id" {
  value = aws_subnet.qvprasanna_subnet[*].id
}