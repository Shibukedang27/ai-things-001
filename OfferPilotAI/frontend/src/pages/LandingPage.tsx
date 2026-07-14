import type { LucideIcon } from "lucide-react";
import {
  ArrowRight,
  BadgeCheck,
  BarChart3,
  Brain,
  BriefcaseBusiness,
  Building2,
  Check,
  ChevronRight,
  Code2,
  FileSearch,
  GraduationCap,
  Moon,
  Play,
  ShieldCheck,
  Sparkles,
  Sun,
  Target,
  Trophy,
  Users,
} from "lucide-react";

type LandingPageProps = {
  theme: "dark" | "light";
  onToggleTheme: () => void;
  onOpenApp: () => void;
};

type Feature = {
  title: string;
  description: string;
  icon: LucideIcon;
};

const features: Feature[] = [
  {
    title: "Adaptive Interview Engine",
    description: "Role, seniority, duration, and topic-aware mock interviews that progress one answer at a time.",
    icon: Brain,
  },
  {
    title: "AI Evaluation",
    description: "Structured scoring across accuracy, communication, completeness, confidence, and problem solving.",
    icon: BadgeCheck,
  },
  {
    title: "Resume Intelligence",
    description: "Resume analysis, ATS scoring, missing skills, job description matching, and interview prompts.",
    icon: FileSearch,
  },
  {
    title: "Live Coding Studio",
    description: "Python, Java, and SQL practice with execution, bug detection, complexity analysis, and optimization.",
    icon: Code2,
  },
  {
    title: "Learning Roadmaps",
    description: "Daily, weekly, and monthly plans generated from weak topics and interview history.",
    icon: Target,
  },
  {
    title: "Readiness Analytics",
    description: "Topic accuracy, heat maps, radar charts, trend lines, streaks, and leaderboards for teams.",
    icon: BarChart3,
  },
];

const steps = [
  ["01", "Map the role", "Select the target role, interview style, seniority, duration, and categories."],
  ["02", "Practice with signal", "Run structured interviews, coding drills, and resume-based question sets."],
  ["03", "Score the response", "Convert answers into clear strengths, weak topics, model answers, and next actions."],
  ["04", "Improve weekly", "Follow a personalized roadmap with resources, practice plans, and progress analytics."],
];

const testimonials = [
  {
    quote: "OfferPilot AI turned vague prep into measurable readiness. Our cohort finally knew what to practice next.",
    name: "Maya R.",
    role: "Career Accelerator Lead",
  },
  {
    quote: "The feedback quality feels like a senior interviewer who also remembers every previous session.",
    name: "Daniel K.",
    role: "Backend Engineering Candidate",
  },
  {
    quote: "We use it to standardize coaching plans before candidates reach final-round interviews.",
    name: "Priya S.",
    role: "Recruiting Operations Manager",
  },
];

const supportedCompanies = [
  ["Startups", BriefcaseBusiness],
  ["Enterprise Teams", Building2],
  ["Bootcamps", GraduationCap],
  ["Universities", GraduationCap],
  ["Recruiting Agencies", Users],
  ["Career Coaches", Trophy],
] satisfies Array<[string, LucideIcon]>;

const pricing = [
  {
    name: "Free",
    price: "$0",
    description: "For candidates testing interview readiness.",
    items: ["Limited mock interviews", "Basic dashboard", "Sample resume scan", "Community-ready practice"],
  },
  {
    name: "Pro",
    price: "$19",
    description: "For serious candidates preparing for offer loops.",
    items: ["Unlimited practice", "Full answer evaluation", "Resume analyzer", "Live coding and roadmaps"],
    featured: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For teams, bootcamps, and talent organizations.",
    items: ["Cohort analytics", "Admin reporting", "Custom rubrics", "SSO and support"],
  },
];

const faqs = [
  ["Who is OfferPilot AI for?", "Candidates, coaching companies, universities, bootcamps, recruiters, and internal talent teams."],
  ["Does it replace human interview coaching?", "No. It makes practice measurable and helps coaches focus on the highest-impact gaps."],
  ["Which domains are supported?", "Python, Java, SQL, DSA, system design, ML, deep learning, NLP, prompt engineering, behavioral, and HR."],
  ["Can teams use it commercially?", "Yes. The architecture is prepared for team plans, enterprise dashboards, and API-based integrations."],
];

