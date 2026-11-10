import React from 'react';
import { EPL_TEAMS } from '../data/eplData.js';

export default function SeasonView() {
  const sortedTeams = [...EPL_TEAMS].sort((a, b) => b.pts - a.pts);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Season Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="mut">Title Favorite</div>
          <div className="text-3xl font-heading font-bold text-[#C6F432] mt-2">
            {sortedTeams[0].name}
          </div>
          <div className="mut mt-1">
            Projected {sortedTeams[0].pts} pts · {sortedTeams[0].title}% Title Probability
          </div>
        </div>

        <div className="card">
          <div className="mut">UCL Cutoff (Top 4)</div>
          <div className="text-3xl font-heading font-bold text-[#8FA8FF] mt-2">
            ~67 Points
          </div>
          <div className="mut mt-1">
            Battle between {sortedTeams[3].name}, {sortedTeams[4].name}, & {sortedTeams[5].name}
          </div>
        </div>

        <div className="card">
          <div className="mut">Relegation Safety Line</div>
          <div className="text-3xl font-heading font-bold text-red-400 mt-2">
            ~35 Points
          </div>
          <div className="mut mt-1">
            Bottom 3: {sortedTeams[17].name}, {sortedTeams[18].name}, {sortedTeams[19].name}
          </div>
        </div>
      </div>

      {/* Main Table */}
      <div className="card overflow-x-auto p-0">
        <div className="p-6 pb-4 border-b border-[#26352D] flex justify-between items-center flex-wrap gap-4">
          <div>
            <h3 className="text-xl font-heading font-bold text-[#E8EFE9]">
              Monte Carlo Season Simulation Table
            </h3>
            <p className="mut mt-1">
              Simulated across 10,000 iterations incorporating squad ratings, fixture difficulty, and rolling form.
            </p>
          </div>
          <span className="text-xs px-3 py-1.5 rounded-full bg-[#16201B] border border-[#26352D] text-[#C6F432] font-mono">
            Matchweek 28 Projected
          </span>
        </div>

        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#121A16] text-[#9DB0A5] text-xs uppercase tracking-wider">
              <th className="py-3 px-4">Pos</th>
              <th className="py-3 px-4">Club</th>
              <th className="py-3 px-4 text-center">Proj Pts</th>
              <th className="py-3 px-4 text-center">Recent Form</th>
              <th className="py-3 px-4 text-center">Title %</th>
              <th className="py-3 px-4 text-center">Top 4 %</th>
              <th className="py-3 px-4 text-center">Relegation %</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#26352D] text-sm">
            {sortedTeams.map((team, idx) => {
              const pos = idx + 1;
              const isChamp = pos === 1;
              const isUCL = pos <= 4;
              const isRel = pos >= 18;

              return (
                <tr
                  key={team.name}
                  className={`hover:bg-[#1C2822] transition-colors ${
                    isChamp ? 'bg-[#C6F432]/5' : ''
                  }`}
                >
                  <td className="py-3.5 px-4 font-mono font-medium">
                    <span
                      className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                        isChamp
                          ? 'bg-[#C6F432] text-[#0E1512]'
                          : isUCL
                          ? 'bg-[#3E5348] text-[#E8EFE9]'
                          : isRel
                          ? 'bg-red-500/20 text-red-300'
                          : 'text-[#9DB0A5]'
                      }`}
                    >
                      {pos}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-heading font-medium text-[#E8EFE9] text-base">
                    {team.name}
                  </td>
                  <td className="py-3.5 px-4 text-center font-heading font-bold text-lg text-[#E8EFE9]">
                    {team.pts}
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex justify-center gap-1">
                      {team.form.map((res, i) => (
                        <span
                          key={i}
                          className={`w-5 h-5 rounded text-[10px] font-bold flex items-center justify-center ${
                            res === 'W'
                              ? 'bg-[#C6F432] text-[#0E1512]'
                              : res === 'D'
                              ? 'bg-[#3E5348] text-[#E8EFE9]'
                              : 'bg-[#8FA8FF] text-[#0E1512]'
                          }`}
                        >
                          {res}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-center font-mono">
                    {team.title > 0 ? (
                      <span className="text-[#C6F432] font-bold">{team.title}%</span>
                    ) : (
                      <span className="text-[#9DB0A5]">&lt;1%</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-center font-mono">
                    {team.top4 > 0 ? (
                      <span className={team.top4 > 50 ? 'text-[#8FA8FF] font-bold' : 'text-[#E8EFE9]'}>
                        {team.top4}%
                      </span>
                    ) : (
                      <span className="text-[#9DB0A5]">&lt;1%</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-center font-mono">
                    {team.rel > 0 ? (
                      <span className={team.rel > 40 ? 'text-red-400 font-bold' : 'text-[#9DB0A5]'}>
                        {team.rel}%
                      </span>
                    ) : (
                      <span className="text-[#9DB0A5]">0%</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
