"""Resume analyzer providers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re

from app.schemas.resume import (
    MissingSkill,
    ResumeAnalysisPayload,
    ResumeInterviewQuestion,
    ResumeSkill,
    SkillGapReport,
)


@dataclass(frozen=True)
class ResumeAnalyzerInput:
    """Resume analyzer input."""

    resume_text: str
    job_description: str | None
    filename: str


class ResumeAnalyzerProvider:
    """Resume analyzer provider interface."""

    analyzer_version = "provider-interface"

    async def analyze(self, payload: ResumeAnalyzerInput) -> ResumeAnalysisPayload:
        raise NotImplementedError


class HeuristicResumeAnalyzerProvider(ResumeAnalyzerProvider):
    """Deterministic resume analyzer with a provider boundary for future AI integration."""

    analyzer_version = "heuristic-resume-analyzer-v1"

    skill_taxonomy: dict[str, tuple[str, tuple[str, ...]]] = {
        "Python": ("Programming", ("python", "fastapi", "django", "flask", "pandas", "numpy")),
        "Java": ("Programming", ("java", "spring", "spring boot", "jvm")),
        "SQL": ("Data", ("sql", "postgresql", "mysql", "query", "joins", "indexing")),
        "JavaScript": ("Frontend", ("javascript", "typescript", "react", "node.js", "nodejs")),
        "React": ("Frontend", ("react", "redux", "vite", "next.js", "nextjs")),
        "System Design": ("Architecture", ("system design", "scalability", "distributed", "microservices")),
        "AWS": ("Cloud", ("aws", "ec2", "lambda", "s3", "cloudwatch")),
        "Azure": ("Cloud", ("azure", "aks", "functions", "cosmos")),
        "Docker": ("DevOps", ("docker", "container", "containers")),
        "Kubernetes": ("DevOps", ("kubernetes", "k8s", "helm")),
        "CI/CD": ("DevOps", ("ci/cd", "github actions", "jenkins", "gitlab ci")),
        "Machine Learning": ("AI/ML", ("machine learning", "ml", "scikit", "xgboost", "model training")),
        "Deep Learning": ("AI/ML", ("deep learning", "pytorch", "tensorflow", "neural", "transformer")),
        "NLP": ("AI/ML", ("nlp", "language model", "embedding", "tokenization")),
        "Testing": ("Quality", ("pytest", "junit", "unit test", "integration test", "test automation")),
        "Observability": ("Operations", ("monitoring", "logging", "tracing", "observability", "prometheus")),
        "Leadership": ("Leadership", ("leadership", "mentored", "stakeholder", "cross-functional", "roadmap")),
        "Communication": ("Soft Skills", ("communication", "collaboration", "presentation", "documentation")),
        "Agile": ("Delivery", ("agile", "scrum", "kanban", "sprint")),
        "Security": ("Security", ("security", "oauth", "jwt", "encryption", "owasp")),
    }

    async def analyze(self, payload: ResumeAnalyzerInput) -> ResumeAnalysisPayload:
        resume_skills = self._extract_skills(payload.resume_text)
        jd_skills = self._extract_skills(payload.job_description or "")
        matched = self._matched_skills(resume_skills, jd_skills)
        missing = self._missing_skills(resume_skills, jd_skills)
        ats_score = self._ats_score(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            missing=missing,
        )
        suggestions = self._suggestions(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            resume_skills=resume_skills,
            missing=missing,
        )
        gap_report = self._gap_report(resume_skills=resume_skills, jd_skills=jd_skills, missing=missing)

        return ResumeAnalysisPayload(
            extracted_skills=resume_skills,
            matched_skills=matched,
            missing_skills=missing,
            ats_score=ats_score,
            resume_suggestions=suggestions,
            interview_questions=self._interview_questions(resume_skills=resume_skills, missing=missing),
            skill_gap_report=gap_report,
            analysis_summary=self._summary(ats_score=ats_score, matched=matched, missing=missing),
            analyzer_version=self.analyzer_version,
        )

    def _extract_skills(self, text: str) -> list[ResumeSkill]:
        normalized = self._normalize(text)
        skills: list[ResumeSkill] = []
        for canonical, (category, aliases) in self.skill_taxonomy.items():
            count = sum(len(re.findall(rf"\b{re.escape(alias.lower())}\b", normalized)) for alias in aliases)
            if count:
                confidence = min(Decimal("100"), Decimal("58") + Decimal(count * 12))
                skills.append(
                    ResumeSkill(
                        name=canonical,
                        category=category,
                        evidence_count=count,
                        confidence=confidence.quantize(Decimal("0.01")),
                    )
                )
        skills.sort(key=lambda skill: (skill.category, skill.name))
        return skills

    def _matched_skills(self, resume_skills: list[ResumeSkill], jd_skills: list[ResumeSkill]) -> list[ResumeSkill]:
        if not jd_skills:
            return resume_skills
        resume_names = {skill.name for skill in resume_skills}
        return [skill for skill in jd_skills if skill.name in resume_names]

    def _missing_skills(self, resume_skills: list[ResumeSkill], jd_skills: list[ResumeSkill]) -> list[MissingSkill]:
        if not jd_skills:
            return []
        resume_names = {skill.name for skill in resume_skills}
        missing: list[MissingSkill] = []
        for skill in jd_skills:
            if skill.name in resume_names:
                continue
            priority = "high" if skill.evidence_count >= 2 or skill.category in {"Programming", "Architecture", "Cloud"} else "medium"
            missing.append(
                MissingSkill(
                    name=skill.name,
                    category=skill.category,
                    priority=priority,
                    reason=f"The job description emphasizes {skill.name}, but the resume does not show a clear match.",
                )
            )
        return missing

    def _ats_score(
        self,
        *,
        resume_text: str,
        job_description: str | None,
        resume_skills: list[ResumeSkill],
        jd_skills: list[ResumeSkill],
        missing: list[MissingSkill],
    ) -> Decimal:
        score = Decimal("42")
        score += Decimal(min(len(resume_skills), 12)) * Decimal("2.2")
        score += self._section_score(resume_text)
        score += self._impact_score(resume_text)
        if jd_skills:
            matched_count = len(jd_skills) - len(missing)
            score += Decimal("28") * Decimal(matched_count) / Decimal(max(len(jd_skills), 1))
            score -= Decimal(len([skill for skill in missing if skill.priority == "high"])) * Decimal("3")
        elif job_description:
            score += Decimal("6")
        bounded = max(Decimal("0"), min(Decimal("100"), score))
        return bounded.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _section_score(self, resume_text: str) -> Decimal:
        normalized = self._normalize(resume_text)
        sections = ["experience", "skills", "education", "projects", "summary"]
        return Decimal(sum(1 for section in sections if section in normalized)) * Decimal("2.5")

    def _impact_score(self, resume_text: str) -> Decimal:
        metric_hits = len(re.findall(r"(\d+%|\$\d+|\b\d+x\b|\b\d+\+\b)", resume_text.lower()))
        action_hits = sum(
            1
            for word in ["built", "led", "owned", "improved", "reduced", "launched", "designed", "automated"]
            if word in resume_text.lower()
        )
        return Decimal(min(metric_hits * 2 + action_hits, 14))

    def _suggestions(
        self,
        *,
        resume_text: str,
        job_description: str | None,
        resume_skills: list[ResumeSkill],
        missing: list[MissingSkill],
    ) -> list[str]:
        suggestions: list[str] = []
        normalized = self._normalize(resume_text)
        if missing:
            high_priority = [skill.name for skill in missing if skill.priority == "high"][:3]
            if high_priority:
                suggestions.append(f"Add evidence for high-priority job skills: {', '.join(high_priority)}.")
        if len(re.findall(r"(\d+%|\$\d+|\b\d+x\b|\b\d+\+\b)", resume_text.lower())) < 3:
            suggestions.append("Quantify impact with metrics such as latency reduction, revenue, scale, or accuracy gains.")
        if "summary" not in normalized:
            suggestions.append("Add a concise professional summary aligned to the target role.")
        if "skills" not in normalized:
            suggestions.append("Add a dedicated skills section using exact job-description keywords.")
        if job_description and not missing:
            suggestions.append("The resume aligns well; tune bullet wording to mirror the job description more closely.")
        if len(resume_skills) < 5:
            suggestions.append("Surface more technical skills and tools explicitly instead of only describing responsibilities.")
        if not suggestions:
            suggestions.append("Tighten the strongest bullets with measurable outcomes and clearer ownership language.")
        return suggestions

    def _interview_questions(
        self,
        *,
        resume_skills: list[ResumeSkill],
        missing: list[MissingSkill],
    ) -> list[ResumeInterviewQuestion]:
        questions: list[ResumeInterviewQuestion] = []
        for skill in resume_skills[:5]:
            questions.append(
                ResumeInterviewQuestion(
                    question=f"Walk me through a project where you used {skill.name}. What tradeoffs did you make?",
                    category=skill.category,
                    difficulty="medium",
                    signal="evidence_depth",
                )
            )
        for gap in missing[:4]:
            questions.append(
                ResumeInterviewQuestion(
                    question=f"The role mentions {gap.name}. How would you ramp up and apply it in the first 30 days?",
                    category=gap.category,
                    difficulty="hard" if gap.priority == "high" else "medium",
                    signal="skill_gap_reasoning",
                )
            )
        if not questions:
            questions.append(
                ResumeInterviewQuestion(
                    question="Tell me about the most technically challenging project on your resume.",
                    category="General",
                    difficulty="medium",
                    signal="resume_depth",
                )
            )
        return questions[:10]

    def _gap_report(
        self,
        *,
        resume_skills: list[ResumeSkill],
        jd_skills: list[ResumeSkill],
        missing: list[MissingSkill],
    ) -> SkillGapReport:
        jd_names = {skill.name for skill in jd_skills}
        matched_count = len([skill for skill in resume_skills if not jd_names or skill.name in jd_names])
        denominator = len(jd_skills) if jd_skills else max(len(resume_skills), 1)
        match_rate = (Decimal(matched_count) * Decimal("100") / Decimal(max(denominator, 1))).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        category_counts = Counter(skill.category for skill in resume_skills)
        missing_counts = Counter(skill.category for skill in missing)
        strongest = [category for category, _ in category_counts.most_common(3)]
        weakest = [category for category, _ in missing_counts.most_common(3)]
        recommended_focus = [skill.name for skill in missing if skill.priority == "high"][:5]
        if not recommended_focus:
            recommended_focus = [skill.name for skill in missing[:5]]
        return SkillGapReport(
            match_rate=min(Decimal("100"), match_rate),
            strongest_categories=strongest,
            weakest_categories=weakest,
            priority_gaps=missing[:5],
            recommended_focus=recommended_focus,
            summary=self._gap_summary(match_rate=match_rate, missing=missing),
        )

    def _summary(self, *, ats_score: Decimal, matched: list[ResumeSkill], missing: list[MissingSkill]) -> str:
        if missing:
            return (
                f"ATS score is {ats_score}. The resume matches {len(matched)} target skills and is missing "
                f"{len(missing)} job-description skills. Prioritize the high-impact gaps before applying."
            )
        return f"ATS score is {ats_score}. The resume has strong keyword alignment for the provided job description."

    def _gap_summary(self, *, match_rate: Decimal, missing: list[MissingSkill]) -> str:
        if not missing:
            return "No major skill gaps were detected against the provided job description."
        high_count = len([skill for skill in missing if skill.priority == "high"])
        return f"Skill match rate is {match_rate}%. {high_count} high-priority gaps should be addressed first."

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower())
