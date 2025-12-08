# ArgoCD App of Apps Configuration

This directory contains the ArgoCD App of Apps pattern for managing the car-lookup-service across multiple environments.

## Structure

```
argocd/
├── app-of-apps/           # Helm chart for App of Apps
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       └── car-lookup-service.yaml
└── environments/          # Environment-specific App definitions
    ├── ci.yaml
    ├── uat.yaml
    └── prod.yaml
```

## How It Works

1. **App of Apps Pattern**: Each environment (CI, UAT, PROD) has its own App of Apps application defined in `environments/`.

2. **Environment-Specific Configuration**: The App of Apps Helm chart uses the `env` parameter to select the correct values file:
   - CI: `values-ci.yaml`
   - UAT: `values-uat.yaml`
   - PROD: `values-prod.yaml`

3. **Version Management**: The `appVersion` parameter is updated by the CI/CD pipeline to deploy specific versions.

## Deployment

### Initial Setup

Apply the environment-specific App of Apps to your cluster:

```bash
# Deploy CI environment
kubectl apply -f argocd/environments/ci.yaml

# Deploy UAT environment
kubectl apply -f argocd/environments/uat.yaml

# Deploy PROD environment
kubectl apply -f argocd/environments/prod.yaml
```

### Update Version via CI/CD

To update the application version in an environment, modify the `appVersion` parameter:

```bash
# Update CI environment to v1.2.3
kubectl patch application apps-ci -n argocd --type merge -p '{"spec":{"source":{"helm":{"parameters":[{"name":"appVersion","value":"v1.2.3"}]}}}}'

# Or using ArgoCD CLI
argocd app set apps-ci -p appVersion=v1.2.3
```

### Update Version via GitHub Actions

The pipeline can update the version by modifying the environment file:

```yaml
# In your GitHub Actions workflow
- name: Update ArgoCD App Version
  run: |
    NEW_VERSION="${{ steps.version.outputs.tag }}"

    # Update the environment file
    yq eval ".spec.source.helm.parameters[] |= select(.name == \"appVersion\").value = \"$NEW_VERSION\"" \
      -i argocd/environments/ci.yaml

    # Commit and push
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add argocd/environments/ci.yaml
    git commit -m "Deploy $NEW_VERSION to CI"
    git push
```

## Sync Policies

### CI Environment
- **Automated**: `prune: true`, `selfHeal: true`
- Automatically syncs and prunes resources
- Suitable for continuous deployment

### UAT Environment
- **Automated**: `prune: false`, `selfHeal: true`
- Auto-syncs but doesn't prune
- Allows manual intervention

### Production Environment
- **Automated**: `prune: false`, `selfHeal: false`
- Manual sync required for safety
- Maximum control over production deployments

## Environment Differences

| Feature | CI | UAT | PROD |
|---------|-----|-----|------|
| Replicas | 1 | 2 | 3 |
| Autoscaling | Disabled | Disabled | Enabled (3-10) |
| CPU Request | 100m | 200m | 500m |
| Memory Request | 128Mi | 256Mi | 512Mi |
| Log Level | DEBUG | INFO | WARNING |
| Auto Prune | Yes | No | No |
| Auto Heal | Yes | Yes | No |

## Troubleshooting

### View Application Status
```bash
kubectl get applications -n argocd
argocd app get apps-ci
```

### Manual Sync
```bash
argocd app sync apps-ci
```

### View Differences
```bash
argocd app diff apps-ci
```

### Rollback
```bash
argocd app rollback apps-ci <history-id>
```
