// GuardRail — Deployment Safety Engine
// Solves the exact failure class behind the Cloudflare Nov 2025 outage (bad config, no validation),
// the AWS DynamoDB outage (no blast-radius control), and CrowdStrike 2024 (no canary, no auto-rollback).

const express = require('express');
const http = require('http');
const path = require('path');
const { WebSocketServer } = require('ws');
const Ajv = require('ajv');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// ---- In-memory state (swap for Postgres/Redis in production) ----
const deployments = [];       // history of every deployment attempt
const featureFlags = {};      // { flagName: { enabled: bool, rolloutPercent: number } }
const rollbackEvents = [];    // audit log of every auto-rollback

// ---- Broadcast helper: push live state to every connected dashboard ----
function broadcast(type, payload) {
  const msg = JSON.stringify({ type, payload });
  wss.clients.forEach(client => {
    if (client.readyState === 1) client.send(msg);
  });
}

// =====================================================================
// 1. CONFIG VALIDATION — catches the Cloudflare-style bug BEFORE deploy
// =====================================================================
const configSchema = {
  type: 'object',
  properties: {
    serviceName: { type: 'string', minLength: 1 },
    maxRules: { type: 'integer', minimum: 1, maximum: 200 },
    maxFileSizeKB: { type: 'integer', minimum: 1, maximum: 5000 },
    rules: { type: 'array', maxItems: 200 },
  },
  required: ['serviceName', 'maxRules', 'maxFileSizeKB', 'rules'],
  additionalProperties: true,
};

const ajv = new Ajv({ allErrors: true });
const validateConfig = ajv.compile(configSchema);

function validateAgainstLimits(config) {
  const errors = [];
  const ok = validateConfig(config);
  if (!ok) {
    validateConfig.errors.forEach(e => errors.push(`${e.instancePath || 'root'} ${e.message}`));
  }
  if (config.rules && config.rules.length > config.maxRules) {
    errors.push(
      `rules array has ${config.rules.length} entries but maxRules is ${config.maxRules} — this WILL crash the downstream proxy (this is the Cloudflare Nov 2025 failure mode)`
    );
  }
  const approxSizeKB = JSON.stringify(config).length / 1024;
  if (approxSizeKB > config.maxFileSizeKB) {
    errors.push(`config is ~${approxSizeKB.toFixed(1)}KB but maxFileSizeKB is ${config.maxFileSizeKB}KB`);
  }
  return { valid: errors.length === 0, errors };
}

app.post('/api/validate-config', (req, res) => {
  const result = validateAgainstLimits(req.body);
  res.json(result);
});

// =====================================================================
// 2. CANARY ROLLOUT ENGINE — progressive traffic shift with health gates
// =====================================================================
const CANARY_STAGES = [1, 10, 50, 100];
const ERROR_RATE_THRESHOLD = 0.02;
const STAGE_DELAY_MS = 2500;

function simulateTrafficErrorRate(chaosLevel) {
  const base = 0.001;
  const noise = Math.random() * 0.01;
  const injected = chaosLevel * (0.05 + Math.random() * 0.15);
  return base + noise + injected;
}

async function runCanaryRollout(deployment) {
  for (const stagePercent of CANARY_STAGES) {
    deployment.currentStage = stagePercent;
    deployment.status = 'rolling_out';
    await new Promise(r => setTimeout(r, STAGE_DELAY_MS));

    const errorRate = simulateTrafficErrorRate(deployment.chaosLevel);
    const stageResult = { stagePercent, errorRate, timestamp: Date.now() };
    deployment.stageHistory.push(stageResult);

    broadcast('stage_update', { deploymentId: deployment.id, ...stageResult, status: deployment.status });

    if (errorRate > ERROR_RATE_THRESHOLD) {
      deployment.status = 'rolled_back';
      deployment.rolledBackAtStage = stagePercent;
      deployment.finishedAt = Date.now();

      const event = {
        deploymentId: deployment.id,
        serviceName: deployment.serviceName,
        version: deployment.version,
        stagePercent,
        errorRate,
        threshold: ERROR_RATE_THRESHOLD,
        timestamp: Date.now(),
        reason: `Error rate ${(errorRate * 100).toFixed(2)}% exceeded ${(ERROR_RATE_THRESHOLD * 100)}% threshold at ${stagePercent}% traffic`,
      };
      rollbackEvents.push(event);
      broadcast('rollback', event);
      return;
    }
  }

  deployment.status = 'success';
  deployment.finishedAt = Date.now();
  broadcast('deploy_success', { deploymentId: deployment.id });
}

app.post('/api/deploy', (req, res) => {
  const { serviceName, version, config, chaosLevel = 0 } = req.body;

  if (!serviceName || !version || !config) {
    return res.status(400).json({ error: 'serviceName, version, and config are required' });
  }

  const validation = validateAgainstLimits(config);
  if (!validation.valid) {
    return res.status(422).json({
      blocked: true,
      reason: 'Deployment blocked at the config-validation gate — this never reached production.',
      errors: validation.errors,
    });
  }

  const deployment = {
    id: `dep_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
    serviceName,
    version,
    chaosLevel: Math.max(0, Math.min(1, Number(chaosLevel))),
    status: 'queued',
    currentStage: 0,
    stageHistory: [],
    startedAt: Date.now(),
  };
  deployments.unshift(deployment);
  broadcast('deploy_started', deployment);

  runCanaryRollout(deployment);

  res.json({ blocked: false, deployment });
});

app.get('/api/deployments', (req, res) => res.json(deployments.slice(0, 25)));
app.get('/api/rollback-events', (req, res) => res.json(rollbackEvents.slice(0, 25)));

// =====================================================================
// 3. FEATURE FLAGS — turn things off instantly, no redeploy required
// =====================================================================
app.get('/api/feature-flags', (req, res) => res.json(featureFlags));

app.post('/api/feature-flags', (req, res) => {
  const { name, enabled = false, rolloutPercent = 100 } = req.body;
  if (!name) return res.status(400).json({ error: 'name is required' });
  featureFlags[name] = { enabled, rolloutPercent };
  broadcast('flag_updated', { name, ...featureFlags[name] });
  res.json(featureFlags[name]);
});

app.post('/api/feature-flags/:name/toggle', (req, res) => {
  const flag = featureFlags[req.params.name];
  if (!flag) return res.status(404).json({ error: 'flag not found' });
  flag.enabled = !flag.enabled;
  broadcast('flag_updated', { name: req.params.name, ...flag });
  res.json(flag);
});

featureFlags['new-checkout-flow'] = { enabled: true, rolloutPercent: 100 };
featureFlags['ai-recommendations'] = { enabled: false, rolloutPercent: 0 };

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`GuardRail running at http://localhost:${PORT}`);
});
