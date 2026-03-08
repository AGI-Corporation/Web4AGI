import express from "express";

const app = express();
app.use(express.json());

// In-memory store; replace with DB in production
const agentStore: Record<string, any> = {};

function initParcelAgent(parcel_id: string) {
  return {
    parcel_id,
    goals: ["maximize_community_engagement", "minimize_utility_risk"],
    metrics: {
      visit_score: Math.floor(Math.random() * 100),
      risk_score: parseFloat((Math.random()).toFixed(2)),
      stikk_points: Math.floor(Math.random() * 300),
      budget_usdx: 200
    },
    suggested_actions: [
      {
        title: "Add micro-reward for off-peak visits",
        description: "Offer 2 USDx per check-in between 2pm–5pm to increase foot traffic.",
        type: "incentive"
      },
      {
        title: "Flag underground risk zone",
        description: "High-density utilities detected. Recommend review before any construction permit.",
        type: "safety"
      }
    ],
    last_updated: new Date().toISOString()
  };
}

// GET /agent/:parcel_id
app.get("/agent/:parcel_id", (req, res) => {
  const { parcel_id } = req.params;
  if (!agentStore[parcel_id]) {
    agentStore[parcel_id] = initParcelAgent(parcel_id);
  }
  res.json(agentStore[parcel_id]);
});

// POST /agent/:parcel_id/goals
app.post("/agent/:parcel_id/goals", (req, res) => {
  const { parcel_id } = req.params;
  const { goals } = req.body;
  if (!agentStore[parcel_id]) agentStore[parcel_id] = initParcelAgent(parcel_id);
  agentStore[parcel_id].goals = goals;
  res.json({ ok: true, goals });
});

app.listen(3002, () => console.log("ParcelAgentServer on :3002"));
