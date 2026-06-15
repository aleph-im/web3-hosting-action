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

On `pull_request` events, the action deploys a preview of the pull request's build and comments the link on the PR. Each pull request gets its own preview (a website named `<website-name>-preview-pr-<number>`), updated on every commit. Previews use the same `private-key` (and `owner-address`, if you use delegation) as production and consume a small amount of credits.

To keep credits low, the action keeps only the latest build per pull request, and removes a pull request's preview automatically once it is closed or merged.

```yml
on:
  pull_request:
    # Add `closed` to tear a preview down the moment its PR is closed or merged.
    # Without it, closed previews are still reaped, but only on the next pull
    # request event (see "Preview cleanup" below).
    types: [opened, synchronize, reopened, closed]

jobs:
  deploy-previews:
    runs-on: ubuntu-latest
    name: An example job to deploy previews
    permissions:
      contents: read
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
          private-key: ${{ secrets.ALEPH_CI_PRIVATE_KEY }}
          owner-address: '0xYourOwnerWalletAddress'
```

> The `pull-requests: write` permission is required so the action can comment the preview link and detect closed PRs to clean up their previews.

#### Preview cleanup

On every pull request event the action first reaps the previews of any pull requests that are now closed, then deploys the current one. So previews are always cleaned up, but the timing depends on your trigger:

- **Without `closed`** in `types` (the default `pull_request` trigger): a closed PR's preview is removed on the next pull request event from any PR. Simple, but a preview can linger if the repository goes quiet.
- **With `closed`** in `types`: the action runs in cleanup-only mode for that event - it tears the preview down immediately and skips the deploy and comment steps (so it never recreates the preview it just removed). This run does not require credits on the billing wallet.

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
| `path`           | Path to the static website's files (eg frontend/out)                                              | ✅        |                    |
| `private-key`    | The private key of the Ethereum wallet used to sign the deployment                                | ✅        |                    |
| `owner-address`  | Address of the wallet that owns the website and pays with its credits (delegated deployments)     |          |                    |
| `website-name`   | Identifier of the website on your Aleph account                                                   |          | Repository name    |
| `domain`         | Domain name to link to the deployed site (eg libertai.io). Ignored for previews                   |          |                    |
| `retention_days` | Delete previous versions of this website older than this number of days. Leave blank to keep all  |          |                    |
| `github-token`   | Token used to detect closed pull requests and clean up their previews                             |          | Workflow token     |

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

- The same `private-key` secret works unchanged (raw hex private key), but it is now **required**, including for pull request previews.
- Payment switched from holding ALEPH tokens to [credits](https://docs.aleph.cloud/devhub/sdks-and-tools/aleph-cli/commands/credits.html): the owning wallet must hold credits or the deployed content is garbage-collected.
- Websites are now registered on your Aleph account with a name and version history, instead of being a bare IPFS pin.
- `pull_request` events deploy a per-PR preview (authenticated like production, kept to a single build, and removed automatically once the PR is closed); production deployments happen on other events (push, workflow_dispatch...).
- `retention_days` now only deletes the previous versions of this website, instead of all the files of the account older than the threshold.
- New `owner-address` input for delegated deployments with a single owner wallet and low-privilege CI keys.
