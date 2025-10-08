# AWS Deployment Guide - Amplify + App Runner

Complete step-by-step guide to deploy RAG Knowledge Hub to AWS using Amplify (frontend) and App Runner (backend).

---

## 🎯 Architecture Overview

```
User Browser
    ↓
AWS Amplify (Next.js Frontend)
    ↓ HTTPS
AWS App Runner (FastAPI Backend)
    ↓ PostgreSQL
Supabase (Database + Auth)
```

**Why This Stack?**
- **Amplify:** Auto-deploys from GitHub, handles Next.js builds, CDN, HTTPS
- **App Runner:** Serverless container service, auto-scales, easy Docker deployment
- **Supabase:** Managed PostgreSQL with pgvector, already set up

**Cost:** ~$5-15/month (mostly App Runner compute time)

---

## ⚙️ Prerequisites

1. **AWS Account** with CLI configured
2. **GitHub Account** with code pushed
3. **Supabase Project** already created
4. **API Keys:** Cohere, Groq (from .env)

**Install AWS CLI:**
```bash
# macOS/Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download from: https://awscli.amazonaws.com/AWSCLIV2.msi

# Configure
aws configure
# Enter: Access Key ID, Secret Access Key, Region (eu-central-1), Output (json)
```

---

## 📦 Part 1: Deploy Backend to App Runner (20 min)

### Step 1.1: Push Docker Image to ECR

**Why ECR?** App Runner can pull from ECR (Elastic Container Registry) or GitHub. ECR is faster for Docker images.

```bash
# 1. Create ECR repository
aws ecr create-repository \
    --repository-name rag-backend \
    --region eu-central-1

# Output will show repository URI - copy this!
# Example: 123456789012.dkr.ecr.eu-central-1.amazonaws.com/rag-backend

# 2. Login to ECR
aws ecr get-login-password --region eu-central-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.eu-central-1.amazonaws.com

# 3. Build Docker image (from project root)
cd apps/backend
docker build -t rag-backend:latest .

# 4. Tag image for ECR
docker tag rag-backend:latest \
    123456789012.dkr.ecr.eu-central-1.amazonaws.com/rag-backend:latest

# 5. Push to ECR
docker push 123456789012.dkr.ecr.eu-central-1.amazonaws.com/rag-backend:latest
```

**Troubleshooting:**
- `docker build` fails? → Check Dockerfile syntax, ensure requirements.txt exists
- `docker push` fails? → Check AWS credentials, ensure ECR login successful
- Build slow? → Multi-stage build is working, wait 5-10 minutes

### Step 1.2: Create App Runner Service

**Via AWS Console** (easier for first deployment):

1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
2. Click **"Create service"**

**Source:**
- **Repository type:** Container registry
- **Provider:** Amazon ECR
- **Container image URI:** (paste your ECR URI from above)
  - Example: `123456789012.dkr.ecr.eu-central-1.amazonaws.com/rag-backend:latest`
- **ECR access role:** Create new role (App Runner will create it)
- **Deployment settings:** Manual (deploy only when you push new images)

**Service settings:**
- **Service name:** `rag-knowledge-hub-backend`
- **Virtual CPU:** 1 vCPU
- **Memory:** 2 GB
- **Port:** `8000`
- **Environment variables:** Click "Add environment variable" for each:

```
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase-dashboard
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-from-supabase
COHERE_API_KEY=your-cohere-api-key
GROQ_API_KEY=your-groq-api-key
CORS_ORIGINS=http://localhost:3000
```

**Note:** We'll update `CORS_ORIGINS` after deploying frontend.

**Health check:**
- **Protocol:** HTTP
- **Path:** `/health`
- **Interval:** 10 seconds
- **Timeout:** 5 seconds
- **Healthy threshold:** 1
- **Unhealthy threshold:** 5

**Auto scaling:**
- **Min instances:** 1
- **Max instances:** 5 (for demo, 1 is fine)

**Networking:**
- Leave default (public endpoint)

3. Click **"Create & deploy"**
4. Wait 5-10 minutes for deployment
5. **Copy the App Runner URL** when ready:
   - Example: `https://abcd1234.eu-central-1.awsapprunner.com`

**Test backend:**
```bash
curl https://abcd1234.eu-central-1.awsapprunner.com/health
# Expected: {"status":"healthy"}
```

---

## 🌐 Part 2: Deploy Frontend to Amplify (15 min)

### Step 2.1: Prepare Code

**Ensure code is pushed to GitHub:**

```bash
# From project root
git status
# Make sure all changes are committed

git add .
git commit -m "Prepare for AWS Amplify deployment"
git push origin main
```

### Step 2.2: Connect GitHub to Amplify

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. **Select GitHub** as source
4. Click **"Connect branch"**
   - Authorize AWS Amplify to access GitHub (first time only)
5. **Select repository:** `capstone-project-rag-based-knowledge-hub`
6. **Select branch:** `main` (or your deploy branch)

### Step 2.3: Configure Build Settings

**App settings:**
- **App name:** `rag-knowledge-hub`
- **Environment name:** `main`

