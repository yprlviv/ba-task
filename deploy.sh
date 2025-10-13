#!/bin/bash

# Facebook Ads Integration - Vercel Deployment Script

echo "🚀 Deploying Facebook Ads Integration to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "Please login to Vercel:"
    vercel login
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your application is now live!"
echo "📖 Check the deployment URL above for your live application"
echo ""
echo "🔧 Don't forget to set environment variables:"
echo "   vercel env add FACEBOOK_APP_ID"
echo "   vercel env add FACEBOOK_APP_SECRET" 
echo "   vercel env add FACEBOOK_ACCESS_TOKEN"
echo ""
echo "📚 For detailed instructions, see DEPLOYMENT_GUIDE.md"
