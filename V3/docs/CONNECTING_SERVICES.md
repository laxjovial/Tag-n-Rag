# Connecting External Services

This guide provides step-by-step instructions on how to obtain the necessary API keys and credentials for each external service that can be integrated with the application.

**IMPORTANT:** For each service, you will need to register your instance of this application on that service's developer portal. This is a standard and secure practice that gives you a unique `Client ID` and `Client Secret` for your application.

---

## 1. Google Drive

The integration with Google Drive allows users to both upload files from their Drive and query them "on-the-fly".

**Steps to get your credentials:**

1.  **Go to the Google Cloud Console:** Navigate to [https://console.cloud.google.com/](https://console.cloud.google.com/).
2.  **Create a New Project:** If you don't have one already, create a new project for this application.
3.  **Enable the Google Drive API:** In your project, go to the "APIs & Services" > "Library" section. Search for "Google Drive API" and enable it.
4.  **Configure the OAuth Consent Screen:**
    *   Go to "APIs & Services" > "OAuth consent screen".
    *   Choose "External" and create a new consent screen.
    *   Fill in the required app information (app name, user support email, developer contact).
    *   On the "Scopes" page, add the following scopes:
        *   `https://www.googleapis.com/auth/drive.readonly`
        *   `https://www.googleapis.com/auth/userinfo.profile`
    *   Add your email address as a "Test user" while your app is in testing mode.
5.  **Create Credentials:**
    *   Go to "APIs & Services" > "Credentials".
    *   Click "Create Credentials" and select "OAuth client ID".
    *   Choose "Web application" as the application type.
    *   Under "Authorized redirect URIs", add the following URLs (adjust the port if necessary):
        *   `http://localhost:8000/auth/google/callback`
        *   `http://127.0.0.1:8000/auth/google/callback`
    *   Click "Create". You will be shown your `Client ID` and `Client Secret`.
6.  **Configure the Application:**
    *   Download the JSON file containing your credentials.
    *   Rename this file to `client_secrets.json` and place it in the root directory of the `new_rag_system_v2` project.

---

## 2. Dropbox

The Dropbox integration will allow users to connect their Dropbox accounts.

**Steps to get your credentials:**

1.  **Go to the Dropbox App Console:** Navigate to [https://www.dropbox.com/developers/apps](https://www.dropbox.com/developers/apps).
2.  **Create a New App:**
    *   Choose an API: Select "Scoped Access".
    *   Choose the type of access: Select "Full Dropbox".
    *   Name your app.
3.  **Configure Permissions:**
    *   In your app's settings, go to the "Permissions" tab.
    *   Enable the following scopes: `files.content.read`, `account_info.read`.
4.  **Configure Redirect URIs:**
    *   In your app's settings, add your application's callback URI to the "Redirect URIs" field (e.g., `http://localhost:8000/auth/dropbox/callback`).
5.  **Get Your Keys:**
    *   In your app's settings, you will find your "App key" (Client ID) and "App secret" (Client Secret).
6.  **Configure the Application:**
    *   These keys will need to be added to a configuration file or as environment variables in the project once the integration is built.

---

## 3. Microsoft OneDrive

The OneDrive integration will use the Microsoft Graph API.

**Steps to get your credentials:**

1.  **Go to the Azure Portal:** Navigate to [https://portal.azure.com/](https://portal.azure.com/).
2.  **Go to App Registrations:** Search for and select the "App registrations" service.
3.  **Register a New Application:**
    *   Click "New registration".
    *   Give your application a name.
    *   Set the "Supported account types" (usually "Accounts in any organizational directory... and personal Microsoft accounts").
    *   Set the "Redirect URI": Select "Web" and enter your callback URL (e.g., `http://localhost:8000/auth/onedrive/callback`).
4.  **Get Your Client ID:** After creation, your "Application (client) ID" will be displayed on the overview page.
5.  **Create a Client Secret:**
    *   Go to "Certificates & secrets".
    *   Click "New client secret".
    *   Give it a description and an expiration, then click "Add".
    *   **Important:** Copy the "Value" of the secret immediately. It will not be shown again.
6.  **Configure API Permissions:**
    *   Go to "API permissions".
    *   Click "Add a permission", select "Microsoft Graph", then "Delegated permissions".
    *   Add the following permissions: `Files.Read.All`, `User.Read`.
7.  **Configure the Application:**
    *   The "Application (client) ID" and the client secret "Value" will need to be added to the project's configuration.

---

## 4. Atlassian Confluence

The Confluence integration will allow access to Confluence spaces and pages.

**Steps to get your credentials:**

1.  **Go to the Atlassian Developer Console:** Navigate to [https://developer.atlassian.com/console/myapps/](https://developer.atlassian.com/console/myapps/).
2.  **Create a New App:** Click "Create" and select "OAuth 2.0 integration".
3.  **Configure the App:**
    *   Give your application a name.
    *   Agree to the terms and click "Create".
4.  **Configure Permissions:**
    *   Go to the "Permissions" tab.
    *   Find "Confluence API" and add the necessary scopes, such as `read:confluence-content.all` and `read:confluence-space.summary`.
5.  **Configure Authorization:**
    *   Go to the "Authorization" tab.
    *   Click "Add" for the OAuth 2.0 flow.
    *   Add your callback URL (e.g., `http://localhost:8000/auth/confluence/callback`).
6.  **Get Your Keys:**
    *   Go to the "Settings" tab.
    *   Here you will find your `Client ID` and `Client secret`.
7.  **Configure the Application:**
    *   These keys will need to be added to the project's configuration.

---

## 5. Google Keep

As of the writing of this document, Google Keep **does not have a public API**. Therefore, a direct integration is not possible. The UI for Google Keep in this application is a non-functional placeholder to represent where such an integration would live if an API becomes available in the future.
