# Demonstration Pipeline Test And Deploy
This repository contains a simple electric car Lookup API. The app is largely irrelevant as it just used to illustrate the stages used to test and deploy code via a GitHub Actions pipeline.

This workflows expects users to merge into main and have the pipeline test and deploy from the initial branch and PR creation through to the production deploy.  This will use a Trunk based workflow rather than GitFlow.

To allow for this to work several gates are needed:

- PR testing. Initial testing to catch errors early on.
- Manual PR review
- Deployment of branch

![Entrac Pipelines](README-ASSETS/entrac-pipelines.drawio.png)

## Step 1.
Developer will checkout the repo on their local machine.  Then create a branch from main.  They will add the changes/fixes to this branch via the the add/commit cycle.  Then push this branch to the git remote (e.g GitHub).

_Justification_
This is a reasonable and largely standard Git workflow.

## Step 2.
Developer will create a pull request, requesting that their branch will be merged into MAIN branch.
