Author: Aditya Dogra

# SECURITY

- SMTP credentials are environment variables; never hardcode secrets.
- Subscription file contains user emails; treat as sensitive local data.
- Avoid logging full credential values.
