# Facebook Ads Integration - Vercel Deployment Guide

## 🚀 Quick Deployment to Vercel

This guide will help you deploy the Facebook Ads Integration project to Vercel in just a few minutes.

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: For connecting your repository
3. **Vercel CLI** (optional): `npm i -g vercel`

### Deployment Methods

## Method 1: GitHub Integration (Recommended)

### Step 1: Push to GitHub

1. **Create a new GitHub repository**
2. **Push your code**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Facebook Ads Integration"
   git branch -M main
   git remote add origin https://github.com/yourusername/facebook-ads-integration.git
   git push -u origin main
   ```

### Step 2: Deploy via Vercel Dashboard

1. **Go to [vercel.com/dashboard](https://vercel.com/dashboard)**
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure the project**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

### Step 3: Environment Variables

Add these environment variables in Vercel dashboard:

```
DEBUG=false
LOG_LEVEL=INFO
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_API_VERSION=v18.0
SECRET_KEY=your-production-secret-key
```

### Step 4: Deploy

Click **"Deploy"** and wait for the build to complete!

## Method 2: Vercel CLI

### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy

```bash
cd /home/yura/testtask
vercel
```

Follow the prompts:
- **Set up and deploy?** Y
- **Which scope?** Select your account
- **Link to existing project?** N
- **Project name:** facebook-ads-integration
- **Directory:** `./`

### Step 4: Set Environment Variables

```bash
vercel env add DEBUG
vercel env add FACEBOOK_APP_ID
vercel env add FACEBOOK_APP_SECRET
vercel env add FACEBOOK_ACCESS_TOKEN
```

## 📁 Project Structure for Vercel

The project is configured with the following Vercel-specific files:

```
/home/yura/testtask/
├── vercel.json              # Vercel configuration
├── api/
│   └── index.py            # Serverless function entry point
├── app/                    # FastAPI application
├── static/                 # Static files (HTML, CSS, JS)
├── requirements.txt        # Python dependencies
└── runtime.txt            # Python version specification
```

## 🔧 Configuration Files

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/app/main.py"
    }
  ]
}
```

### `api/index.py`
```python
from app.main import app
handler = app
```

## 🌐 Access Your Deployed Application

After successful deployment, you'll get URLs like:

- **API Root**: `https://your-project.vercel.app/`
- **API Documentation**: `https://your-project.vercel.app/docs`
- **UI Demo**: `https://your-project.vercel.app/static/index.html`
- **Health Check**: `https://your-project.vercel.app/health/`

## 🔍 Testing the Deployment

### Test API Endpoints

```bash
# Health check
curl https://your-project.vercel.app/health/

# API root
curl https://your-project.vercel.app/

# List campaigns
curl https://your-project.vercel.app/api/v1/campaigns/

# Validate advertiser
curl -X POST https://your-project.vercel.app/api/v1/advertisers/validate \
  -H "Content-Type: application/json" \
  -d '{"facebook_ad_account_id": "act_123456789"}'
```

### Test UI Interface

Visit these URLs in your browser:
- `https://your-project.vercel.app/static/index.html` - Main dashboard
- `https://your-project.vercel.app/static/campaign-details.html` - Campaign details
- `https://your-project.vercel.app/static/advertiser-management.html` - Advertiser management

## 🐛 Troubleshooting

### Common Issues

**1. Build Failures**
- Check that `requirements.txt` only includes necessary dependencies
- Ensure Python version is compatible (3.9 specified in `runtime.txt`)

**2. Static Files Not Loading**
- Verify `vercel.json` routes configuration
- Check that static files are in the correct directory

**3. API Errors**
- Check environment variables are set correctly
- Verify Facebook API credentials

**4. Import Errors**
- Ensure all imports use absolute paths from project root
- Check that `PYTHONPATH` is set correctly in `vercel.json`

### Debugging

**View Deployment Logs**:
```bash
vercel logs your-project-url
```

**Local Testing**:
```bash
vercel dev
```

## 🔒 Security Considerations

### Production Environment Variables

Make sure to set these in Vercel dashboard:

```
DEBUG=false
SECRET_KEY=generate-a-strong-secret-key
FACEBOOK_APP_SECRET=your-real-facebook-app-secret
FACEBOOK_ACCESS_TOKEN=your-production-access-token
```

### Domain Configuration

1. **Add Custom Domain** (optional):
   - Go to Vercel dashboard → Project → Settings → Domains
   - Add your custom domain
   - Configure DNS records

2. **HTTPS**: Automatically enabled by Vercel

## 📊 Monitoring and Analytics

Vercel provides built-in:
- **Performance Monitoring**
- **Error Tracking** 
- **Usage Analytics**
- **Function Logs**

Access these in your Vercel dashboard under the project settings.

## 🔄 Continuous Deployment

Once connected to GitHub:
- **Automatic deployments** on every push to main branch
- **Preview deployments** for pull requests
- **Rollback capability** to previous deployments

## 📞 Support

If you encounter issues:

1. **Check Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
2. **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
3. **Project Issues**: Check the deployment logs in Vercel dashboard

---

**🎉 Congratulations!** Your Facebook Ads Integration is now live on Vercel with global CDN, automatic HTTPS, and serverless scaling!
