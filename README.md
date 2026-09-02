# Sales Support Demo

A Streamlit app with login, an admin panel for uploading documents and
managing users, and a chat interface backed by a single shared cognee
"brain" hosted on Cognee Cloud. The chat only answers from what's been
uploaded or explicitly remembered.

## What you'll need before you start

- **Python 3.10, 3.11, 3.12, or 3.13** — not 3.14 or newer, and not older
  than 3.10. This is a hard requirement of `cogwit-sdk` (the Cognee Cloud
  client this app uses), not a suggestion. Check what you have:
  ```bash
  python3 --version
  ```
  If that's 3.14+ (or below 3.10), see step 2 below before doing anything
  else — trying to install dependencies with the wrong version will fail
  partway through with a confusing `ERROR: Could not find a version that
  satisfies the requirement cogwit-sdk` message.
- An [OpenAI](https://platform.openai.com/account/api-keys) API key
- A [Cognee Cloud](https://platform.cognee.ai) account and API key

## 1. Get the project onto your machine

Copy all the project files into one folder. You should end up with:

```
app.py
auth.py
login_page.py
admin_page.py
upload_page.py
chat_page.py
agent.py
requirements.txt
.env.example
```

(`credentials.json` and `chat_history.json` get created automatically the first time you run the app)

## 2. Create a virtual environment

**If `python3 --version` above was already 3.10–3.13**, just:
```bash
cd path/to/project
python3 -m venv .venv
source .venv/bin/activate
```

**If it wasn't** (e.g. you have 3.14, or nothing installed), install a
compatible version via Homebrew first, then point the venv at that
specific interpreter instead of your default `python3`:
```bash
brew install python@3.12
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
source .venv/bin/activate
```
(On Intel Macs, Homebrew's path is `/usr/local/opt/...` instead of
`/opt/homebrew/opt/...` — adjust accordingly.)

Your terminal prompt should now show `(.venv)` at the start of the line.
**Every new terminal tab needs this activation step run again** — it
doesn't persist across tabs or terminal restarts.

Confirm it worked:

```bash
which python3
python3 --version
```

The first should print a path ending in `.venv/bin/python3`, inside your
project folder. The second should show 3.10–3.13. If either looks wrong,
the venv isn't active or was built with the wrong interpreter — re-run
the steps above.

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `pip` isn't recognized as a command, use:

```bash
python3 -m pip install -r requirements.txt
```

## 4. Get your API keys

**OpenAI:** platform.openai.com → API Keys → Create new secret key.

**Cognee Cloud:** platform.cognee.ai → sign in → API Keys page → create
a key.

## 5. Create your `.env` file

Create an `.env` file, then fill in your actual keys:

```
COGNEE_API_KEY=ck_...
OPENAI_API_KEY=sk-...
```

`.env` is only read once, when the app process starts — if you change
it later, you'll need to fully stop and restart the app (not just
refresh the browser) for the change to take effect.

## 6. Run the app

```bash
streamlit run app.py
```

**Never run this with `python3 app.py`.** Streamlit apps need to run
through Streamlit's own command so it can start the local web server —
running the file directly with plain Python will fail or do nothing
useful, even if the code itself is fine.

It should open automatically in your browser at `http://localhost:8501`.
If it doesn't, open that URL manually.

## 7. Log in

Default admin credentials:

```
Username: admin
Password: admin123
```

From the admin panel you can:
- **Upload documents** — these get processed into the shared memory
  (cognee builds a knowledge graph from them; larger documents can take
  a minute or two to finish processing).
- **Remove users** — anyone you add can log in and use the chat.

## How it's put together

- **One shared "brain"** — every user's chat and every uploaded document
  goes into the same cognee dataset (`sales-support`). This is
  intentionally simple for a demo; there's no per-user data isolation.
- **Chat answers only from memory** — every message triggers a real
  cognee search first; the answer is generated strictly from what comes
  back, with an explicit instruction not to fill in unstated details.
  If nothing relevant is found, it says so instead of guessing.
- **Memory writes are explicit** — clicking "💾 Remember this" on an
  answer is what actually commits it to permanent memory. Nothing gets
  written automatically just from chatting.
- **Storage lives on Cognee Cloud**, not on your machine — check
  platform.cognee.ai's dashboard to see the dataset, browse what's been
  ingested, or clear it out if test data has piled up.

## If something goes wrong

- **"ModuleNotFoundError"** → your venv likely isn't active, or the
  package went to a `pipx` install instead of this project's venv.
  **Important: use `pip`, not `pipx`.** `pipx` installs tools in their own
  isolated environment, invisible to your project — it's meant for
  standalone CLI tools, not for packages you `import` in code. If you ever
  already have `streamlit` installed via `pipx`, that installation won't
  help this project and can actively cause confusing "it's installed but
  Python can't find it" errors. Check with:
  ```bash
  pipx list
  ```
  and uninstall anything that shows up there with `pipx uninstall <name>`
  to avoid the confusion later.
- **"ERROR: Could not find a version that satisfies the requirement
  cogwit-sdk"** → your venv was built with an incompatible Python version
  (3.14+, or older than 3.10). Delete it and rebuild using a Python
  3.10–3.13 interpreter — see step 2 above.
- **`streamlit run` uses the wrong environment** (e.g. a
  `ModuleNotFoundError` even though `pip show` confirms the package is
  installed) → run `which streamlit` to check where the command is
  actually resolving from. If it's not inside your project's `.venv`,
  something else on your PATH (another install, a leftover `pipx`
  install, etc.) is shadowing it. Safest fix: bypass the `streamlit`
  command entirely and run `python3 -m streamlit run app.py` instead —
  this guarantees it uses whichever Python you currently have active.
- **"externally-managed-environment" error on `pip install`** → this
  means you're not actually inside an active venv, even if it looks like
  you are. Delete and recreate it: `rm -rf .venv && python3 -m venv
  .venv && source .venv/bin/activate`.
- **Blank page, no errors anywhere** → hard-refresh the browser
  (`Cmd+Shift+R`), and try an incognito window to rule out a browser
  extension or stale cache.
- **A previously-working venv suddenly acts broken** → venvs don't
  survive being copied to a new folder or a new machine; they bake in
  absolute paths at creation time. Always create a fresh one per project
  location rather than copying an old one over.
- **Connection/TLS errors reaching Cognee Cloud** → if `api.cognee.ai`
  itself is having issues, you can point directly at your tenant's own
  URL instead by adding `COGWIT_API_BASE=https://tenant-<your-tenant-id>.aws.cognee.ai`
  to `.env` (find your tenant ID in the Cognee Cloud dashboard, or in
  any raw search response's `dataset_tenant_id` field).