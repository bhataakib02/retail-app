# Fixing Vercel Deployment Error

## Issue: FUNCTION_INVOCATION_FAILED

If you're seeing "This Serverless Function has crashed" error, follow these steps:

## Step 1: Check Vercel Logs

1. Go to your Vercel dashboard
2. Click on your project
3. Go to the "Deployments" tab
4. Click on the failed deployment
5. Check the "Functions" tab or "Logs" tab to see the actual error

## Step 2: Verify Environment Variables

Make sure you've set these environment variables in Vercel:

1. Go to Project Settings → Environment Variables
2. Verify these are set:
   - `DATABASE_URL` - Your Supabase connection string
   - `SECRET_KEY` - A random secret key (e.g., `be45662e6531f5a2c63d33b54009547924b93e479fb158063a09dba857246922`)

**Important for DATABASE_URL:**
If your password has special characters like `!@$&`, you need to URL-encode them:
- `!` becomes `%21`
- `@` becomes `%40` (but NOT the @ before the domain)
- `$` becomes `%24`
- `&` becomes `%26`

Example: If your password is `B!@ckB1rD@$&85`, the URL-encoded version is `B%21%40ckB1rD%40%24%2685`

So your DATABASE_URL should be:
```
postgresql://postgres:B%21%40ckB1rD%40%24%2685@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres
```

## Step 3: Common Issues and Fixes

### Issue 1: Database Connection Error
**Symptom:** Error about database connection in logs

**Fix:** 
- Verify DATABASE_URL is correctly set
- Make sure password is URL-encoded
- Check that Supabase database is running

### Issue 2: Missing Dependencies
**Symptom:** ImportError in logs

**Fix:**
- Check `requirements.txt` has all packages
- Make sure versions are compatible

### Issue 3: Handler Format Error
**Symptom:** Handler not found errors

**Fix:**
- Verify `api/index.py` exists
- Make sure it exports `handler = app`

## Step 4: Re-deploy

After fixing issues:

1. Commit and push your changes:
   ```bash
   git add .
   git commit -m "Fix deployment issues"
   git push origin main
   ```

2. Vercel will automatically redeploy

3. Or manually trigger a redeploy from Vercel dashboard

## Quick Test

To test if the connection string works, you can test it locally:

```bash
# Set environment variable
export DATABASE_URL="postgresql://postgres:B%21%40ckB1rD%40%24%2685@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres"

# Test connection
python -c "import psycopg2; import os; conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require'); print('Connection successful!'); conn.close()"
```

## Still Having Issues?

1. Check Vercel build logs for specific error messages
2. Test the database connection locally first
3. Verify all environment variables are set correctly
4. Check that `runtime.txt` specifies Python 3.11
5. Ensure `vercel.json` is correctly configured

