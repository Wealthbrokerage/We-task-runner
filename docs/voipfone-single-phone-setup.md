# Voipfone — single phone setup

Reference for registering **one** phone (deskphone, ATA or softphone) to a
Voipfone account. Settings below are from Voipfone's official General Phone
Configuration page.

Field names differ between handsets, so common aliases are listed.

## 1. Which account type?

For a single phone with no Virtual PBX, use **Single User**. Only use the
Multi-User settings if you are on Voipfone's PBX service.

### Single User account (no PBX) — the single-phone case

| Setting | Value | Also labelled |
|---|---|---|
| Username | Account number, e.g. `30999999` | Account, SIP ID, Authenticate ID, Authorised User |
| Password | Your phone password (usually 6 digits) | PIN |
| SIP server | `sip.voipfone.net` | Proxy, Registrar |
| Port | `5060` | — |
| Outbound proxy | `sip.voipfone.net` | — |
| Registration expiry | **60 seconds (1 minute)** | Proposed expiry |

Password location: `Master Account → Phone Settings` in the Control Panel.

### Multi-User account (with PBX)

Same server, port, outbound proxy and expiry as above. Only the credentials
differ:

| Setting | Value |
|---|---|
| Username | `<8-digit account>*<3-digit extension>`, e.g. `30999999*200` |
| Password | That extension's password (usually 6 digits) |

Password location: `Virtual PBX → PBX Extensions` in the Control Panel.

> **Everything else should be left at its default.** Do not change codecs,
> STUN or NAT settings unless you are troubleshooting a specific fault.

## 2. Can't find your password?

- Your password is **not** your memorable word.
- You may be on an **Extension Account**. Check your Dashboard: if the page
  title reads `Extension` followed by your extension number, you cannot see
  the password yourself — ask the account owner for it.

## 3. Test it

| Dial | Checks |
|---|---|
| `155` | Phone is connecting and registering correctly |
| `152` | Echo test — quality of your connection to Voipfone |

Then call the phone from a mobile to confirm inbound routing, and call out to
confirm the caller ID presented.

## 4. If it's still not working

**Check firmware first.** Voipfone add features that depend on up-to-date
equipment. Install the most recent **full release** from the manufacturer's
site — avoid beta firmware, which may not work correctly. Message Waiting
Indication (MWI) failing is a classic symptom of firmware that doesn't
support it properly.

Then work through:

| Symptom | Check |
|---|---|
| Won't register | Username format — account number alone for Single User, `account*extension` for PBX. Confirm the password is the *phone/extension* password, not the memorable word |
| Registers but no inbound calls | Registration expiry is set to 60s, and outbound proxy is set |
| Dial 155 fails | Registration is not succeeding — recheck credentials before anything else |
| One-way audio, or calls dropping ~30s | Router-side SIP ALG. Not a Voipfone setting — disabling SIP ALG resolves this on most routers |

Any standards-based SIP hardware works on the network. For an unusual device,
email Voipfone with as much detail as possible.

Voipfone customer service: **0345 868 5555**.

## Scope note

Voipfone publishes **no official public API**. Everything above is manual
Control Panel and handset configuration. Any future automation would have to
drive the undocumented JSON API used by their own web control panel, which can
change without notice — treat that as a deliberate decision, not a default.

---

# Mobile arrangement — iPhone, Voipfone app, forwarding and travel eSIM

How the business line is wired, and what to set before travelling.

## The arrangement

```
Caller dials business mobile
        |
        v
UK network forwards unconditionally  (never reaches the handset)
        |
        v
Voipfone number
        |
        v
Voipfone app on iPhone, over Wi-Fi or travel eSIM data
```

Because forwarding is **unconditional**, it is applied in the UK network
before the call is delivered. The call never roams, so there is no
international charge for receiving it.

## What it costs

- **No roaming charge to receive** — the call is never delivered abroad.
- **You do pay the forwarding leg** — the carrier bills the onward call from
  the mobile to the Voipfone number as a normal UK outbound call, for its full
  duration, on every incoming call. Check whether the tariff includes this.

## iPhone settings

`Settings → Mobile Service`

| Setting | Value | Why |
|---|---|---|
| Mobile Data | Travel eSIM | Otherwise the business allowance is used |
| Default Voice Line | Business | Forwarding and outbound calls depend on it |
| Data Roaming — travel eSIM | **ON** | Travel eSIMs connect as roaming profiles; off means no data at all |
| Data Roaming — business line | **OFF** | The main protection against a large bill |
| Allow Mobile Data Switching | Off | Stops iOS falling back to the business line's data |

Call forwarding: `Settings → Apps → Phone → Call Forwarding`.

Most iPhones allow only **two lines active at once** — adding a travel eSIM
may deactivate another line. Confirm the business line is still On.

## Before travelling

1. Confirm forwarding is on and points at the Voipfone number.
2. Data Roaming **off** on the business line.
3. Optionally toggle the business line **off** entirely on the device —
   forwarding lives in the network, so it keeps working with the line off,
   as long as the subscription is live.
4. Data Roaming **on** for the travel eSIM.
5. Make outbound calls from the Voipfone app, never the mobile line.

## Verification test

Turn **Wi-Fi off** — this is the only way to prove the eSIM is carrying calls.

1. Load a web page — travel eSIM data is live.
2. Dial `155` in the Voipfone app — the app registers over mobile data.
3. Ring the business mobile from another phone — forwarding arrives with no
   Wi-Fi in the chain.

Step 3 passing with Wi-Fi off means the arrangement will behave the same
abroad.

## Known gaps

- **SMS is not forwarded.** Call forwarding covers calls only. With the
  business line switched off, texts to it — including banking and 2FA codes —
  will not arrive. Move 2FA elsewhere before travelling, or leave the line on
  with data roaming off.
- **Watch for a forwarding loop.** The Voipfone number must not divert back
  to the business mobile. Mobile to Voipfone to mobile loops indefinitely and
  costs money on both legs.
- **Travel eSIM plans expire by date, not just data.** A lapsed plan fails
  silently — no alert, calls simply stop arriving.
- **Travel eSIMs are poor value for continuous domestic use.** A rolling
  monthly UK data SIM is cheaper and has no silent expiry.
