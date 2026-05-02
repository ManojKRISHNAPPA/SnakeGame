package main

# Service should use ClusterIP type
deny contains msg if {
  input.kind == "Service"
# Service should use ClusterIP type
  input.spec.type != "ClusterIP"
  msg = "Service type should be ClusterIP"
}