**Monorepo detection:**
- **Root directory:** `apps/web`
- **Build output directory:** `.next` (auto-detected)

**Build settings** (Amplify auto-detects Next.js, but verify):

```yaml
version: 1
applications:
  - appRoot: apps/web
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: .next
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
```

**If build settings are missing, manually add:**
- Amplify → App settings → Build settings → Edit
- Paste YAML above

### Step 2.4: Add Environment Variables

**Before triggering build**, add environment variables:

1. Amplify → Your app → Environment variables
2. Click "Add variable" for each:

```
NEXT_PUBLIC_API_URL=https://abcd1234.eu-central-1.awsapprunner.com
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Get these values:**
- `NEXT_PUBLIC_API_URL`: Your App Runner URL from Part 1
- `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase Dashboard → Settings → API

3. Click **"Save"**

### Step 2.5: Deploy

1. Click **"Save and deploy"**
2. Amplify will:
   - Clone your repo
   - Install dependencies
   - Build Next.js app
   - Deploy to CDN
3. **Wait 10-15 minutes** for first build
4. Watch build logs for errors

**Build stages:**
```
Provision   (1 min)  - Spin up build environment
Build       (8 min)  - npm install, npm run build
Deploy      (2 min)  - Upload to CDN
Verify      (1 min)  - Health checks
```

5. **Copy Amplify URL** when deployment succeeds:
   - Example: `https://main.d1a2b3c4d5e6f7.amplifyapp.com`

