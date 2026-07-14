import {
  AlertTriangle,
  CheckCircle2,
  FileSearch,
  FileText,
  Loader2,
  MessageSquareText,
  Target,
  UploadCloud,
} from "lucide-react";
import { useMemo, useRef, useState } from "react";

import { analyzeResumePdf } from "../../services/resumeAnalyzerApi";
import { sampleJobDescription, sampleResumeAnalysis } from "./resumeAnalyzerData";
import type { ResumeAnalysis } from "./types";

export function ResumeAnalyzerWorkspace() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState(sampleJobDescription);
  const [analysis, setAnalysis] = useState<ResumeAnalysis>(sampleResumeAnalysis);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const atsScore = Number(analysis.ats_score);
  const circumference = 2 * Math.PI * 44;
  const scoreOffset = circumference - (Math.min(100, Math.max(0, atsScore)) / 100) * circumference;

  const priorityGaps = useMemo(
    () => analysis.missing_skills.filter((skill) => skill.priority === "high" || skill.priority === "medium").slice(0, 5),
    [analysis.missing_skills],
  );

  const handleFile = (file: File | undefined) => {
    if (!file) {
      return;
    }
    setErrorMessage("");
    setSelectedFile(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setErrorMessage("Choose a resume PDF before running analysis.");
      return;
    }
    setIsAnalyzing(true);
    setErrorMessage("");
    try {
      setAnalysis(await analyzeResumePdf(selectedFile, jobDescription));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Resume analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <section className="resume-workspace" aria-label="Resume analyzer">
      <div className="module-heading">
        <div>
          <p className="eyebrow">Resume Analyzer</p>
          <h2>Upload, compare, score, and prepare</h2>
        </div>
        <button className="primary-action" disabled={isAnalyzing} onClick={handleAnalyze} type="button">
          {isAnalyzing ? <Loader2 className="spin" size={17} /> : <FileSearch size={17} />}
          Analyze Resume
        </button>
      </div>

      <div className="resume-grid">
        <section className="resume-input-panel">
          <button
            className="upload-zone"
            onClick={() => inputRef.current?.click()}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              handleFile(event.dataTransfer.files.item(0) ?? undefined);
            }}
            type="button"
          >
            <UploadCloud size={32} />
            <strong>{selectedFile ? selectedFile.name : "Upload Resume PDF"}</strong>
            <span>{selectedFile ? `${Math.round(selectedFile.size / 1024)} KB selected` : "Drag and drop or browse"}</span>
          </button>
          <input
            accept="application/pdf,.pdf"
            hidden
            onChange={(event) => handleFile(event.target.files?.item(0) ?? undefined)}
            ref={inputRef}
            type="file"
          />

          <label className="job-description-box">
            <span>Job Description</span>
            <textarea onChange={(event) => setJobDescription(event.target.value)} value={jobDescription} />
          </label>

          {errorMessage && (
            <div className="resume-error">
              <AlertTriangle size={17} />
              <span>{errorMessage}</span>
            </div>
          )}
        </section>

        <section className="panel ats-panel">
          <div className="panel-heading">
            <div>
              <h2>ATS Score</h2>
              <span>{analysis.filename}</span>
            </div>
            <Target size={20} />
          </div>
          <div className="ats-score-wrap">
            <svg viewBox="0 0 110 110" aria-label={`ATS score ${analysis.ats_score}`}>
              <circle className="score-track" cx="55" cy="55" r="44" />
              <circle
                className="score-value"
                cx="55"
                cy="55"
                r="44"
                strokeDasharray={circumference}
                strokeDashoffset={scoreOffset}
              />
            </svg>
            <div>
              <strong>{analysis.ats_score}</strong>
              <span>out of 100</span>
            </div>
          </div>
          <p>{analysis.analysis_summary}</p>
        </section>
      </div>

      <div className="resume-results-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Analyzed Skills</h2>
              <span>{analysis.extracted_skills.length} detected</span>
            </div>
            <CheckCircle2 size={20} />
          </div>
          <div className="skill-chip-list">
            {analysis.extracted_skills.map((skill) => (
              <span className="skill-chip" key={`${skill.category}-${skill.name}`}>
                {skill.name}
                <b>{skill.category}</b>
              </span>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Missing Skills</h2>
              <span>{analysis.missing_skills.length} gaps</span>
            </div>
            <AlertTriangle size={20} />
          </div>
          <div className="gap-list">
            {priorityGaps.map((skill) => (
              <div className={`gap-row gap-${skill.priority}`} key={skill.name}>
                <strong>{skill.name}</strong>
                <span>{skill.reason}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Skill Gap Report</h2>
              <span>{analysis.skill_gap_report.match_rate}% match</span>
            </div>
            <FileText size={20} />
          </div>
          <p className="report-summary">{analysis.skill_gap_report.summary}</p>
          <div className="focus-list">
            {analysis.skill_gap_report.recommended_focus.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </section>
      </div>

      <div className="resume-lower-grid">
        <section className="panel">
          <div className="panel-heading">
            <h2>Resume Suggestions</h2>
            <span className="pill">Actionable</span>
          </div>
          <div className="suggestion-list">
            {analysis.resume_suggestions.map((suggestion) => (
              <div className="suggestion-row" key={suggestion}>
                <CheckCircle2 size={16} />
                <span>{suggestion}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Resume-Based Questions</h2>
            <MessageSquareText size={20} />
          </div>
          <div className="resume-question-list">
            {analysis.interview_questions.map((question) => (
              <div className="resume-question-row" key={question.question}>
                <strong>{question.question}</strong>
                <span>
                  {question.category} · {question.difficulty} · {question.signal}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
