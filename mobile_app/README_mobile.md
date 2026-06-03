Mobile app (Expo) for AI Money Mentor

Quick start

1. Install Expo CLI if needed:

```bash
npm install -g expo-cli
```

2. From `mobile_app/` install dependencies:

```bash
npm install
```

3. Start the Expo development server:

```bash
npm run start
```

4. If running on an Android emulator the default (http://10.0.2.2:8000) will work.

   For a physical device, you have two options:
   - Add your host IP to `app.json` under `expo.extra.API_BASE`, e.g.:

```json
{
  "expo": {
    "extra": { "API_BASE": "http://192.168.1.5:8000" }
  }
}
```

   - Or set it at runtime by calling `setApiBase('http://192.168.1.5:8000')` from developer code or the JS console.


5. Use the mobile app to register, login, create a new analysis record, view history, and update saved records.

Backend

Make sure the API is running (`python main.py`) and accessible from the device/emulator.
