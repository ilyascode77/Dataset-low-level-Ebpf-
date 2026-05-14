# GitHub Workflow

## Branching

Do not work directly on `main`. Use one branch per feature:

```bash
git checkout -b feature/k3s-lab
git checkout -b feature/tetragon-telemetry
git checkout -b feature/wazuh-integration
git checkout -b feature/detection-rules
git checkout -b docs/architecture
```

## Commit Style

Use clear commit messages:

```bash
git add .
git commit -m "Add K3s lab documentation"
git commit -m "Add Kubernetes namespaces"
git commit -m "Add Tetragon shell execution policy"
git commit -m "Add Wazuh decoder for Tetragon events"
```

Avoid vague messages:

```text
update
test
final
fix
```

## Push

After creating the GitHub repository:

```bash
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

For a feature branch:

```bash
git push -u origin feature/k3s-lab
```

Then create a Pull Request into `main`.
