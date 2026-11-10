import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { TEAM_NAMES, calculatePrediction } from '../data/eplData.js';

export default function Predictor() {
  const [home, setHome] = useState("Arsenal");
  const [away, setAway] = useState("Man City");
  const [prediction, setPrediction] = useState(() => calculatePrediction("Arsenal", "Man City"));
  const [loading, setLoading] = useState(false);

  // Compute prediction whenever home/away changes
  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    const clientPred = calculatePrediction(home, away);

    // Try live API backend, fallback gracefully to client calculations
    axios.post('/predict', { home_team: home, away_team: away }, { timeout: 2500 })
      .then(res => {
        if (!isMounted) return;
        const data = res.data;
        if (data && data.probs) {
          const homeP = Math.round((data.probs.Home || 0.46) * 100);
          const drawP = Math.round((data.probs.Draw || 0.27) * 100);
          const awayP = 100 - homeP - drawP;

          setPrediction({
            ...clientPred,
            probs: { Home: homeP, Draw: drawP, Away: awayP },
            shapUrl: data.shap_url ? `${axios.defaults.baseURL || ''}${data.shap_url}` : null
          });
        }
      })
      .catch(() => {
        if (isMounted) {
          setPrediction(clientPred);
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [home, away]);

  const handleHomeChange = (e) => {
    const val = e.target.value;
    if (val === away) {
      const alt = TEAM_NAMES.find(t => t !== val && t !== home) || "Liverpool";
      setAway(alt);
    }
    setHome(val);
  };

  const handleAwayChange = (e) => {
    const val = e.target.value;
    if (val === home) {
      const alt = TEAM_NAMES.find(t => t !== val && t !== away) || "Arsenal";
      setHome(alt);
    }
    setAway(val);
  };

  const swapTeams = () => {
    setHome(away);
    setAway(home);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Match Hero Card */}
      <section className="card grid grid-cols-1 md:grid-cols-3 gap-6 items-center text-center">
        {/* Home Team */}
        <div>
          <label className="mut uppercase tracking-wider font-semibold block text-xs" htmlFor="h">
            Home Team
          </label>
          <select
            id="h"
            value={home}
            onChange={handleHomeChange}
            className="custom-select w-full mt-2 font-medium"
          >
            {TEAM_NAMES.map(t => (
              <option key={t} value={t} disabled={t === away}>
                {t}
              </option>
            ))}
          </select>
          <h2 className="text-3xl sm:text-4xl font-heading font-bold text-[#E8EFE9] mt-4">
            {home}
          </h2>
          <div className="mut mt-1">
            Form {prediction.homeForm.join(' ')}
          </div>
        </div>

        {/* Center Match Display */}
        <div className="py-2">
          <div className="mut text-xs sm:text-sm font-medium">
            Matchweek 28 · Saturday 15:00
          </div>
          <div
            className={`text-6xl sm:text-7xl font-heading font-bold text-[#C6F432] my-2 tracking-tight transition-opacity ${
              loading ? 'opacity-50' : 'opacity-100'
            }`}
          >
            {prediction.predictedScore}
          </div>
          <div className="mut text-xs sm:text-sm">
            Predicted scoreline · xG {prediction.xGHome} – {prediction.xGAway}
          </div>

          <button
            onClick={swapTeams}
            title="Swap Home/Away"
            className="mt-3 inline-flex items-center gap-1.5 text-xs text-[#9DB0A5] hover:text-[#C6F432] transition-colors py-1 px-3 rounded-full border border-[#26352D] hover:border-[#3E5348]"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            <span>Swap Venue</span>
          </button>
        </div>

        {/* Away Team */}
        <div>
          <label className="mut uppercase tracking-wider font-semibold block text-xs" htmlFor="a">
            Away Team
          </label>
          <select
            id="a"
            value={away}
            onChange={handleAwayChange}
            className="custom-select w-full mt-2 font-medium"
          >
            {TEAM_NAMES.map(t => (
              <option key={t} value={t} disabled={t === home}>
                {t}
              </option>
            ))}
          </select>
          <h2 className="text-3xl sm:text-4xl font-heading font-bold text-[#E8EFE9] mt-4">
            {away}
          </h2>
          <div className="mut mt-1">
            Form {prediction.awayForm.join(' ')}
          </div>
        </div>
      </section>

      {/* Outcome Probabilities Card */}
      <section className="card">
        <h3 className="text-xl font-heading font-bold text-[#E8EFE9] mb-5">
          Outcome probabilities
        </h3>

        {/* Segmented Bar */}
        <div className="flex gap-1.5 overflow-hidden">
          <div
            className="bar bg-[#C6F432]"
            style={{ width: `${prediction.probs.Home}%` }}
            title={`${home} win: ${prediction.probs.Home}%`}
          />
          <div
            className="bar bg-[#3E5348]"
            style={{ width: `${prediction.probs.Draw}%` }}
            title={`Draw: ${prediction.probs.Draw}%`}
          />
          <div
            className="bar bg-[#8FA8FF]"
            style={{ width: `${prediction.probs.Away}%` }}
            title={`${away} win: ${prediction.probs.Away}%`}
          />
        </div>

        {/* Probabilities Legend */}
        <div className="flex justify-between items-center mt-3 text-sm sm:text-base flex-wrap gap-2">
          <span>
            <b className="text-[#C6F432] font-mono text-lg">{prediction.probs.Home}%</b>{' '}
            <span className="text-[#E8EFE9]">{home} win</span>
          </span>
          <span>
            <b className="text-[#E8EFE9] font-mono text-lg">{prediction.probs.Draw}%</b>{' '}
            <span className="text-[#9DB0A5]">Draw</span>
          </span>
          <span>
            <b className="text-[#8FA8FF] font-mono text-lg">{prediction.probs.Away}%</b>{' '}
            <span className="text-[#E8EFE9]">{away} win</span>
          </span>
        </div>
      </section>

      {/* 2-Column Section: SHAP Drivers & Recent Form/Ensemble */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Driving Factors (SHAP) Card */}
        <section className="card flex flex-col justify-between">
          <div>
            <h3 className="text-xl font-heading font-bold text-[#E8EFE9]">
              What drives this prediction
            </h3>
            <p className="mut mt-1 mb-4">
              SHAP impact on {home} win probability
            </p>

            <div className="space-y-1">
              {prediction.shapFactors.map((factor) => {
                const isHomePush = factor.direction === 'home';
                return (
                  <div key={factor.name} className="row-item">
                    <span className="text-[#E8EFE9]">{factor.name}</span>
                    <div className="w-full flex justify-end">
                      <div
                        className={`bar ${isHomePush ? 'bg-[#C6F432]' : 'bg-[#8FA8FF]'}`}
                        style={{ width: `${factor.impact}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <p className="mut mt-6 pt-3 border-t border-[#26352D] text-xs">
            Lime pushes toward the home side, blue toward the away side.
          </p>
        </section>

        {/* Recent Form & Model Ensemble Card */}
        <section className="card">
          <h3 className="text-xl font-heading font-bold text-[#E8EFE9] mb-4">
            Recent form
          </h3>

          <div className="space-y-3">
            {/* Home Form */}
            <div className="flex items-center gap-2">
              <span className="w-24 text-sm font-medium text-[#E8EFE9] truncate">
                {home}
              </span>
              <div className="flex gap-1.5">
                {prediction.homeForm.map((result, i) => (
                  <span
                    key={i}
                    className={`chip ${
                      result === 'W'
                        ? 'bg-[#C6F432] text-[#0E1512]'
                        : result === 'D'
                        ? 'bg-[#3E5348] text-[#E8EFE9]'
                        : 'bg-[#8FA8FF] text-[#0E1512]'
                    }`}
                  >
                    {result}
                  </span>
                ))}
              </div>
            </div>

            {/* Away Form */}
            <div className="flex items-center gap-2">
              <span className="w-24 text-sm font-medium text-[#E8EFE9] truncate">
                {away}
              </span>
              <div className="flex gap-1.5">
                {prediction.awayForm.map((result, i) => (
                  <span
                    key={i}
                    className={`chip ${
                      result === 'W'
                        ? 'bg-[#C6F432] text-[#0E1512]'
                        : result === 'D'
                        ? 'bg-[#3E5348] text-[#E8EFE9]'
                        : 'bg-[#8FA8FF] text-[#0E1512]'
                    }`}
                  >
                    {result}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Model Ensemble */}
          <h3 className="text-xl font-heading font-bold text-[#E8EFE9] mt-8 mb-3">
            Model ensemble
          </h3>

          <div>
            {prediction.ensemble.map(model => (
              <div key={model.name} className="row-item">
                <span className="text-[#E8EFE9]">{model.name}</span>
                <span className="mut text-right font-mono">weight {model.weight}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <p className="mut text-center text-xs">
        Statistical analytics & probabilistic machine learning calibrated for Premier League matchweeks.
      </p>
    </div>
  );
}
