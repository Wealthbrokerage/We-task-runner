# Voipfone — single phone setup

Reference for registering **one** phone (deskphone, ATA or softphone) to a new
Voipfone account. Written for the simple case: one handset, one number.

## 1. Collect your credentials

Everything comes from the Voipfone **Control Panel** (log in at voipfone.co.uk).

| What | Where to find it | Looks like |
|---|---|---|
| Account number | Top of the Control Panel | 8 digits starting `30`, e.g. `30999999` |
| Phone / extension password | See "Which password" below | 6 digits, numeric |

### Which password?

There are two registration styles. For a **single phone, use Option A.**

**Option A — register to the master account (simplest).**
No Virtual PBX needed. The phone *is* the account.

- Username / SIP ID: your account number alone, e.g. `30999999`
- Password: the master account **phone password**, from
  `Services → Master Account → Phone Settings`

**Option B — register to a PBX extension.**
Use this only if you have the Virtual PBX and want extension dialling,
call groups, or plan to add more phones later.

- Extensions start at **200**. Each needs a name, an email address (voicemail
  is sent there) and its own 6-digit password.
- Set them up under `Services → Virtual PBX → PBX Extensions`.
- Username / SIP ID: `<account>*<extension>`, e.g. `30999999*200`
  (note the `*` separator, not a dot or dash)
- Password: that extension's own 6-digit password, not the account password.

## 2. Settings to enter on the phone

Field names vary by handset; the right-hand column lists common aliases.

| Setting | Value | Also labelled |
|---|---|---|
| SIP server / registrar | `sip.voipfone.net` | Proxy, Domain, Realm, Host |
| Port | `5060` | — |
| Outbound proxy | `sip.voipfone.net` | — |
| Username | `30999999` (A) or `30999999*200` (B) | SIP ID, Auth ID, Account, Login |
| Password | 6-digit password from step 1 | PIN, Auth password |
| Display name | Whatever you want shown | Caller ID name, Label |
| Transport | UDP | — |
| Registration expiry | `600` seconds | Register expires, Refresh |
| Preferred codec | G711a (a-law) | PCMA |

Notes:

- **Registration expiry**: handsets commonly default to 3600s (an hour).
  Dropping it to 600s keeps the NAT pinhole open so inbound calls arrive.
- **Codec**: some Voipfone softphones default to GSM to save bandwidth.
  Switch to a-law (G711a) for noticeably better call quality — fine on any
  normal broadband connection.
- **Outbound proxy**: not always required, but setting it resolves most
  "registers fine but no inbound calls" problems.

## 3. Test it

1. Check the phone shows **Registered** (Voipfone Control Panel will also
   show the extension/account as online).
2. Dial `123` — Voipfone's echo/test service — to confirm two-way audio.
3. Call the phone from a mobile to confirm inbound routing.
4. Make an outbound call to a mobile and check the caller ID presented.

## 4. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Won't register | Wrong username format | Check `*` separator and that the password matches the *extension*, not the account |
| Registers, no inbound calls | NAT timeout | Set expiry to 600s; add the outbound proxy |
| One-way audio | NAT / RTP blocked | Enable STUN on the handset; avoid SIP ALG on the router (turn it **off**) |
| Poor call quality | GSM codec | Switch to G711a (a-law) |
| Calls drop after ~30s | SIP ALG interfering | Disable SIP ALG on the router |

Voipfone customer service: **0345 868 5555**.

## Scope note

Voipfone publishes **no official public API**. Everything above is manual
Control Panel and handset configuration. Any future automation would have to
drive the undocumented JSON API used by their own web control panel, which can
change without notice — treat that as a deliberate decision, not a default.
