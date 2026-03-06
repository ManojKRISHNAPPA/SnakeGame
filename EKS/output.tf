output "cluster_id" {
  value = aws_eks_cluster.itkannadigaru.id
}

output "node_group_id" {
  value = aws_eks_node_group.itkannadigaru.id
}

output "vpc_id" {
  value = aws_vpc.itkannadigaru_vpc.id
}

output "subnet_id" {
  value = aws_subnet.itkannadigaru_subnet[*].id
}