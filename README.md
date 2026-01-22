# Aleph Web3 Hosting - GitHub Action

## What is it ?

A GitHub action that deploys a website or dApp frontend on Aleph Cloud.
For more information about Web3 Hosting with Aleph, check [the documentation](https://docs.aleph.cloud/devhub/deploying-and-hosting/web-hosting/#web3-hosting-on-aleph-cloud).

## Usage

### Classic usage

Deploy your website in production when commits are pushed to the `main` branch

```yml
on:
  push:
    branches:
      - main

jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    name: An example job to deploy a website
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
      - run: npm ci
      - run: npm build

      - name: Deploy on Aleph
        uses: aleph-im/web3-hosting-action@v1.1.4
        with:
          path: 'out'
          private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
          domain: your-website.com
```

### Deploy without a domain

If you don't need a domain name, don't pass anything to the corresponding parameter.\
A domain in the format `https://{ipfs-cid-v1}.ipfs.aleph.sh` will be allocated automatically.

```yml
- name: Deploy on Aleph
  uses: aleph-im/web3-hosting-action@v1.1.4
  with:
    path: 'out'
    private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
```

### Deploy previews

Deploy previews on your PRs, completely free without any authentication required.\
A comment will be added to the PR with the link to access the preview.

```yml
on:
  pull_request:

jobs:
  deploy-previews:
    runs-on: ubuntu-latest
    name: An example job to deploy previews
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
      - run: npm ci
      - run: npm build

      - name: Deploy on Aleph
        uses: aleph-im/web3-hosting-action@v1.1.4
        with:
          path: 'out'
```

> Don't forget the `pull-requests: write` permission, or the comment won't be posted on the PR.

> 💡 Previews will be garbage-collected after some time, for production usage please pass the private key of a wallet holding a sufficient amount of ALEPH tokens.

### Remove older files

Deploying a new version of your site will change the IPFS file your domain points to, but won't delete the files of older versions.\
You can use the `retention_days` parameter to automatically delete all the Aleph files in your account that are older than this number of days.

> ⚠️ Use this only if you are using this Aleph account only for deploying this website (which is recommended for security reasons), or this could remove files that you uploaded with the same wallet for other purposes.

```yml
- name: Deploy on Aleph
  uses: aleph-im/web3-hosting-action@v1.1.4
  with:
    path: 'out'
    private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
    domain: your-website.com
    retention_days: 30
```

## Inputs

### Action inputs

| Name             | Description                                                               | Required | Default |
| ---------------- | ------------------------------------------------------------------------- | -------- | ------- |
| `path`           | Path to the static website's files (eg frontend/out)                      | ✅        |         |
| `private-key`    | The private key of the Ethereum wallet to use to connect to Aleph         |          |         |
| `domain`         | Domain name to link to the deployed site (eg libertai.io)                 |          |         |
| `retention_days` | Delete files older than this number of days. Leave blank to skip deletion |          |         |

## Outputs

### Action outputs

You can get the following outputs from this actions:

| Name  | Description                            |
| ----- | -------------------------------------- |
| `url` | The deployed URL to access the website |

### Example output

```yml
- name: Deploy on Aleph
  uses: aleph-im/web3-hosting-action@v1.1.4
  id: deploy
  with:
    path: 'out'
    private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
    domain: your-website.com
- name: Check outputs
  run: |
    echo "url: ${{ steps.deploy.outputs.url }}"
```
