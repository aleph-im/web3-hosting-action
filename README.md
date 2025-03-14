# Aleph Web3 Hosting - GitHub Action

## What is it ?

A GitHub action that deploys a website or dApp frontend on Aleph Cloud.
For more information about Web3 Hosting with Aleph, check [the documentation](https://docs.aleph.im/tools/web3-hosting).

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
        uses: aleph-im/web3-hosting-action@v1
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
  uses: aleph-im/web3-hosting-action@v1
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
        uses: aleph-im/web3-hosting-action@v1
        with:
          path: 'out'
```

> Don't forget the `pull-requests: write` permission, or the comment won't be posted on the PR.

> 💡 Previews will be garbage-collected after some time, for production usage please pass the private key of a wallet holding a sufficient amount of ALEPH tokens.

## Inputs

### Action inputs

| Name          | Description                                                       | Required | Default |
| ------------- | ----------------------------------------------------------------- | -------- | ------- |
| `path`        | Path to the static website's files (eg frontend/out)              | ✅        |         |
| `private-key` | The private key of the Ethereum wallet to use to connect to Aleph |          |         |
| `domain`      | Domain name to link to the deployed site (eg libertai.io)         |          |         |

## Outputs

### Action outputs

You can get the following outputs from this actions:

| Name  | Description                            |
| ----- | -------------------------------------- |
| `url` | The deployed URL to access the website |

### Example output

```yml
- name: Deploy on Aleph
  uses: aleph-im/web3-hosting-action@v1
  id: deploy
  with:
    path: 'out'
    private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
    domain: your-website.com
- name: Check outputs
  run: |
    echo "url: ${{ steps.deploy.outputs.url }}"
```
