---
description: How to obtain Google Client ID and Client Secret for OAuth 2.0
---

# Setting up Google OAuth 2.0 Credentials

Follow these steps to obtain your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

## 1. Create a Project in Google Cloud Console

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown at the top left and select **"New Project"**.
3. Enter a project name (e.g., "Citizen AI System") and click **"Create"**.

## 2. Configure OAuth Consent Screen

1. In the left sidebar, navigate to **APIs & Services** > **OAuth consent screen**.
2. Select **External** (unless you are in a G-Suite organization) and click **Create**.
3. Fill in the required fields:
   - **App Name**: Citizen AI System
   - **User Support Email**: Your email address
   - **Developer Contact Information**: Your email address
4. Click **Save and Continue**.
5. (Optional) Add Scopes: You can skip this for now or add `userinfo.email` and `userinfo.profile`.
6. Click **Save and Continue**.
7. **Test Users**: Add your own email address to test the login functionality.
8. Click **Save and Continue** and then **Back to Dashboard**.

## 3. Create Credentials

1. In the left sidebar, click on **Credentials**.
2. Click **+ CREATE CREDENTIALS** at the top and select **OAuth client ID**.
3. **Application type**: Select **Web application**.
4. **Name**: Enter a name (e.g., "Web Client 1").
5. **Authorized JavaScript origins**:
   - Add: `http://localhost:3000`
6. **Authorized redirect URIs**:
   - Add: `http://localhost:8000/auth/google/callback`
7. Click **Create**.

## 4. Copy Your Credentials

1. A dialog will appear with your **Client ID** and **Client Secret**.
2. Copy these values.

## 5. Add to Environment Variables

1. Open your `.env` file in the project root.
2. Add the following lines:

```env
GOOGLE_CLIENT_ID=your_copied_client_id
GOOGLE_CLIENT_SECRET=your_copied_client_secret
```

3. Restart your backend service for changes to take effect.
