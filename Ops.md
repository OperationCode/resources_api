# Deploying the Resources API

Once a release is built and deployed by CircleCI, deploy it to an environment using ArgoCD.

1. First, to connect to ArgoCD:
```
kubectl -n argocd port-forward service/argocd-server 8443:443 &
open https://localhost:8443
```
2. Login - credentials are in 1password, or ask someone for help
3. Pick up the new version in staging.
  - Go to https://localhost:8443/applications/resources-staging.k8s.operationcode.org,
  - Click the hamburger menu (3 dots, blue button), -> App Details -> Parameters
  - Click the "Edit" button and change the number of the image to the latest tag number
    - You can find the latest tag image in CircleCI or https://hub.docker.com/r/operationcode/resources-api/tags?page=1
    - Do not change it to `latest`, we want to manually deploy the correct image
  - As the new pods deploy, check the logs for errors
  - Validate the staging environment (try a few API calls, particularly GET and POST)
4. Repeat those steps for the production environment
  - When validating prod, please add a real resource to the API, not a test resource (there's no way to delete a test resource using the API)
