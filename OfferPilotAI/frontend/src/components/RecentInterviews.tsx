import { CheckCircle2, Clock3, TriangleAlert } from "lucide-react";

import type { InterviewRecord } from "../app/types";

type RecentInterviewsProps = {
  interviews: InterviewRecord[];
};

const statusIcon = {
  Completed: CheckCircle2,
  "Needs Review": TriangleAlert,
  "In Progress": Clock3,
};

export function RecentInterviews({ interviews }: RecentInterviewsProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Recent Interviews</h2>
        <span className="pill">Live</span>
      </div>
      <div className="interview-list">
        {interviews.map((interview) => {
          const Icon = statusIcon[interview.status];
          return (
            <div className="interview-row" key={interview.id}>
              <div className="status-icon">
                <Icon size={18} />
              </div>
              <div className="interview-main">
                <strong>{interview.role}</strong>
                <span>
                  {interview.type} · {interview.date}
                </span>
              </div>
              <b>{interview.score}</b>
            </div>
          );
        })}
      </div>
    </section>
  );
}
