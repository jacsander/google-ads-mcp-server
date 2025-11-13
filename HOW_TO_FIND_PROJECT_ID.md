# How to Find Your Google Cloud Project ID

Your **Project ID** is a unique identifier for your Google Cloud project. Here are several ways to find it:

## Method 1: Google Cloud Console (Easiest)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Look at the **top of the page** - you'll see a project selector dropdown
3. Click on it - your **Project ID** is shown in the dropdown
   - It's usually a string like: `my-project-123456` or `google-ads-mcp-abc123`
   - **Note:** Project ID is different from Project Name (the ID is what you need!)

**Visual Guide:**
```
┌─────────────────────────────────────────┐
│ Google Cloud Platform  [Project Name ▼]│  ← Click here
│                                         │
│ Project ID: my-project-123456          │  ← This is what you need!
└─────────────────────────────────────────┘
```

## Method 2: Project Settings Page

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the **project selector** at the top
3. Click **Project Settings** (or go directly to [Project Settings](https://console.cloud.google.com/iam-admin/settings))
4. Your **Project ID** is displayed at the top of the page

## Method 3: Using gcloud CLI

If you have `gcloud` installed and configured:

```bash
# Show current project ID
gcloud config get-value project

# Or list all your projects
gcloud projects list
```

## Method 4: From the URL

When you're in the Google Cloud Console, look at the URL:

```
https://console.cloud.google.com/apis/library?project=YOUR-PROJECT-ID
                                                    ↑
                                            This is your Project ID!
```

## Method 5: API & Services Page

1. Go to [APIs & Services](https://console.cloud.google.com/apis)
2. Look at the URL or the project selector at the top
3. Your Project ID is shown there

## Quick Check: Project ID vs Project Name

- **Project Name**: A human-readable name (e.g., "My Google Ads Project")
- **Project ID**: A unique identifier (e.g., `my-google-ads-project-123456`)

**You need the Project ID** (the one with numbers/letters, not spaces)

## If You Don't Have a Project Yet

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the **project selector** at the top
3. Click **New Project**
4. Enter a project name
5. Google will auto-generate a Project ID (you can edit it)
6. Click **Create**

**Note:** Make sure billing is enabled for your project!

## Example

Your Project ID might look like:
- `google-ads-mcp-123456`
- `my-ads-project-abc123`
- `fiskars-google-ads-2024`

It's usually lowercase letters, numbers, and hyphens.

## Verify It's Correct

You can verify your Project ID is correct by running:

```bash
gcloud projects describe YOUR-PROJECT-ID
```

If it works, you have the right ID!

---

**Quick Tip:** Once you find it, save it somewhere safe - you'll need it for the Cloud Run deployment command!