**Test frontend:**
- Open URL in browser
- Should see landing page
- Try logging in (may fail due to CORS - we'll fix next)

---

## 🔗 Part 3: Connect Frontend to Backend (5 min)

### Step 3.1: Update CORS in App Runner

Now that you have the Amplify URL, update backend CORS:

1. Go to App Runner → Your service
2. **Configuration** → **Edit** (or "Configure")
3. Scroll to **Environment variables**
4. Find `CORS_ORIGINS` and update:
   ```
   CORS_ORIGINS=https://main.d1a2b3c4d5e6f7.amplifyapp.com
   ```
   **Important:** Use `https://` (not `http://`), no trailing slash

5. Click **"Deploy"** to apply changes
6. Wait 3-5 minutes for redeployment

### Step 3.2: Test End-to-End

1. **Open Amplify URL**
2. **Login** with test credentials:
   - Email: `employee@company.com`
   - Password: `dev`
3. **Navigate to Chatbot**
4. **Search:** "What is Atlas?" or "How do I deploy?"
5. **Expected result:**
   - AI-generated answer appears
   - Source citations shown below
   - Clicking citation opens document/handover

**If search fails, check:**
- Browser console for errors (F12 → Console)
- Network tab: Is API call reaching App Runner?
- App Runner logs: CloudWatch Logs (check for errors)

---

## 📊 Part 4: Monitoring & Logs

### App Runner Logs

**View logs:**
1. App Runner → Your service → **Logs**
2. Click "View in CloudWatch"
3. Filter by time range
4. Look for errors or warnings

**Common log messages:**
```
✅ "Starting RAG Knowledge Hub API..."
✅ "Database connection pool initialized"
✅ "Application startup complete"
❌ "Failed to connect to database" - Check DATABASE_URL
❌ "Invalid SUPABASE_JWT_SECRET" - Check env var
```

### Amplify Build Logs

**View build logs:**
1. Amplify → Your app → **Build history**
2. Click on a build
3. Expand each phase to see logs

**Common build errors:**
```
❌ "npm ERR!" - Dependency issue, check package.json
❌ "Type error" - TypeScript error (if ignoreBuildErrors: false)
❌ "Build failed" - Check build logs for specific error
```

### CloudWatch Metrics

**Monitor performance:**
1. CloudWatch → Metrics → App Runner
2. Select your service
3. View:
   - **RequestCount** - Number of API calls
   - **CPUUtilization** - CPU usage (should be <50% for demo)
   - **MemoryUtilization** - Memory usage
   - **4xxStatusCode** / **5xxStatusCode** - Errors

---

## 💰 Cost Breakdown

### App Runner
- **Compute:** $0.064/vCPU-hour + $0.007/GB-hour
- **1 vCPU + 2 GB:** ~$50/month if running 24/7
- **Provisioned concurrency:** Extra $40/month per instance
- **Free tier:** No free tier for App Runner

**Cost optimization:**
- For demo: 1 instance is enough (~$50/month)
- For production: Enable auto-scaling, min=1, max=5

### Amplify
- **Build minutes:** $0.01/minute (first 1,000 free)
- **Hosting:** $0.15/GB stored + $0.15/GB served
- **Demo estimate:** ~$5/month (small traffic)

### Total Monthly Cost
- **Demo (light traffic):** $55-60/month
- **Production (moderate traffic):** $100-150/month

**Save money:**
- Pause App Runner when not demoing (can't pause, but delete/recreate)
- Use AWS free credits (students get $100)
- Deploy only when needed, delete after demo

---

## 🚨 Troubleshooting

### "CORS error" in browser console

**Problem:** Frontend can't reach backend

**Fix:**
1. Check App Runner `CORS_ORIGINS` includes exact Amplify URL
2. Ensure `https://` (not `http://`)
3. No trailing slash
4. Redeploy App Runner after changing

### "JWT verification failed"

**Problem:** Wrong JWT secret

**Fix:**
1. Get JWT secret: Supabase Dashboard → Settings → API → JWT Secret
2. Update App Runner env var: `SUPABASE_JWT_SECRET`
3. Redeploy App Runner

### "No search results"

**Problem:** No data in database OR user has no project access

**Fix:**
```bash
# Check if chunks exist
psql $DATABASE_URL -c "SELECT COUNT(*) FROM chunks;"

# If 0: Run Notion ingestion or upload test documents
cd workers
python ingest_notion.py --notion-db-id <id>

# Check user's projects
psql $DATABASE_URL -c "SELECT project_id FROM employee_projects WHERE employee_id = '<user-uuid>';"

# Add user to project if empty
psql $DATABASE_URL -c "INSERT INTO employee_projects (employee_id, project_id, role) VALUES ('<user-uuid>', 'demo-project', 'member');"
```

### "App Runner deployment failed"

**Problem:** Docker image issue or missing env vars

**Fix:**
1. Check CloudWatch logs
2. Verify all env vars are set
3. Test Docker image locally:
   ```bash
   docker run -p 8000:8000 \
     -e DATABASE_URL="..." \
     -e SUPABASE_JWT_SECRET="..." \
     rag-backend:latest

   curl http://localhost:8000/health
   ```

### "Amplify build failed"

**Problem:** Build errors or missing dependencies

**Fix:**
1. Check build logs in Amplify console
2. Build locally first:
   ```bash
   cd apps/web
   npm run build
   # Fix any errors before pushing
   ```
3. Verify `next.config.mjs` has `output: 'standalone'`

### "Database connection failed"

**Problem:** Wrong DATABASE_URL or Supabase IP whitelist

**Fix:**
1. Verify DATABASE_URL format:
   ```
   postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```
2. Use **connection pooling** URL (not direct connection)
3. Supabase → Settings → Database → Connection string → "Connection pooling"

---

## 🔄 Redeployment & Updates

### Update Backend Code

```bash
# 1. Make changes to backend code
cd apps/backend

# 2. Rebuild Docker image
docker build -t rag-backend:latest .

# 3. Tag for ECR
docker tag rag-backend:latest \
    123456789012.dkr.ecr.eu-central-1.amazonaws.com/rag-backend:latest

# 4. Push to ECR
docker push 123456789012.dkr.ecr.eu-central-1.amazonaws.com/rag-backend:latest

# 5. Trigger App Runner deployment
aws apprunner start-deployment --service-arn <your-service-arn>
# Or use AWS Console: App Runner → Your service → Deploy
```

### Update Frontend Code

```bash
# 1. Make changes to frontend code
cd apps/web

# 2. Commit and push to GitHub
git add .
git commit -m "Update frontend"
git push origin main

# 3. Amplify auto-deploys (webhooks enabled by default)
# Watch build in Amplify console
```

---

## 🎯 Production Checklist

Before going live with real users:

- [ ] **Fix security issues:**
  - [ ] Remove JWT secret fallback (`auth.py:19`)
  - [ ] Enable TypeScript checks (`next.config.mjs`)
  - [ ] Remove console.log statements (`api.ts`)

- [ ] **Set up real authentication:**
  - [ ] Replace mock login with Supabase Auth
  - [ ] Sync employees table with Supabase Auth

- [ ] **Database:**
  - [ ] Run all migrations
  - [ ] Set up backups (Supabase does this automatically)
  - [ ] Verify HNSW index exists

- [ ] **Monitoring:**
  - [ ] Set up CloudWatch alarms (5xx errors, high CPU)
  - [ ] Enable X-Ray tracing (optional)

- [ ] **Security:**
  - [ ] Enable AWS WAF (optional, $5/month)
  - [ ] Review IAM roles (least privilege)
  - [ ] Rotate API keys regularly

- [ ] **Performance:**
  - [ ] Enable App Runner auto-scaling
  - [ ] Test under load (simulate 100 concurrent users)

- [ ] **Cost:**
  - [ ] Set up AWS Budget alerts
  - [ ] Review CloudWatch dashboards weekly

---

## 📚 Additional Resources

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [AWS Amplify Documentation](https://docs.amplify.aws/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Supabase Documentation](https://supabase.com/docs)

---

## 🆘 Support

**Issues?**
- App Runner errors: Check CloudWatch Logs
- Amplify errors: Check build logs in Amplify console
- Database errors: Check Supabase logs
- General: Review this guide's troubleshooting section

**Still stuck?** Check:
1. Environment variables (most common issue)
2. CORS settings (second most common)
3. Database connectivity

---

**🚀 You're ready to deploy! Follow the steps in order and you'll have a live demo in 30-45 minutes.**