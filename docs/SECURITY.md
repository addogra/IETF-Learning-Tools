
# SECURITY

## Security Posture

The project is a client-side/data-integration tool and does not run a persistent web service.
Primary security concerns are credential handling, PII handling, and safe dependency/runtime practices.

## Mandatory Controls

1. Never hardcode SMTP credentials.
2. Load SMTP credentials only from environment variables.
3. Treat subscription data as sensitive local data:
   - `~/.ietf_wg_agent_subscriptions.json`
4. Do not log full secrets, auth tokens, or full credential payloads.
5. Keep network calls bounded with explicit timeouts and handled exceptions.

## Data Handling Notes

- User `user_id` values may be email addresses and should be treated as PII.
- Daily report artifacts can contain WG activity summaries tied to recipients.
- Avoid committing local report artifacts or local subscription DB files.

## Secure Development Checklist

1. Review changes for accidental secret literals.
2. Validate no test fixtures include real credentials.
3. Validate error messages do not leak sensitive values.
4. Keep dependencies pinned and update with changelog review.
