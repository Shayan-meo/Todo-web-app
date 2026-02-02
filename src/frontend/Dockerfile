# =============================================================================
# Frontend Dockerfile - Multi-stage build for Next.js
# Base Image: node:20-alpine (as per spec: node:alpine)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies - Install node modules
# -----------------------------------------------------------------------------
FROM node:20-alpine AS deps

# Add libc compatibility for Alpine
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json* ./

# Install dependencies with clean install (production + dev for build)
RUN npm ci

# -----------------------------------------------------------------------------
# Stage 2: Builder - Build the Next.js application
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Set build-time environment variables
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build Next.js application (standalone output configured in next.config.mjs)
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Production - Minimal runtime image
# -----------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

# Set production environment
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Create .next directory with correct permissions
RUN mkdir .next \
    && chown nextjs:nodejs .next

# Copy standalone build output (includes server.js and required node_modules)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

# Copy static assets
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose application port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Run Next.js standalone server
CMD ["node", "server.js"]
