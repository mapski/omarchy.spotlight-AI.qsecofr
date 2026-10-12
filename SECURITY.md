# Security and privacy

This is a private release candidate, not a security-certified product. Omarchy plugins share the shell process and run with the user's permissions.

## Intended boundary

- Ordinary app/file search does not invoke AI.
- AI is opt-in with an explicit provider/model; no silent fallback.
- Q&A only: no agent tool, shell, filesystem mutation or desktop-control interface is exposed to the model.
- Native Claude/Codex execution remains blocked. Successful authentication does not remove those blocks.
- Local HTTP adapters require loopback, disable proxies and reject redirects. The jcode relay applies that boundary to inference and accepts one request for the selected model.
- Model discovery never installs runtimes or downloads/loads weights.
- Request size, output size, timeouts, cancellation and process-group cleanup are bounded.

## Credentials and history

App-owned ChatGPT tokens live in permission-restricted state files, not in source control or the UI. They are not encrypted at rest and do not resist another process with the same user's access. The plugin does not scrape browser sessions or copy native CLI authentication stores.

App history is bounded and clearable. Removing the plugin retains state; clearing history does not revoke tokens. jcode uses a temporary private HOME/configuration; its positional prompt can be visible to processes allowed to inspect command lines while it runs. See [details](docs/JCODE.md).

## Evidence and limits

75 offline tests and synthetic real-binary jcode probes passed. The tests cover no-tools requests, unsolicited tool rejection, redirect rejection, selection binding and cancellation boundaries. Live inference, service-side behavior and answer accuracy remain unverified. This does not establish absence of all vulnerabilities.

## Report privately

Repository collaborators should use GitHub private vulnerability reporting if the repository exposes it, or contact the repository owner privately through an existing trusted channel. If no private channel is available, open an issue asking for one without exploit details or sensitive data. Do not paste tokens, private prompts, browser callback URLs or account files into issues.

Include the candidate version, platform, reproducible steps using synthetic data and expected/observed behavior. There is no promised response-time SLA for this preview.
