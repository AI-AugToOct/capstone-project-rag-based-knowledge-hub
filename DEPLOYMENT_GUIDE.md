# AWS Deployment Guide - Vercel + App Runner

Complete step-by-step guide to deploy RAG Knowledge Hub using Vercel (frontend) and AWS App Runner (backend).

---

## 🎯 Architecture Overview

```
User Browser
    ↓
Vercel (Next.js Frontend)
    ↓ HTTPS
AWS App Runner (FastAPI Backend)
    ↓ PostgreSQL
Supabase (Database + Auth)
```

**Why This Stack?**
- **Vercel:** Auto-deploys from GitHub, optimized for Next.js, CDN, HTTPS, generous free tier
- **App Runner:** Serverless container service, auto-scales, easy Docker deployment
- **Supabase:** Managed PostgreSQL with pgvector, already set up

**Cost:** ~$57-64/month (mostly App Runner compute time, Vercel free tier)

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

## 🌐 Part 2: Deploy Frontend to Vercel (10 min)

### Step 2.1: Prepare Code

**Ensure code is pushed to GitHub:**

```bash
# From project root
git status
# Make sure all changes are committed

git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2.2: Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. **Import Git Repository:**
   - Click "Import" next to your GitHub repo
   - Or connect GitHub if first time (authorize Vercel to access GitHub)
   - Select repository: `capstone-project-rag-based-knowledge-hub`

### Step 2.3: Configure Project Settings

**Framework Preset:** Next.js (auto-detected)

**Root Directory:**
- Click "Edit"
- Enter: `apps/web`
- ✅ This tells Vercel to build from the monorepo subdirectory

**Build Settings:**
- **Build Command:** `npm run build` (auto-detected)
- **Output Directory:** `.next` (auto-detected)
- **Install Command:** `npm install` (auto-detected)

**Leave these as default - Vercel auto-detects Next.js correctly**

### Step 2.4: Add Environment Variables

**Before deploying**, add environment variables:

1. Scroll down to **Environment Variables** section
2. Add each variable:

```
NEXT_PUBLIC_API_URL=https://abcd1234.awsapprunner.com
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Get these values:**
- `NEXT_PUBLIC_API_URL`: Your App Runner URL from Part 1
- `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase Dashboard → Settings → API

**Important:** Make sure to add these for "Production" environment

### Step 2.5: Deploy

1. Click **"Deploy"**
2. Vercel will:
   - Clone your repo
   - Install dependencies
   - Build Next.js app
   - Deploy to Edge Network
3. **Wait 3-5 minutes** for first build (faster than traditional hosting!)
4. Watch build logs in real-time

**Build stages:**
```
Building    (2 min)  - npm install, npm run build
Deploying   (1 min)  - Upload to Edge Network
Ready       (30s)    - Health checks & DNS propagation
```

5. **Copy Vercel URL** when deployment succeeds:
   - Example: `https://your-app.vercel.app` or `https://ghannam.vercel.app`

**Test frontend:**
- Open URL in browser
- Should see landing page
- Try logging in (may fail due to CORS - we'll fix next)

---

## 🔗 Part 3: Connect Frontend to Backend (5 min)

### Step 3.1: Update CORS in App Runner

Now that you have the Vercel URL, update backend CORS:

1. Go to App Runner → Your service
2. **Configuration** → **Edit** (or "Configure")
3. Scroll to **Environment variables**
4. Find `CORS_ORIGINS` and update:
   ```
   CORS_ORIGINS=https://your-app.vercel.app
   ```
   **Important:** Use `https://` (not `http://`), no trailing slash

   **Example:** `CORS_ORIGINS=https://ghannam.vercel.app`

5. Click **"Deploy"** to apply changes
6. Wait 3-5 minutes for redeployment

### Step 3.2: Test End-to-End

1. **Open Vercel URL** (e.g., https://ghannam.vercel.app)
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
- Verify CORS_ORIGINS matches your exact Vercel URL

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

### Vercel Build Logs

**View build logs:**
1. Vercel → Your project → **Deployments**
2. Click on a deployment
3. Click "Building" or "View Function Logs"

**Common build errors:**
```
❌ "npm ERR!" - Dependency issue, check package.json
❌ "Type error" - TypeScript error (if ignoreBuildErrors: false in next.config.mjs)
❌ "Build failed" - Check build logs for specific error
❌ "ENOENT" - Missing file, check root directory setting (should be apps/web)
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
- **1 vCPU + 2 GB (24/7):**
  - vCPU: $0.064 × 730 = **$46.72**
  - Memory: $0.007 × 2 × 730 = **$10.22**
  - **Total: ~$57/month**
- **0.25 vCPU + 0.5 GB (24/7):** ~$14/month (for low traffic)
- **Free tier:** No free tier for App Runner

**Cost optimization:**
- For demo: Scale down to 0.25 vCPU (~$14/month)
- For production: Keep 1 vCPU, enable auto-scaling (min=1, max=5)

### Vercel
- **Hobby (Free):** 100 GB bandwidth, unlimited requests, unlimited deployments
- **Pro ($20/month):** 1 TB bandwidth, priority support, advanced analytics
- **Demo/production estimate:** **$0/month** (free tier is very generous)

**When to upgrade:**
- Only if you exceed 100 GB bandwidth/month (rare for small-medium teams)
- If you need team collaboration features

### Total Monthly Cost
- **Demo (light traffic):** $14/month (App Runner 0.25 vCPU + Vercel Free)
- **Small team (current setup):** $57/month (App Runner 1 vCPU + Vercel Free)
- **Production (with scaling):** $57-114/month (App Runner auto-scale + Vercel Free)

**Save money:**
- Scale down App Runner to 0.25 vCPU for demos (~$14/month)
- Use AWS free credits (students get $100)
- Vercel free tier covers most use cases (no need to upgrade)

---

## 🚨 Troubleshooting

### "CORS error" in browser console

**Problem:** Frontend can't reach backend

**Fix:**
1. Check App Runner `CORS_ORIGINS` includes exact Vercel URL
2. Ensure `https://` (not `http://`)
3. No trailing slash
4. Example: `CORS_ORIGINS=https://ghannam.vercel.app`
5. Redeploy App Runner after changing
6. Verify Vercel deployment is using correct `NEXT_PUBLIC_API_URL`

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

### "Vercel build failed"

**Problem:** Build errors or missing dependencies

**Fix:**
1. Check build logs in Vercel dashboard
2. Verify Root Directory is set to `apps/web`
3. Build locally first:
   ```bash
   cd apps/web
   npm run build
   # Fix any errors before pushing
   ```
4. Check environment variables are set correctly in Vercel
5. Verify `next.config.mjs` has `output: 'standalone'`

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

# 3. Vercel auto-deploys (Git integration enabled by default)
# Watch build in Vercel dashboard → Deployments
# Deployment typically completes in 2-3 minutes
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
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Supabase Documentation](https://supabase.com/docs)

---

## 🆘 Support

**Issues?**
- App Runner errors: Check CloudWatch Logs
- Vercel errors: Check build logs in Vercel dashboard → Deployments
- Database errors: Check Supabase logs
- General: Review this guide's troubleshooting section

**Still stuck?** Check:
1. Environment variables (most common issue)
   - Vercel: Settings → Environment Variables
   - App Runner: Configuration → Environment variables
2. CORS settings (second most common)
   - Must match exact Vercel URL
3. Root directory in Vercel (should be `apps/web`)
4. Database connectivity

---

**🚀 You're ready to deploy! Follow the steps in order and you'll have a live demo in 20-30 minutes.**