import { java } from "@codemirror/lang-java";
import { python } from "@codemirror/lang-python";
import { sql } from "@codemirror/lang-sql";
import type { Extension } from "@codemirror/state";
import { oneDark } from "@codemirror/theme-one-dark";
import CodeMirror from "@uiw/react-codemirror";
import {
  Bug,
  CheckCircle2,
  Clock3,
  Code2,
  FileCode2,
  Loader2,
  Play,
  Save,
  ScanSearch,
  Terminal,
  Zap,
} from "lucide-react";
import { useMemo, useState } from "react";

import { analyzeCode, runCode, submitCode } from "../../services/liveCodingApi";
import { codeTemplates, initialAnalysis, initialRunResult, sampleSubmissions } from "./liveCodingData";
import type { CodeAnalysisResult, CodeRunResult, CodeSubmission, CodingLanguage } from "./types";

type LiveCodingWorkspaceProps = {
  theme: "dark" | "light";
};

const languageExtensions: Record<CodingLanguage, () => Extension> = {
  python,
  java,
  sql,
};

const languageOrder: CodingLanguage[] = ["python", "java", "sql"];

export function LiveCodingWorkspace({ theme }: LiveCodingWorkspaceProps) {
  const [language, setLanguage] = useState<CodingLanguage>("python");
  const [sourceCode, setSourceCode] = useState(codeTemplates.python.sourceCode);
  const [stdin, setStdin] = useState(codeTemplates.python.stdin);
  const [expectedOutput, setExpectedOutput] = useState(codeTemplates.python.expectedOutput);
  const [promptTitle, setPromptTitle] = useState(codeTemplates.python.promptTitle);
  const [prompt, setPrompt] = useState(codeTemplates.python.prompt);
  const [runResult, setRunResult] = useState<CodeRunResult>(initialRunResult);
  const [analysis, setAnalysis] = useState<CodeAnalysisResult>(initialAnalysis);
  const [submissions, setSubmissions] = useState<CodeSubmission[]>(sampleSubmissions);
  const [isRunning, setIsRunning] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const editorExtensions = useMemo(() => [languageExtensions[language]()], [language]);
  const editorTheme = theme === "dark" ? oneDark : undefined;

  const selectLanguage = (nextLanguage: CodingLanguage) => {
    const template = codeTemplates[nextLanguage];
    setLanguage(nextLanguage);
    setSourceCode(template.sourceCode);
    setStdin(template.stdin);
    setExpectedOutput(template.expectedOutput);
    setPromptTitle(template.promptTitle);
    setPrompt(template.prompt);
    setRunResult({ ...initialRunResult, language: nextLanguage });
    setAnalysis({ ...initialAnalysis, language: nextLanguage, observations: [`Editor initialized with ${template.label}.`] });
  };

  const handleRun = async () => {
    setIsRunning(true);
    try {
      setRunResult(
        await runCode({
          language,
          source_code: sourceCode,
          stdin,
          expected_output: expectedOutput || undefined,
          timeout_seconds: 3,
        }),
      );
    } catch (error) {
      setRunResult({
        language,
        status: "failed",
        stdout: "",
        stderr: error instanceof Error ? error.message : "Code execution failed.",
        exit_code: null,
        execution_time_ms: null,
        memory_kb: null,
        passed: null,
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      setAnalysis(
        await analyzeCode({
          language,
          source_code: sourceCode,
          prompt,
        }),
      );
    } catch (error) {
      setAnalysis({
        ...initialAnalysis,
        language,
        bugs: [
          {
            severity: "warning",
            message: error instanceof Error ? error.message : "Analysis failed.",
            line: null,
            rule: "frontend.request",
          },
        ],
        improvement_explanation: "Analysis could not be completed. Check API connectivity and authentication.",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const submission = await submitCode({
        language,
        source_code: sourceCode,
        stdin,
        expected_output: expectedOutput || undefined,
        timeout_seconds: 3,
        prompt_title: promptTitle,
        prompt,
        run_code: true,
        metadata: { source: "frontend-live-coding" },
      });
      setSubmissions((current) => [submission, ...current].slice(0, 6));
    } catch (error) {
      setRunResult({
        language,
        status: "failed",
        stdout: "",
        stderr: error instanceof Error ? error.message : "Submission failed.",
        exit_code: null,
        execution_time_ms: null,
        memory_kb: null,
        passed: null,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="coding-workspace" aria-label="Live coding module">
      <div className="module-heading">
        <div>
          <p className="eyebrow">Live Coding Module</p>
          <h2>Run, analyze, optimize, and store submissions</h2>
        </div>
        <div className="language-tabs" aria-label="Language selector">
          {languageOrder.map((item) => (
            <button
              className={item === language ? "active" : ""}
              key={item}
              onClick={() => selectLanguage(item)}
              type="button"
            >
              {codeTemplates[item].label}
            </button>
          ))}
        </div>
      </div>

      <div className="coding-shell">
        <div className="coding-editor-panel">
          <div className="challenge-strip">
            <div>
              <span>Current Challenge</span>
              <strong>{promptTitle}</strong>
            </div>
            <Code2 size={22} />
          </div>

          <textarea
            aria-label="Coding prompt"
            className="prompt-input"
            onChange={(event) => setPrompt(event.target.value)}
            value={prompt}
          />

          <div className="editor-toolbar">
            <span>
              <FileCode2 size={16} />
              {codeTemplates[language].label}
            </span>
            <div className="action-bar">
              <button className="secondary-action" disabled={isAnalyzing} onClick={handleAnalyze} type="button">
                {isAnalyzing ? <Loader2 className="spin" size={17} /> : <ScanSearch size={17} />}
                Analyze
              </button>
              <button className="secondary-action" disabled={isSubmitting} onClick={handleSubmit} type="button">
                {isSubmitting ? <Loader2 className="spin" size={17} /> : <Save size={17} />}
                Submit
              </button>
              <button className="primary-action" disabled={isRunning} onClick={handleRun} type="button">
                {isRunning ? <Loader2 className="spin" size={17} /> : <Play size={17} />}
                Run
              </button>
            </div>
          </div>

          <div className="editor-frame">
            <CodeMirror
              basicSetup={{
                autocompletion: true,
                bracketMatching: true,
                foldGutter: true,
                highlightActiveLine: true,
                lineNumbers: true,
              }}
              extensions={editorExtensions}
              height="430px"
              onChange={setSourceCode}
              theme={editorTheme}
              value={sourceCode}
            />
          </div>

          <div className="io-grid">
            <label>
              <span>Standard Input</span>
              <textarea onChange={(event) => setStdin(event.target.value)} value={stdin} />
            </label>
            <label>
              <span>Expected Output</span>
              <textarea onChange={(event) => setExpectedOutput(event.target.value)} value={expectedOutput} />
            </label>
          </div>
        </div>

        <aside className="coding-side-panel">
          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Run Output</h2>
                <span>{runResult.execution_time_ms ? `${runResult.execution_time_ms} ms` : "Ready"}</span>
              </div>
              <Terminal size={20} />
            </div>
            <div className={`status-banner status-${runResult.status}`}>
              {runResult.status === "success" ? <CheckCircle2 size={17} /> : <Clock3 size={17} />}
              <strong>{runResult.status}</strong>
              {runResult.passed !== null && <span>{runResult.passed ? "Expected output matched" : "Output mismatch"}</span>}
            </div>
            <pre className="result-terminal">{runResult.stderr || runResult.stdout}</pre>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Code Analysis</h2>
                <span>Complexity and quality</span>
              </div>
              <Zap size={20} />
            </div>
            <div className="analysis-grid">
              <div>
                <span>Time</span>
                <strong>{analysis.time_complexity}</strong>
              </div>
              <div>
                <span>Space</span>
                <strong>{analysis.space_complexity}</strong>
              </div>
              <div>
                <span>Score</span>
                <strong>{analysis.quality_score}</strong>
              </div>
            </div>
            <div className="issue-list">
              {analysis.bugs.length ? (
                analysis.bugs.map((issue) => (
                  <div className={`issue-row issue-${issue.severity}`} key={`${issue.rule}-${issue.message}`}>
                    <Bug size={16} />
                    <span>{issue.message}</span>
                  </div>
                ))
              ) : (
                <div className="issue-row">
                  <CheckCircle2 size={16} />
                  <span>No bugs detected yet.</span>
                </div>
              )}
            </div>
          </section>

          <section className="panel optimized-panel">
            <div className="panel-heading">
              <h2>Optimized Code</h2>
              <span className="pill">Generated</span>
            </div>
            <p>{analysis.improvement_explanation}</p>
            <pre>{analysis.optimized_code}</pre>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <h2>Submissions</h2>
              <span className="pill">Stored</span>
            </div>
            <div className="submission-list">
              {submissions.map((submission) => (
                <div className="submission-row" key={submission.id}>
                  <div>
                    <strong>{submission.prompt_title}</strong>
                    <span>
                      {submission.language.toUpperCase()} · {submission.time_complexity} · {submission.submitted_at}
                    </span>
                  </div>
                  <b>{submission.status}</b>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </section>
  );
}