export function LandingPage({ theme, onToggleTheme, onOpenApp }: LandingPageProps) {
  return (
    <main className="landing-page">
      <header className="landing-nav">
        <a className="landing-brand" href="#top" aria-label="OfferPilot AI home">
          <span className="brand-mark landing-brand-mark">OP</span>
          <span>
            <strong>OfferPilot AI</strong>
            <small>Interview Intelligence</small>
          </span>
        </a>
        <nav aria-label="Landing navigation">
          <a href="#features">Features</a>
          <a href="#workflow">Workflow</a>
          <a href="#pricing">Pricing</a>
          <a href="#faq">FAQ</a>
        </nav>
        <div className="landing-actions">
          <button className="icon-button" type="button" aria-label="Toggle theme" title="Toggle theme" onClick={onToggleTheme}>
            {theme === "dark" ? <Sun size={19} /> : <Moon size={19} />}
          </button>
          <button className="secondary-action nav-action" type="button" onClick={onOpenApp}>
            <ShieldCheck size={17} />
            Login
          </button>
        </div>
      </header>

      <section className="landing-hero" id="top">
        <div className="hero-visual" aria-hidden="true">
          <div className="hero-console">
            <div className="console-header">
              <span className="brand-mark">OP</span>
              <div>
                <strong>Offer Readiness</strong>
                <small>Live candidate cockpit</small>
              </div>
              <b>92%</b>
            </div>
            <div className="console-grid">
              <div className="console-panel score-panel">
                <span>Interview score</span>
                <strong>86.4</strong>
                <div className="mini-bars">
                  <i />
                  <i />
                  <i />
                  <i />
                  <i />
                </div>
              </div>
              <div className="console-panel">
                <span>Weak topic</span>
                <strong>Dynamic Programming</strong>
                <small>Next drill queued</small>
              </div>
              <div className="console-panel wide">
                <span>Evaluation stream</span>
                <div className="signal-row">
                  <b>Accuracy</b>
                  <em style={{ width: "82%" }} />
                </div>
                <div className="signal-row">
                  <b>Communication</b>
                  <em style={{ width: "91%" }} />
                </div>
                <div className="signal-row">
                  <b>Problem Solving</b>
                  <em style={{ width: "76%" }} />
                </div>
              </div>
              <div className="console-panel">
                <span>Resume match</span>
                <strong>78%</strong>
                <small>3 skills missing</small>
              </div>
            </div>
          </div>
        </div>
        <div className="hero-copy">
          <p className="landing-eyebrow">
            <Sparkles size={16} />
            AI interview readiness platform
          </p>
          <h1>OfferPilot AI</h1>
          <p>
            Interview intelligence for candidates and teams that need measurable readiness, sharper answers,
            stronger resumes, and a clear path from practice to offer.
          </p>
          <div className="hero-actions">
            <button className="primary-action hero-action" type="button" onClick={onOpenApp}>
              Start free
              <ArrowRight size={18} />
            </button>
            <a className="secondary-action hero-action" href="#workflow">
              See workflow
              <Play size={17} />
            </a>
          </div>
          <div className="hero-stats" aria-label="OfferPilot AI highlights">
            <span>
              <strong>11</strong>
              Interview domains
            </span>
            <span>
              <strong>6</strong>
              Readiness signals
            </span>
            <span>
              <strong>24/7</strong>
              Practice engine
            </span>
          </div>
        </div>
      </section>

      <section className="landing-section feature-section" id="features">
        <div className="section-heading">
          <p className="landing-eyebrow">Platform</p>
          <h2>Everything candidates need before the offer conversation.</h2>
        </div>
        <div className="feature-grid">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <article className="feature-card" key={feature.title}>
                <Icon size={22} />
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="landing-section workflow-section" id="workflow">
        <div className="section-heading">
          <p className="landing-eyebrow">How it works</p>
          <h2>From target role to weekly improvement loop.</h2>
        </div>
        <div className="workflow-grid">
          {steps.map(([number, title, detail]) => (
            <article className="workflow-step" key={number}>
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-section social-section">
        <div className="section-heading">
          <p className="landing-eyebrow">Teams supported</p>
          <h2>Built for individual preparation and commercial readiness programs.</h2>
        </div>
        <div className="company-strip" aria-label="Companies and organizations supported">
          {supportedCompanies.map(([label, Icon]) => (
            <span key={label}>
              <Icon size={18} />
              {label}
            </span>
          ))}
        </div>
        <div className="testimonial-grid">
          {testimonials.map((testimonial) => (
            <figure className="testimonial-card" key={testimonial.name}>
              <blockquote>{testimonial.quote}</blockquote>
              <figcaption>
                <strong>{testimonial.name}</strong>
                <span>{testimonial.role}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section className="landing-section pricing-section" id="pricing">
        <div className="section-heading">
          <p className="landing-eyebrow">Pricing</p>
          <h2>Plans for candidates, coaches, and talent teams.</h2>
        </div>
        <div className="pricing-grid">
          {pricing.map((plan) => (
            <article className={`pricing-card ${plan.featured ? "featured" : ""}`} key={plan.name}>
              <div>
                <span className="pricing-name">{plan.name}</span>
                <strong>{plan.price}</strong>
                {plan.price !== "Custom" && <small>/ month</small>}
              </div>
              <p>{plan.description}</p>
              <ul>
                {plan.items.map((item) => (
                  <li key={item}>
                    <Check size={16} />
                    {item}
                  </li>
                ))}
              </ul>
              <button className={plan.featured ? "primary-action" : "secondary-action"} type="button" onClick={onOpenApp}>
                {plan.name === "Enterprise" ? "Book demo" : "Choose plan"}
                <ChevronRight size={17} />
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-section faq-section" id="faq">
        <div className="section-heading">
          <p className="landing-eyebrow">FAQ</p>
          <h2>Practical answers for buyers and builders.</h2>
        </div>
        <div className="faq-list">
          {faqs.map(([question, answer]) => (
            <details key={question}>
              <summary>{question}</summary>
              <p>{answer}</p>
            </details>
          ))}
        </div>
      </section>

      <footer className="landing-footer">
        <div>
          <span className="brand-mark">OP</span>
          <strong>OfferPilot AI</strong>
        </div>
        <p>Interview intelligence for offer-ready candidates and teams.</p>
        <span>
          <ShieldCheck size={16} />
          Production-ready FastAPI, React, PostgreSQL, Docker, and analytics foundation.
        </span>
      </footer>
    </main>
  );
}
