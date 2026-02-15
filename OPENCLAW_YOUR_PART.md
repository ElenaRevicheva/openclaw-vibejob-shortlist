# OpenClaw: your part (WhatsApp + Telegram)

Config and skill are set up. Do these steps once — then both agents work.

---

## 1. API key (required for the AI)

OpenClaw needs one AI provider so it can answer (and run your job shortlist).

**Option A – Anthropic (Claude)**  
- Get an API key: https://console.anthropic.com/  
- Set it before starting OpenClaw:

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

**Or permanently:**  
- Create or edit `C:\Users\kirav\.openclaw\.env`  
- Add one line: `ANTHROPIC_API_KEY=sk-ant-your-key-here`  
- (Don’t commit this file.)

**Option B – OpenAI**  
- Get key from https://platform.openai.com/api-keys  
- Set `OPENAI_API_KEY` the same way, and in `openclaw.json` change the model to e.g. `openai/gpt-4o`.

---

## 2. Telegram agent (new bot)

1. Open Telegram, search for **@BotFather**.
2. Send: `/newbot`
3. Follow the prompts (name and username for the bot).
4. Copy the **token** BotFather gives you (looks like `123456789:ABCdefGHI...`).
5. Open the config and replace the placeholder:
   - File: `C:\Users\kirav\.openclaw\openclaw.json`
   - Find: `"botToken": "REPLACE_WITH_YOUR_BOT_TOKEN"`
   - Replace with: `"botToken": "YOUR_ACTUAL_TOKEN"`
6. Save the file. OpenClaw will reload the config.

7. **First time you message the bot:** You’ll get a **pairing code** in the chat. In a terminal run:  
   `openclaw pairing approve telegram YOUR_CODE`  
   After that, your Telegram is linked and you can use “job shortlist” and other commands.

---

## 3. WhatsApp agent (your existing number)

1. **Put your real number in the config**
   - File: `C:\Users\kirav\.openclaw\openclaw.json`
   - Find: `"allowFrom": ["+507XXXXXXXX"]`
   - Replace with your Panama number, e.g.: `"allowFrom": ["+50761234567"]`  
   - Use international format: `+507` + your number (no leading 0).

2. **Link WhatsApp (QR once)**
   - Start the Gateway (see step 4).
   - In a **new** terminal run:
     ```powershell
     openclaw channels login
     ```
   - Choose WhatsApp when asked.
   - Scan the QR code with your phone: WhatsApp → Settings → Linked devices → Link a device.
   - After that, your WhatsApp is the “WhatsApp agent”; only your number (in `allowFrom`) can use it.

---

## 4. Start the Gateway

In a terminal:

```powershell
openclaw gateway --port 18789 --verbose
```

Leave this running. You should see it load the config and connect to Telegram (and after WhatsApp login, to WhatsApp).

---

## 5. Test both agents

- **Telegram:** Open Telegram, find your new bot by its username, send: `job shortlist`  
- **WhatsApp:** From your Panama number, send the same to the linked “device” (OpenClaw): `job shortlist`

You should get back your YC AI Assistant shortlist from the job-list-filter pipeline.

---

## Quick checklist

| Step | What to do |
|------|------------|
| 1 | Set `ANTHROPIC_API_KEY` (or OpenAI) in env or `C:\Users\kirav\.openclaw\.env` |
| 2 | Create bot in @BotFather, put token in `openclaw.json` → `channels.telegram.botToken` |
| 3 | Put your Panama number in `openclaw.json` → `channels.whatsapp.allowFrom` |
| 4 | Run `openclaw channels login` and scan QR for WhatsApp |
| 5 | Run `openclaw gateway --port 18789 --verbose` and test “job shortlist” in both apps |

If the Gateway won’t start, run: `openclaw doctor` and fix any reported errors.
