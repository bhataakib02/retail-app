# Deployment Guide for Vercel + Supabase

This guide will help you deploy the retail app to Vercel with Supabase as the database.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. A Supabase account and project (you already have one: `retailapp`)
3. Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Get Your Supabase Database URL

1. Go to your Supabase project dashboard: https://supabase.com/dashboard/project/wfcxwbmxvseweajyenzj
2. Navigate to **Settings** → **Database**
3. Scroll down to **Connection string** section
4. Under **Connection pooling**, copy the **URI** connection string
   - It will look like: `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`
   - Or you can use the **Connection string** (Transaction mode) which looks like: `postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres`

5. **Important**: Replace `[password]` with your actual database password if it's not already in the string.

## Step 2: Set Up Database Schema

Before deploying, you need to run the database migrations on your Supabase database:

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy the contents of `db/schema.sql`
4. Paste and run the SQL in the SQL Editor
5. Verify that tables are created: `users`, `products`, `orders`, `order_items`

Alternatively, you can run migrations locally:
```bash
# Set your DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:[password]@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres"

# Run migrations
python run_migrations.py
```

## Step 3: Deploy to Vercel

### Option A: Deploy via Vercel CLI

1. Install Vercel CLI (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy your project:
   ```bash
   vercel
   ```

4. Follow the prompts to link your project

5. Add environment variables:
   ```bash
   vercel env add DATABASE_URL
   # Paste your Supabase connection string when prompted
   
   vercel env add SECRET_KEY
   # Enter a random secret key for Flask sessions (e.g., generate one with: python -c "import secrets; print(secrets.token_hex(32))")
   ```

6. Deploy to production:
   ```bash
   vercel --prod
   ```

### Option B: Deploy via Vercel Dashboard

1. Push your code to GitHub/GitLab/Bitbucket
2. Go to https://vercel.com/dashboard
3. Click **Add New** → **Project**
4. Import your Git repository
5. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: `pip install -r requirements.txt`

6. Add Environment Variables:
   - Click **Environment Variables**
   - Add `DATABASE_URL` with your Supabase connection string
   - Add `SECRET_KEY` with a random secret (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

7. Click **Deploy**

## Step 4: Verify Deployment

1. After deployment, Vercel will provide you with a URL (e.g., `https://your-app.vercel.app`)
2. Visit the URL to verify the app is working
3. Test the login functionality:
   - Default admin credentials:
     - Email: `admin@admin.com`
     - Password: `admin123`

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Supabase PostgreSQL connection string | `postgresql://postgres:password@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres` |
| `SECRET_KEY` | Flask session secret key | Random 32+ character string |

## Troubleshooting

### Database Connection Issues

- Make sure your DATABASE_URL is correct and includes the password
- Verify your Supabase database is running (check project status in Supabase dashboard)
- Ensure your Supabase project allows connections from external IPs (default: enabled)

### Build Errors

- Check that all dependencies in `requirements.txt` are correct
- Verify Python version compatibility (Vercel uses Python 3.9 by default)
- Check Vercel build logs for specific error messages

### Static Files Not Loading

- Vercel handles static files automatically via the `vercel.json` configuration
- Make sure `static/` folder is included in your repository

## Important Notes

1. **File Uploads**: File uploads to `static/images/products/` will not persist on Vercel (serverless functions are stateless). Consider using Supabase Storage for product images instead.

2. **Sessions**: Flask sessions use server-side storage. For production, consider using Flask-Session with Redis or database-backed sessions.

3. **Database Migrations**: Run migrations before deploying or use Supabase SQL Editor to execute `db/schema.sql`.

## Getting Help

- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- Flask Docs: https://flask.palletsprojects.com/

