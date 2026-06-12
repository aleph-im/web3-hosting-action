# Aleph Web3 Hosting - GitHub Action

## What is it ?

A GitHub action that deploys a website or dApp frontend on Aleph Cloud.
For more information about Web3 Hosting with Aleph, check [the documentation](https://docs.aleph.cloud/devhub/deploying-and-hosting/web-hosting/#web3-hosting-on-aleph-cloud).

Deployments are paid with [Aleph Cloud credits](https://docs.aleph.cloud/devhub/sdks-and-tools/aleph-cli/commands/credits.html) held by the wallet that owns the website. Each deployment registers a new version of your website on your Aleph account, and automatically re-points the domains attached to it.

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
        uses: aleph-im/web3-hosting-action@v2
        with:
          path: 'out'
          private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
          domain: your-website.com
```

The wallet of `private-key` must hold credits, which can be bought with the [Aleph CLI](https://docs.aleph.cloud/devhub/sdks-and-tools/aleph-cli/) (`aleph credit buy`) or from the Aleph Cloud console.\
The website is identified by `website-name` (defaults to the repository name).

### Delegated deployments (recommended)

Instead of giving CI a wallet that holds funds, use a single **owner wallet** that holds the credits and owns all your websites, and a low-privilege **CI wallet** per repository that only signs deployments on its behalf. If a CI key leaks, revoke its authorization and nothing else is at risk: the scoped grant below can't touch the owner's funds, instances or other messages.

One-time setup with the [Aleph CLI](https://docs.aleph.cloud/devhub/sdks-and-tools/aleph-cli/), signing as the **owner** wallet:

```sh
aleph authorization add <ci-wallet-address> \
  --message-types store,aggregate \
  --aggregate-keys websites,domains \
  --channels ALEPH-CLOUDSOLUTIONS
```

Then put the CI wallet's private key in your repository secrets and pass the owner's address to the action:

```yml
- name: Deploy on Aleph
  uses: aleph-im/web3-hosting-action@v2
  with:
    path: 'out'
    private-key: ${{ secrets.ALEPH_CI_PRIVATE_KEY }}
    owner-address: '0xYourOwnerWalletAddress'
    domain: your-website.com
```

The website and its domains are owned by the owner wallet, and credits are consumed from it. The action fails early with a clear error if the authorization is missing or the owner has no credits.

### Deploy previews

On `pull_request` events, the action always deploys a free preview: no authentication required, no credits consumed, and a comment is added to the PR with the link to access it.\
Previews are garbage-collected ~24 hours after upload (re-run the job to refresh the link), and never touch your domain or website versions.

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
        uses: aleph-im/web3-hosting-action@v2
        with:
          path: 'out'
```

> Don't forget the `pull-requests: write` permission, or the comment won't be posted on the PR.

### Remove older versions

Each deployment creates a new version of your website, and previous versions stay stored on Aleph, where storage is billed in credits over time.\
Use the `retention_days` parameter to automatically delete the previous versions of this website that are older than this number of days. Only the previous versions of this website are ever touched, never the other files of the account.

```yml
- name: Deploy on Aleph
  uses: aleph-im/web3-hosting-action@v2
  with:
    path: 'out'
    private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
    domain: your-website.com
    retention_days: 30
```

### Custom domain DNS records

When linking a domain for the first time, configure the following DNS records (the action also prints them in its logs):

| Type  | Name                        | Value                                              |
| ----- | --------------------------- | -------------------------------------------------- |
| CNAME | `your-website.com`          | `ipfs.public.aleph.sh`                             |
| CNAME | `_dnslink.your-website.com` | `_dnslink.your-website.com.static.public.aleph.sh` |
| TXT   | `_control.your-website.com` | The owner wallet address                           |

> The TXT record must contain the address that **owns** the website: `owner-address` when using delegated deployments, the `private-key` wallet's address otherwise.

## Inputs

### Action inputs

| Name             | Description                                                                                       | Required | Default         |
| ---------------- | ------------------------------------------------------------------------------------------------- | -------- | --------------- |
| `path`           | Path to the static website's files (eg frontend/out)                                              | ✅        |                 |
| `private-key`    | The private key of the Ethereum wallet used to sign the deployment                                |          |                 |
| `owner-address`  | Address of the wallet that owns the website and pays with its credits (delegated deployments)     |          |                 |
| `website-name`   | Identifier of the website on your Aleph account                                                   |          | Repository name |
| `domain`         | Domain name to link to the deployed site (eg libertai.io)                                         |          |                 |
| `retention_days` | Delete previous versions of this website older than this number of days. Leave blank to keep all  |          |                 |

## Outputs

### Action outputs

You can get the following outputs from this action:

| Name      | Description                                            |
| --------- | ------------------------------------------------------ |
| `url`     | The deployed URL to access the website                 |
| `cid`     | The IPFS CID (v1) of the deployed files                |
| `version` | The version of the website on Aleph (empty for previews) |

### Example output

```yml
- name: Deploy on Aleph
  uses: aleph-im/web3-hosting-action@v2
  id: deploy
  with:
    path: 'out'
    private-key: ${{ secrets.ALEPH_PRIVATE_KEY }}
    domain: your-website.com
- name: Check outputs
  run: |
    echo "url: ${{ steps.deploy.outputs.url }}"
    echo "cid: ${{ steps.deploy.outputs.cid }}"
    echo "version: ${{ steps.deploy.outputs.version }}"
```

## Migrating from v1

- The same `private-key` secret works unchanged (raw hex private key).
- Payment switched from holding ALEPH tokens to [credits](https://docs.aleph.cloud/devhub/sdks-and-tools/aleph-cli/commands/credits.html): the owning wallet must hold credits or the deployed content is garbage-collected.
- Websites are now registered on your Aleph account with a name and version history, instead of being a bare IPFS pin.
- `pull_request` events now always deploy a free ephemeral preview, even if a private key is passed: production deployments only happen on other events (push, workflow_dispatch...).
- `retention_days` now only deletes the previous versions of this website, instead of all the files of the account older than the threshold.
- New `owner-address` input for delegated deployments with a single owner wallet and low-privilege CI keys.
