import { BookOpenCheck } from "lucide-react";

import type { LearningItem } from "../app/types";

type LearningProgressProps = {
  items: LearningItem[];
};

export function LearningProgress({ items }: LearningProgressProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Learning Progress</h2>
          <span>Roadmap completion</span>
        </div>
        <BookOpenCheck size={20} />
      </div>
      <div className="progress-list">
        {items.map((item) => (
          <div className="progress-item" key={item.title}>
            <div className="progress-copy">
              <strong>{item.title}</strong>
              <span>{item.detail}</span>
            </div>
            <div className="progress-track" aria-label={`${item.title} ${item.progress}% complete`}>
              <div style={{ width: `${item.progress}%` }} />
            </div>
            <b>{item.progress}%</b>
          </div>
        ))}
      </div>
    </section>
  );
}
