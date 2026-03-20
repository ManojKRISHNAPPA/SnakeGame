package main

# Service should use LoadBalancer type
deny contains msg if {
  input.kind == "Service"
# Service should use LoadBalancer type
  input.spec.type != "LoadBalancer"
  msg = "Service type should be LoadBalancer"
}