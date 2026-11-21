# Security and safety policy

GROWN is scientific research software, not a hardened multi-tenant
job submission platform. Its user-supplied `env_activation` text is
included in generated PBS scripts: **accept configs only from
trusted sources** and inspect all generated scripts before executing
or submitting them.

Do not commit credentials, internal cluster hostnames, API keys,
tokens, private dataset URLs, personal home directories or executable
binaries obtained from an untrusted source. When reporting a
security-sensitive issue, avoid publishing exploit details or secrets
in a public issue. Contact the repository owner using GitHub's
private contact facilities, if available, before disclosure.

Model checkpoints and external packages may execute code at load
time; follow their upstream security guidance. Large simulations
should not run on interactive login nodes or GitHub CI.
