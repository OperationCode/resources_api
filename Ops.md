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

# Backing up prod to staging

Every so often, we should back up prod to staging to ensure that we don't lose data, and also so that the staging data isn't stale during testing. And also, to blow away test changes that were made to staging while validating a new image version before going to prod.

1. Create a postgres image in the cluster
```bash
kubectl run -it postgres --image postgres:9.6 --rm -- /bin/bash
```
2. Run the following command to dump the resources data (replace username and dbname with the values in resources-api-secrets). You'll be prompted for the db password, so have that value ready as well.
```bash
pg_dump --clean --if-exists --inserts --quote-all-identifiers --host=python-prod.czwauqf3tjaz.us-east-2.rds.amazonaws.com --username=XXXX --dbname=XXX -f prod_backup.sql
```
3. Restore the data to staging with this command (have the password for staging db at the ready, because again, you'll be prompted for it)
```bash
psql --host=python-staging.czwauqf3tjaz.us-east-2.rds.amazonaws.com --username=XXXX --dbname=XXXX -f prod_backup.sql
```
