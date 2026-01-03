# Quick Setup Guide: Getting Your Supabase Database URL

## Step 1: Access Your Supabase Project

Your Supabase project:
- **Project Name**: `retailapp`
- **Project ID**: `wfcxwbmxvseweajyenzj`
- **Dashboard URL**: https://supabase.com/dashboard/project/wfcxwbmxvseweajyenzj

## Step 2: Get Database Connection String

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/wfcxwbmxvseweajyenzj/settings/database

2. Scroll down to **Connection string** section

3. You'll see different connection string options:
   - **Connection pooling (Recommended)**: Use this for serverless/Vercel
   - **Direct connection**: Use this for migrations/local development

4. Copy the **URI** format connection string. It will look like:
   ```
   postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
   
   OR for direct connection:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres
   ```

5. **Important**: Replace `[YOUR-PASSWORD]` with your actual database password (the one you set when creating the project)

## Step 3: Set Up Database Schema

1. Go to **SQL Editor** in your Supabase dashboard: https://supabase.com/dashboard/project/wfcxwbmxvseweajyenzj/sql/new

2. Copy the entire contents of `db/schema.sql` from this project

3. Paste it into the SQL Editor and click **Run**

4. Verify tables were created by running:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```
   
   You should see: `users`, `products`, `orders`, `order_items`

## Step 4: Use the Connection String

### For Local Development:
Create a `.env` file (or set environment variable):
```bash
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres"
SECRET_KEY="your-secret-key-here"
```

### For Vercel Deployment:
1. Go to your Vercel project settings
2. Navigate to **Environment Variables**
3. Add:
   - `DATABASE_URL` = your Supabase connection string (use pooling URL)
   - `SECRET_KEY` = a random secret key (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

## Troubleshooting

- **Connection Refused**: Make sure your Supabase project is running (not paused)
- **Authentication Failed**: Double-check your password
- **SSL Required**: Supabase requires SSL - the connection string should include SSL parameters automatically
- **Tables Not Found**: Make sure you ran the schema.sql in SQL Editor

## Need Help?

- Supabase Docs: https://supabase.com/docs/guides/database/connecting-to-postgres
- Connection Pooling: https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler

