# Quick Start Guide - Deploy to Vercel with Supabase

## Step 1: Set Up Database Schema in Supabase

1. Go to your Supabase SQL Editor: https://supabase.com/dashboard/project/wfcxwbmxvseweajyenzj/sql/new

2. Copy the entire contents of `db/schema.sql` and paste it into the SQL Editor

3. Click **Run** to execute the SQL

4. Verify tables were created by running:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name;
   ```
   You should see: `order_items`, `orders`, `products`, `users`

## Step 2: Push Code to GitHub

If you haven't already, commit and push your changes:
```bash
git add .
git commit -m "Ready for deployment with Supabase"
git push origin main
```

## Step 3: Deploy to Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Click **Add New** → **Project**
3. Import your GitHub repository: `bhataakib02/retail-app`
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: `pip install -r requirements.txt`
5. **Add Environment Variables** (IMPORTANT!):
   - Click **Environment Variables** before deploying
   - Add `DATABASE_URL`:
     ```
     postgresql://postgres:B!@ckB1rD@$&85@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres
     ```
     ⚠️ **Note**: If your password has special characters, you may need to URL-encode them:
     - `!` = `%21`
     - `@` = `%40` (but NOT the @ before the domain)
     - `$` = `%24`
     - `&` = `%26`
     
     So the encoded version would be:
     ```
     postgresql://postgres:B%21%40ckB1rD%40%24%2685@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres
     ```
   
   - Add `SECRET_KEY`:
     ```
     be45662e6531f5a2c63d33b54009547924b93e479fb158063a09dba857246922
     ```
6. Click **Deploy**

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Add environment variables
vercel env add DATABASE_URL
# Paste: postgresql://postgres:B!@ckB1rD@$&85@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres

vercel env add SECRET_KEY
# Paste: be45662e6531f5a2c63d33b54009547924b93e479fb158063a09dba857246922

# Deploy to production
vercel --prod
```

## Step 4: Test Your Deployment

1. After deployment, Vercel will provide a URL like: `https://your-app.vercel.app`

2. Visit the URL and test:
   - Homepage loads
   - Register a new user
   - Login with admin credentials:
     - Email: `admin@admin.com`
     - Password: `admin123`

## Troubleshooting

### Database Connection Errors

- **Check password encoding**: If your password has special characters, ensure they're URL-encoded in the `DATABASE_URL`
- **Verify Supabase is running**: Check your Supabase project status
- **Check connection string**: Make sure it matches exactly from Supabase dashboard

### Build Errors

- Check Vercel build logs for specific error messages
- Ensure `requirements.txt` has all dependencies
- Verify Python version (set to 3.11 in `runtime.txt`)

### 404 Errors

- Check `vercel.json` configuration
- Ensure `api/index.py` exists and exports the Flask app correctly

## Important Notes

1. **File Uploads**: Product image uploads won't persist on Vercel (serverless). Consider using Supabase Storage for images in production.

2. **Sessions**: Flask sessions work but are stored in memory. For production, consider database-backed sessions.

3. **Database Password**: Keep your database password secure. Never commit it to Git!

## Need Help?

- Check `DEPLOYMENT.md` for detailed instructions
- Check `SETUP_SUPABASE.md` for Supabase setup
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs

