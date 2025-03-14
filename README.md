# Aleph Web3 Hosting - GitHub Action

## What is it ?

A GitHub action that deploys a website / dApp frontend on Aleph Cloud.
For more information about Web3 Hosting, check [the documentation](https://docs.aleph.im/tools/web3-hosting)

## Inputs

### Action inputs

| Name          | Description                                                       | Required | Default |
| ------------- | ----------------------------------------------------------------- | -------- | ------- |
| `path`        | Path to the static website's files (eg frontend/out)              | ✅        |         |
| `private-key` | The private key of the Ethereum wallet to use to connect to Aleph |          |         |
| `domain`      | Domain name to link to the deployed site (eg libertai.io)         |          |         |
