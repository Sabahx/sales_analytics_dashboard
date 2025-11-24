# Neon PostgreSQL Credentials

Your Neon database has been set up! Use these credentials to update your deployments.

## Connection Details

**Full Connection String:**
```
postgresql://neondb_owner:npg_VogqX2pU1sNh@ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Individual Components:**
- **Host:** `ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech`
- **Port:** `5432`
- **Database:** `neondb`
- **User:** `neondb_owner`
- **Password:** `npg_VogqX2pU1sNh`

---

## 1. Update Railway API Environment Variables

Go to your Railway web service → **Variables** → Add/Update these:

```
DB_HOST=ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_VogqX2pU1sNh
```

**IMPORTANT:** Remove the old `DATABASE_URL` variable if it exists!

After updating, Railway will automatically redeploy your API.

---

## 2. Update Streamlit Cloud Secrets

Go to your Streamlit Cloud app → **Settings** → **Secrets** → Paste this:

```toml
# Database Configuration (Neon PostgreSQL)
DB_HOST = "ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech"
DB_PORT = "5432"
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "npg_VogqX2pU1sNh"

# Application Settings
ENVIRONMENT = "production"
DEBUG = "False"
LOG_LEVEL = "INFO"
```

Click **Save**, then **Reboot app**.

---

## 3. Update Local .env (Optional - for local testing)

If you want to test with Neon locally, update your `.env` file:

```env
DB_HOST=ep-delicate-block-ahzahxr5-pooler.c-3.us-east-1.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_VogqX2pU1sNh
```

---

## Benefits of Neon over Railway

✅ **More stable** - No random crashes
✅ **Better connection handling** - Supports connection pooling
✅ **Faster uploads** - No artificial timeouts
✅ **3GB free tier** - More than enough for this project
✅ **Auto-scaling** - Handles load better

---

## What's Next

Once the upload completes (you'll see "NEON SETUP COMPLETE!"), follow these steps:

1. Update Railway API variables (see section 1)
2. Update Streamlit Cloud secrets (see section 2)
3. Test your API: https://web-env-ef7b.up.railway.app/api/health
4. Test your dashboard on Streamlit Cloud
5. Verify ML forecasting now works with full dataset!
