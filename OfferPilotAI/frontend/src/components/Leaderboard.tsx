import { Flame, Trophy } from "lucide-react";

import type { LeaderboardEntry } from "../app/types";

type LeaderboardProps = {
  entries: LeaderboardEntry[];
};

export function Leaderboard({ entries }: LeaderboardProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Leaderboard</h2>
          <span>Weekly score</span>
        </div>
        <Trophy size={20} />
      </div>
      <div className="leaderboard-list">
        {entries.map((entry) => (
          <div className={`leaderboard-row ${entry.currentUser ? "current-user" : ""}`} key={entry.rank}>
            <span className="rank">{entry.rank}</span>
            <strong>{entry.name}</strong>
            <span className="streak">
              <Flame size={15} />
              {entry.streak}
            </span>
            <b>{entry.score}</b>
          </div>
        ))}
      </div>
    </section>
  );
}
