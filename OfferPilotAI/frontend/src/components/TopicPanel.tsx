import type { TopicScore } from "../app/types";

type TopicPanelProps = {
  title: string;
  topics: TopicScore[];
  tone: "weak" | "strong";
};

export function TopicPanel({ title, topics, tone }: TopicPanelProps) {
  return (
    <section className="panel topic-panel">
      <div className="panel-heading">
        <h2>{title}</h2>
        <span className={`pill pill-${tone}`}>{tone === "weak" ? "Focus" : "Lead"}</span>
      </div>
      <div className="topic-list">
        {topics.map((topic) => (
          <div className="topic-row" key={topic.topic}>
            <div>
              <strong>{topic.topic}</strong>
              <span>{topic.category}</span>
            </div>
            <div className="topic-meter" aria-label={`${topic.topic} score ${topic.score}`}>
              <div style={{ width: `${topic.score}%` }} />
            </div>
            <b>{topic.score}</b>
          </div>
        ))}
      </div>
    </section>
  );
}
