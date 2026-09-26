# GameApp Argo CD

This GitOps structure deploys only three GameApp containers: `frontend`, `backend`, and the `db-migrate` RDS schema job. Their manifests are separated under `base/frontend`, `base/backend`, and `base/db`.

Before deploying, update the Git repository URL in `argocd/app.yaml`, replace `your-org` and version tags in `overlays/production/kustomization.yaml`, and create the RDS secret without committing it:

```bash
kubectl -n gameapp create secret generic gameapp-rds \
  --from-literal=DB_HOST='your-rds-endpoint' \
  --from-literal=DB_PORT='5432' \
  --from-literal=DB_NAME='gameapp' \
  --from-literal=DB_USERNAME='gameapp_app' \
  --from-literal=DB_PASSWORD='your-rds-password'
```

Apply the Argo CD application with `kubectl apply -f argocd/app.yaml`.