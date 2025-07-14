# Google Cloud Setup for Omeyo Image Generation

This guide will help you set up Google Cloud with Vertex AI Imagen for image generation in your Omeyo application.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Basic familiarity with cloud services

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**: Visit [console.cloud.google.com](https://console.cloud.google.com)

2. **Create a new project**:
   - Click on the project dropdown at the top
   - Click "New Project"
   - Name: `omeyo-image-generation` (or your preferred name)
   - Click "Create"

3. **Note your Project ID**: You'll need this later (it's different from the project name)

## Step 2: Enable Required APIs

1. **Go to APIs & Services**: In the Google Cloud Console, navigate to "APIs & Services" > "Library"

2. **Enable these APIs**:
   - Search for "Vertex AI API" and enable it
   - Search for "Cloud Storage API" and enable it
   - Search for "IAM Service Account Credentials API" and enable it

## Step 3: Enable Vertex AI Imagen

1. **Go to Vertex AI**: Navigate to "Vertex AI" in the Google Cloud Console

2. **Enable Imagen**:
   - Go to "Generative AI Studio"
   - Click on "Image Generation"
   - Accept the terms of service
   - This enables Imagen for your project

## Step 4: Create Service Account

1. **Go to IAM & Admin**: Navigate to "IAM & Admin" > "Service Accounts"

2. **Create Service Account**:
   - Click "Create Service Account"
   - Name: `omeyo-image-generator`
   - Description: `Service account for Omeyo image generation`
   - Click "Create and Continue"

3. **Grant Permissions**:
   - Click "Grant Access"
   - Add these roles:
     - **Vertex AI User**
     - **Storage Object Viewer** (optional, for storing generated images)
   - Click "Continue" and then "Done"

4. **Create Key**:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Click "Create"
   - The JSON file will download automatically

## Step 5: Configure Your Application

1. **Move the service account key** to your project:
   ```bash
   # Move the downloaded JSON file to your project
   mv ~/Downloads/your-project-key.json /Users/eva/Omeyo/omeyo-goal-app/service-account-key.json
   ```

2. **Create/update your .env file**:
   ```bash
   # Add these lines to your .env file
   GOOGLE_APPLICATION_CREDENTIALS=/Users/eva/Omeyo/omeyo-goal-app/service-account-key.json
   GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id-here
   ```

   **Important**: Replace `your-actual-project-id-here` with your actual Google Cloud Project ID (not the project name).

## Step 6: Test Your Setup

1. **Run the test script**:
   ```bash
   cd /Users/eva/Omeyo/omeyo-goal-app
   python3 test_imagen_setup.py
   ```

2. **If the test passes**, restart your backend server:
   ```bash
   pkill -f "python.*app.main"
   python3 -m app.main
   ```

3. **Test the API endpoint**:
   ```bash
   curl -X POST http://localhost:8000/generate-image \
     -H "Content-Type: application/json" \
     -d '{"prompt": "A beautiful sunset over mountains"}'
   ```

## Step 7: Test in Frontend

1. **Start your frontend** (if not already running):
   ```bash
   cd /Users/eva/Omeyo/omeyo-dev
   npm run dev
   ```

2. **Go through the onboarding flow** and reach the "Future Dream Step"

3. **Enter a dream** in the textbox and click "Visualize My Dream"

4. **You should see a generated image** appear!

## Troubleshooting

### Common Issues:

1. **"Project not found" error**:
   - Double-check your Project ID in the .env file
   - Make sure you're using the Project ID, not the Project Name

2. **"Permission denied" error**:
   - Ensure the service account has the correct roles
   - Check that the JSON key file path is correct

3. **"API not enabled" error**:
   - Make sure you've enabled the Vertex AI API
   - Ensure Imagen is enabled in Generative AI Studio

4. **"Model not found" error**:
   - Verify that Imagen is enabled for your project
   - Check that you're in the correct region (us-central1)

### Getting Help:

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Imagen Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images)

## Cost Considerations

- Imagen has usage costs per image generated
- Monitor your usage in the Google Cloud Console
- Set up billing alerts to avoid unexpected charges

## Security Notes

- Keep your service account key secure
- Don't commit the key file to version control
- Consider using environment-specific keys for production 