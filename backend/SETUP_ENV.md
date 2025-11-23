# Setting Up Environment Variables

## Quick Setup

The server requires `ENCRYPTION_KEY` to start. Follow these steps:

### Step 1: Generate Keys

Run this command in the `backend` directory:

```bash
python generate_keys.py
```

This will output something like:
```
SECRET_KEY=KKcoLCjp4GIlLMIuxyAXEFLxi9vcdAsb
ENCRYPTION_KEY=nPgOAdnYQBigrtlH1KsgXC0oFpOiTrQx-_ZS-NSomNs=
```

### Step 2: Create .env File

Create a file named `.env` in the `backend` directory with this content:

```env
SECRET_KEY=KKcoLCjp4GIlLMIuxyAXEFLxi9vcdAsb
ENCRYPTION_KEY=nPgOAdnYQBigrtlH1KsgXC0oFpOiTrQx-_ZS-NSomNs=
DATABASE_URL=sqlite:///./aria.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Important:** Replace the keys with the ones generated in Step 1!

### Step 3: Verify

The `.env` file should be in: `backend/.env`

### Step 4: Restart Server

After creating the `.env` file, restart your server. It should start successfully.

## Manual Creation (Windows PowerShell)

```powershell
cd backend
python generate_keys.py
# Copy the output, then create .env file:
@"
SECRET_KEY=your-generated-secret-key-here
ENCRYPTION_KEY=your-generated-encryption-key-here
DATABASE_URL=sqlite:///./aria.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
"@ | Out-File -FilePath .env -Encoding utf8
```

## Manual Creation (Command Prompt)

```cmd
cd backend
python generate_keys.py
# Then manually create .env file with notepad:
notepad .env
# Paste the content from generate_keys.py output
```

## Troubleshooting

### Error: "ENCRYPTION_KEY environment variable is required!"

**Solution:** Create the `.env` file in the `backend` directory with the generated keys.

### Error: "Invalid ENCRYPTION_KEY format"

**Solution:** Make sure the ENCRYPTION_KEY is exactly 44 characters and base64-encoded. Re-generate if needed.

### Old API Keys Not Working

If you had API keys saved before setting up ENCRYPTION_KEY:
1. They were encrypted with a random key that's now lost
2. You need to re-enter them in Settings
3. New keys will work correctly with the persistent ENCRYPTION_KEY

---

**Note:** The `.env` file is in `.gitignore` and should NOT be committed to version control.

