// Premier League Teams with statistical profiles for analytics & offline demo
export const EPL_TEAMS = [
  { name: "Arsenal", att: 91, def: 93, form: ['W', 'W', 'D', 'W', 'W'], rank: 2, pts: 84, title: 28, top4: 94, rel: 0 },
  { name: "Aston Villa", att: 84, def: 81, form: ['W', 'L', 'W', 'D', 'W'], rank: 4, pts: 68, title: 3, top4: 65, rel: 0 },
  { name: "Bournemouth", att: 78, def: 74, form: ['W', 'D', 'L', 'W', 'L'], rank: 11, pts: 49, title: 0, top4: 4, rel: 4 },
  { name: "Brentford", att: 80, def: 73, form: ['L', 'W', 'D', 'L', 'W'], rank: 12, pts: 46, title: 0, top4: 2, rel: 7 },
  { name: "Brighton", att: 82, def: 79, form: ['W', 'W', 'D', 'L', 'D'], rank: 7, pts: 57, title: 1, top4: 24, rel: 1 },
  { name: "Chelsea", att: 86, def: 80, form: ['W', 'W', 'D', 'W', 'L'], rank: 5, pts: 66, title: 4, top4: 55, rel: 0 },
  { name: "Crystal Palace", att: 76, def: 77, form: ['D', 'L', 'D', 'W', 'L'], rank: 15, pts: 41, title: 0, top4: 1, rel: 14 },
  { name: "Everton", att: 73, def: 78, form: ['L', 'D', 'W', 'D', 'L'], rank: 16, pts: 39, title: 0, top4: 0, rel: 19 },
  { name: "Fulham", att: 79, def: 76, form: ['W', 'L', 'W', 'D', 'W'], rank: 10, pts: 51, title: 0, top4: 6, rel: 3 },
  { name: "Ipswich", att: 72, def: 70, form: ['L', 'D', 'L', 'L', 'D'], rank: 19, pts: 28, title: 0, top4: 0, rel: 72 },
  { name: "Leicester", att: 74, def: 71, form: ['L', 'L', 'W', 'L', 'D'], rank: 17, pts: 34, title: 0, top4: 0, rel: 48 },
  { name: "Liverpool", att: 92, def: 90, form: ['W', 'W', 'W', 'D', 'W'], rank: 1, pts: 86, title: 38, top4: 98, rel: 0 },
  { name: "Man City", att: 94, def: 88, form: ['W', 'W', 'W', 'L', 'W'], rank: 3, pts: 83, title: 26, top4: 95, rel: 0 },
  { name: "Man United", att: 81, def: 78, form: ['D', 'W', 'L', 'D', 'W'], rank: 9, pts: 54, title: 0, top4: 18, rel: 1 },
  { name: "Newcastle", att: 85, def: 82, form: ['W', 'D', 'L', 'W', 'W'], rank: 6, pts: 63, title: 2, top4: 42, rel: 0 },
  { name: "Nott'm Forest", att: 77, def: 82, form: ['W', 'W', 'D', 'W', 'L'], rank: 8, pts: 55, title: 0, top4: 20, rel: 1 },
  { name: "Southampton", att: 70, def: 68, form: ['L', 'L', 'L', 'D', 'L'], rank: 20, pts: 24, title: 0, top4: 0, rel: 84 },
  { name: "Tottenham", att: 87, def: 79, form: ['L', 'W', 'L', 'W', 'W'], rank: 7, pts: 60, title: 1, top4: 35, rel: 0 },
  { name: "West Ham", att: 77, def: 74, form: ['L', 'D', 'W', 'L', 'L'], rank: 14, pts: 43, title: 0, top4: 1, rel: 10 },
  { name: "Wolves", att: 75, def: 72, form: ['L', 'L', 'D', 'W', 'L'], rank: 18, pts: 31, title: 0, top4: 0, rel: 58 }
];

export const TEAM_NAMES = EPL_TEAMS.map(t => t.name).sort();

export function getTeam(name) {
  return EPL_TEAMS.find(t => t.name === name) || EPL_TEAMS[0];
}

// Calculate realistic prediction, xG, probabilities and SHAP impacts
export function calculatePrediction(homeName, awayName) {
  const home = getTeam(homeName);
  const away = getTeam(awayName);

  // Home advantage factor (+0.35 xG)
  const baseHome = (home.att / 100) * 1.55 + 0.35 - (away.def / 100) * 0.45;
  const baseAway = (away.att / 100) * 1.35 - (home.def / 100) * 0.50;

  const xGHome = Math.max(0.4, Number((baseHome + Math.random() * 0.1 - 0.05).toFixed(1)));
  const xGAway = Math.max(0.3, Number((baseAway + Math.random() * 0.1 - 0.05).toFixed(1)));

  // Simulated score based on xG rounding with sports realism
  let homeGoals = Math.round(xGHome);
  let awayGoals = Math.round(xGAway);

  // Win probability calculation
  const strengthDiff = (home.att + home.def + 8) - (away.att + away.def);
  let homeWinP = Math.round(42 + strengthDiff * 1.1);
  let awayWinP = Math.round(30 - strengthDiff * 0.9);
  let drawP = Math.max(16, 100 - homeWinP - awayWinP);

  // Normalization
  homeWinP = Math.max(12, Math.min(80, homeWinP));
  awayWinP = Math.max(8, Math.min(75, awayWinP));
  drawP = 100 - homeWinP - awayWinP;
  if (drawP < 15) {
    drawP = 18;
    homeWinP = Math.round((100 - drawP) * (homeWinP / (homeWinP + awayWinP)));
    awayWinP = 100 - drawP - homeWinP;
  }

  // SHAP impact factors
  const formHomeScore = home.form.filter(f => f === 'W').length - home.form.filter(f => f === 'L').length;
  const formAwayScore = away.form.filter(f => f === 'W').length - away.form.filter(f => f === 'L').length;
  const formDiff = formHomeScore - formAwayScore;

  const shapFactors = [
    {
      name: "Rolling form, last 5",
      impact: Math.min(95, Math.max(25, Math.abs(formDiff * 18 + 50))),
      direction: formDiff >= 0 ? "home" : "away"
    },
    {
      name: "Home attack strength",
      impact: Math.min(95, Math.max(30, Math.round(home.att * 0.85))),
      direction: home.att >= 80 ? "home" : "away"
    },
    {
      name: "Head-to-head record",
      impact: Math.min(85, Math.max(20, Math.round(35 + (strengthDiff > 0 ? strengthDiff * 1.5 : strengthDiff * 1.2)))),
      direction: strengthDiff >= 0 ? "home" : "away"
    },
    {
      name: "Away defensive record",
      impact: Math.min(90, Math.max(25, Math.round(away.def * 0.75))),
      direction: away.def > 82 ? "away" : "home"
    },
    {
      name: "Key absences / Depth",
      impact: Math.min(70, Math.max(15, Math.round(25 + Math.random() * 20))),
      direction: home.rank < away.rank ? "home" : "away"
    }
  ];

  return {
    home: home.name,
    away: away.name,
    predictedScore: `${homeGoals} – ${awayGoals}`,
    xGHome,
    xGAway,
    probs: {
      Home: homeWinP,
      Draw: drawP,
      Away: awayWinP
    },
    homeForm: home.form,
    awayForm: away.form,
    shapFactors,
    ensemble: [
      { name: "XGBoost Classifier", weight: "0.55" },
      { name: "Random Forest", weight: "0.45" }
    ]
  };
}
