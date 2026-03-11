import { useState, useEffect, useRef } from "react";

const DOCS = {
  invoice: {
    label: "Invoice",
    icon: "⬛",
    emoji: "🧾",
    color: "#00D4FF",
    confidence: 70.63,
    action: "verified",
    valid: false,
    ms: 340,
    errors: ["vendor_name field extracted via fallback"],
    warnings: [],
    fieldsRatio: 0.75,
    score: 82,
    strategy: "Strategy A + D (Text Layer + Table Detection)",
    extractor: "invoice_extractor.py",
    extracted: {
      invoice_number: "INV-2024-00847",
      invoice_date: "2024-03-15",
      due_date: "2024-04-14",
      vendor_name: "Nexus Tech Solutions Pty Ltd",
      bill_to: "Meridian Consulting Group",
      subtotal: "$8,450.00",
      tax_amount: "$845.00",
      total_amount: "$9,295.00",
      payment_terms: "Net 30",
    },
    problem: "Manual invoice entry: 8–12 min per document, 200+ invoices/month",
    saving: "~40 hours/month saved",
    filename: "Nexus_Tech_Invoice_INV-2024-00847.pdf",
  },
  bank_statement: {
    label: "Bank Statement",
    icon: "⬛",
    emoji: "🏦",
    color: "#7C3AED",
    confidence: 63.48,
    action: "verified",
    valid: true,
    ms: 520,
    errors: [],
    warnings: [],
    fieldsRatio: 1.0,
    score: 79,
    strategy: "Strategy A + D (Text Layer + Table Detection)",
    extractor: "bank_extractor.py",
    extracted: {
      account_number: "XXXX XXXX XXXX 4521",
      account_holder: "Meridian Consulting Group Pty Ltd",
      bank_name: "ANZ Bank",
      statement_period: "01/03/2024 – 31/03/2024",
      opening_balance: "$42,850.75",
      closing_balance: "$72,118.75",
      total_credits: "$66,500.00",
      total_debits: "$37,232.00",
      transactions_count: "13",
    },
    problem: "Reconciling 200+ transactions monthly across 4 bank accounts",
    saving: "~60 hours/month saved",
    filename: "ANZ_Bank_Statement_March2024.pdf",
  },
  purchase_order: {
    label: "Purchase Order",
    icon: "⬛",
    emoji: "📦",
    color: "#059669",
    confidence: 73.80,
    action: "verified",
    valid: true,
    ms: 290,
    errors: [],
    warnings: [],
    fieldsRatio: 1.0,
    score: 85,
    strategy: "Strategy A + D (Text Layer + Table Detection)",
    extractor: "po_extractor.py",
    extracted: {
      po_number: "PO-2024-0392",
      po_date: "2024-03-20",
      vendor_name: "Orbit Technologies Pty Ltd",
      delivery_date: "2024-04-05",
      order_total: "$23,210.00",
      approved_by: "Michael Torres — CFO",
      items_count: "5 line items",
    },
    problem: "PO-to-invoice matching done manually, frequent mismatch errors",
    saving: "~25 hours/month saved",
    filename: "PO-2024-0392_Orbit_Technologies.pdf",
  },
  contract: {
    label: "Contract",
    icon: "⬛",
    emoji: "📋",
    color: "#DC2626",
    confidence: 37.47,
    action: "needs_review",
    valid: true,
    ms: 410,
    errors: [],
    warnings: ["Confidence below high threshold — flagged for human review"],
    fieldsRatio: 0.67,
    score: 61,
    strategy: "Strategy A + C (Text Layer + Layout Anchoring)",
    extractor: "contract_extractor.py",
    extracted: {
      contract_title: "SERVICE AGREEMENT",
      parties: "Nexus Tech Solutions / Meridian Consulting",
      effective_date: "2024-01-01",
      termination_date: "2024-12-31",
      governing_law: "Victoria, Australia",
      key_clauses: "Confidentiality, IP, Force Majeure, Indemnification",
    },
    problem: "Tracking 50+ active contracts — renewal dates missed, clauses not logged",
    saving: "~15 hours/month saved",
    filename: "Service_Agreement_Nexus_Meridian_2024.pdf",
  },
  salary_slip: {
    label: "Salary Slip",
    icon: "⬛",
    emoji: "💰",
    color: "#F59E0B",
    confidence: 66.35,
    action: "verified",
    valid: true,
    ms: 270,
    errors: [],
    warnings: [],
    fieldsRatio: 1.0,
    score: 81,
    strategy: "Strategy A + D (Text Layer + Table Detection)",
    extractor: "salary_extractor.py",
    extracted: {
      employee_name: "Sarah Chen",
      employee_id: "EMP-0042",
      department: "Strategy & Consulting",
      designation: "Senior Consultant",
      pay_period: "March 2024",
      gross_salary: "$11,100.00",
      total_deductions: "$4,411.00",
      net_salary: "$6,689.00",
    },
    problem: "Payroll verification for 80+ staff required manual cross-checking",
    saving: "~30 hours/month saved",
    filename: "Payslip_Sarah_Chen_March2024.pdf",
  },
  utility_bill: {
    label: "Utility Bill",
    icon: "⬛",
    emoji: "⚡",
    color: "#0EA5E9",
    confidence: 66.20,
    action: "verified",
    valid: true,
    ms: 195,
    errors: [],
    warnings: [],
    fieldsRatio: 1.0,
    score: 80,
    strategy: "Strategy A + C (Text Layer + Layout Anchoring)",
    extractor: "utility_extractor.py",
    extracted: {
      utility_type: "Electricity",
      account_id: "AGL-9823-4410",
      customer_name: "Meridian Consulting Group Pty Ltd",
      billing_period: "01/03/2024 – 31/03/2024",
      units_consumed: "1,662 kWh",
      previous_reading: "84,210 kWh",
      current_reading: "85,872 kWh",
      amount_due: "$499.16",
    },
    problem: "Utility bills across 12 locations — manual data entry per bill per month",
    saving: "~20 hours/month saved",
    filename: "AGL_Electricity_March2024.pdf",
  },
  application_form: {
    label: "Application Form",
    icon: "⬛",
    emoji: "📝",
    color: "#EC4899",
    confidence: 28.69,
    action: "unverified",
    valid: false,
    ms: 380,
    errors: ["applicant_name resolved via generic fallback"],
    warnings: ["Low confidence — structured form layout requires layout anchoring"],
    fieldsRatio: 0.5,
    score: 48,
    strategy: "Strategy C + Generic Fallback (Layout Anchoring)",
    extractor: "generic_extractor.py",
    extracted: {
      applicant_name: "Orbit Technologies Pty Ltd",
      contact_person: "Lisa Pham",
      email: "l.pham@orbittech.com.au",
      phone: "+61 7 3000 9988",
      credit_limit_requested: "$50,000.00",
      bank_name: "Westpac Banking Corporation",
    },
    problem: "Credit applications manually entered into CRM — 20+ min each",
    saving: "~18 hours/month saved",
    filename: "Credit_Application_Form_OrbitTech.pdf",
  },
  report: {
    label: "Report",
    icon: "⬛",
    emoji: "📊",
    color: "#6366F1",
    confidence: 6.35,
    action: "unverified",
    valid: false,
    ms: 460,
    errors: ["No structured fields detected — generic extraction applied"],
    warnings: ["Report type has high variance — custom extractor recommended"],
    fieldsRatio: 0.0,
    score: 32,
    strategy: "Generic Fallback Extractor",
    extractor: "generic_extractor.py",
    extracted: {
      detected_dates: "05/04/2024, FY2024",
      detected_amounts: "$1.24M, $980K, $620K, $451K, $789K",
      word_count: "248 words",
      prepared_by: "Michael Torres, CFO",
      period: "Q1 2024 (Jan – Mar)",
    },
    problem: "KPI extraction from board reports required reading and manual copy-paste",
    saving: "~12 hours/month saved",
    filename: "Q1_Financial_Performance_Report_2024.pdf",
  },
};

const PIPELINE_STEPS = [
  { id: 1, name: "Document Upload", desc: "PDF received, text layer probed", icon: "↑" },
  { id: 2, name: "Type Classifier", desc: "Keyword + TF-IDF + Regex scoring", icon: "🔍" },
  { id: 3, name: "Strategy Selector", desc: "Text quality → strategy A/B/C/D", icon: "⚙" },
  { id: 4, name: "Field Extractor", desc: "Document-specific module runs", icon: "⛏" },
  { id: 5, name: "Validation Engine", desc: "Rules checked, errors flagged", icon: "✓" },
  { id: 6, name: "Confidence Score", desc: "Final score + storage action", icon: "◎" },
  { id: 7, name: "JSON Output", desc: "Structured data stored / returned", icon: "{ }" },
];

const actionConfig = {
  verified: { label: "VERIFIED", bg: "#052e16", border: "#16a34a", text: "#4ade80" },
  needs_review: { label: "NEEDS REVIEW", bg: "#1c1003", border: "#d97706", text: "#fbbf24" },
  unverified: { label: "UNVERIFIED", bg: "#1c0505", border: "#dc2626", text: "#f87171" },
};

function ScoreRing({ score, color, size = 64 }) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1a1a2e" strokeWidth={6} />
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={6}
        strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round"
        style={{ transition: "stroke-dasharray 1s ease" }} />
    </svg>
  );
}

function PipelineViz({ activeStep }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 0, overflowX: "auto", padding: "8px 0" }}>
      {PIPELINE_STEPS.map((step, i) => (
        <div key={step.id} style={{ display: "flex", alignItems: "center" }}>
          <div style={{
            display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
            minWidth: 80,
          }}>
            <div style={{
              width: 40, height: 40, borderRadius: "50%",
              background: activeStep >= step.id ? "#0f0f23" : "#0a0a14",
              border: `2px solid ${activeStep >= step.id ? "#00D4FF" : "#1e1e3a"}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 14,
              boxShadow: activeStep >= step.id ? "0 0 12px rgba(0,212,255,0.4)" : "none",
              transition: "all 0.4s ease",
            }}>
              {activeStep > step.id ? "✓" : step.icon}
            </div>
            <div style={{
              fontSize: 9, color: activeStep >= step.id ? "#00D4FF" : "#444",
              textAlign: "center", lineHeight: 1.3, maxWidth: 72,
              transition: "color 0.4s",
            }}>
              {step.name}
            </div>
          </div>
          {i < PIPELINE_STEPS.length - 1 && (
            <div style={{
              width: 24, height: 2,
              background: activeStep > step.id ? "#00D4FF" : "#1e1e3a",
              marginBottom: 20, flexShrink: 0,
              transition: "background 0.4s ease",
            }} />
          )}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [selected, setSelected] = useState("invoice");
  const [activeStep, setActiveStep] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [showResult, setShowResult] = useState(true);
  const [tab, setTab] = useState("extracted");
  const stepRef = useRef(null);

  const doc = DOCS[selected];
  const ac = actionConfig[doc.action];

  function runDemo() {
    setProcessing(true);
    setShowResult(false);
    setActiveStep(0);
    setTab("extracted");
    let step = 0;
    const interval = setInterval(() => {
      step++;
      setActiveStep(step);
      if (step >= PIPELINE_STEPS.length) {
        clearInterval(interval);
        setTimeout(() => {
          setProcessing(false);
          setShowResult(true);
        }, 300);
      }
    }, 300);
  }

  useEffect(() => {
    setShowResult(true);
    setActiveStep(PIPELINE_STEPS.length);
  }, [selected]);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#050510",
      color: "#e0e0f0",
      fontFamily: "'Courier New', monospace",
      padding: "24px 16px",
    }}>
      {/* Header */}
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            fontSize: 11, letterSpacing: 8, color: "#00D4FF", marginBottom: 8,
            textTransform: "uppercase",
          }}>
            PORTFOLIO PROJECT — AUTOMATION SYSTEM
          </div>
          <h1 style={{
            margin: 0, fontSize: "clamp(22px, 4vw, 38px)",
            background: "linear-gradient(135deg, #00D4FF 0%, #7C3AED 50%, #EC4899 100%)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            fontFamily: "'Courier New', monospace",
            letterSpacing: 2,
            lineHeight: 1.2,
          }}>
            MODULAR INTELLIGENT<br />DOCUMENT PROCESSING ENGINE
          </h1>
          <div style={{ fontSize: 12, color: "#5a5a8a", marginTop: 10, letterSpacing: 2 }}>
            MIDPE v1.0 — 8 Document Types · Rule-Based + ML · Confidence Scoring · JSON Output
          </div>
        </div>

        {/* Doc selector */}
        <div style={{
          display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center",
          marginBottom: 28,
        }}>
          {Object.entries(DOCS).map(([key, d]) => (
            <button key={key} onClick={() => setSelected(key)}
              style={{
                padding: "7px 14px",
                background: selected === key ? d.color + "20" : "transparent",
                border: `1px solid ${selected === key ? d.color : "#1e1e3a"}`,
                color: selected === key ? d.color : "#5a5a8a",
                borderRadius: 4, cursor: "pointer", fontSize: 11,
                fontFamily: "'Courier New', monospace",
                letterSpacing: 1,
                transition: "all 0.2s",
              }}>
              {d.emoji} {d.label.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Main panel */}
        <div style={{
          border: `1px solid ${doc.color}40`,
          borderRadius: 8,
          background: "#080818",
          overflow: "hidden",
        }}>
          {/* Top bar */}
          <div style={{
            background: `linear-gradient(90deg, ${doc.color}15, transparent)`,
            borderBottom: `1px solid ${doc.color}30`,
            padding: "14px 20px",
            display: "flex", alignItems: "center", justifyContent: "space-between",
            flexWrap: "wrap", gap: 12,
          }}>
            <div>
              <div style={{ fontSize: 11, color: doc.color, letterSpacing: 3, marginBottom: 4 }}>
                DOCUMENT — {doc.label.toUpperCase()}
              </div>
              <div style={{ fontSize: 12, color: "#5a5a8a" }}>📄 {doc.filename}</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{
                padding: "4px 12px",
                background: ac.bg,
                border: `1px solid ${ac.border}`,
                color: ac.text,
                borderRadius: 3, fontSize: 10, letterSpacing: 2,
              }}>
                {ac.label}
              </div>
              <button onClick={runDemo} disabled={processing}
                style={{
                  padding: "8px 20px",
                  background: processing ? "#111" : doc.color,
                  color: processing ? "#666" : "#000",
                  border: "none", borderRadius: 4, cursor: processing ? "default" : "pointer",
                  fontSize: 11, fontFamily: "'Courier New', monospace",
                  fontWeight: "bold", letterSpacing: 1,
                  transition: "all 0.2s",
                }}>
                {processing ? "PROCESSING..." : "▶ RUN PIPELINE"}
              </button>
            </div>
          </div>

          {/* Pipeline visualizer */}
          <div style={{ padding: "16px 20px", borderBottom: "1px solid #1a1a2e" }}>
            <PipelineViz activeStep={activeStep} />
          </div>

          {/* Stats row */}
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            borderBottom: "1px solid #1a1a2e",
          }}>
            {[
              { label: "CLASSIFIER CONF.", value: `${doc.confidence.toFixed(1)}%`, color: doc.color },
              { label: "FINAL SCORE", value: `${doc.score}%`, color: doc.color },
              { label: "PROCESSING TIME", value: `${doc.ms}ms`, color: "#7C3AED" },
              { label: "FIELDS RATIO", value: `${Math.round(doc.fieldsRatio * 100)}%`, color: "#059669" },
              { label: "STRATEGY", value: doc.strategy.split("(")[0].trim(), color: "#EC4899" },
              { label: "EXTRACTOR", value: doc.extractor, color: "#F59E0B" },
            ].map((s, i) => (
              <div key={i} style={{
                padding: "14px 16px",
                borderRight: i < 5 ? "1px solid #1a1a2e" : "none",
              }}>
                <div style={{ fontSize: 9, color: "#444", letterSpacing: 2, marginBottom: 6 }}>{s.label}</div>
                <div style={{ fontSize: 11, color: s.color, wordBreak: "break-word" }}>{s.value}</div>
              </div>
            ))}
          </div>

          {/* Content area */}
          {showResult && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
              {/* Left: Extracted data */}
              <div style={{ padding: 20, borderRight: "1px solid #1a1a2e" }}>
                <div style={{ fontSize: 10, letterSpacing: 3, color: "#444", marginBottom: 16 }}>
                  EXTRACTED DATA
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {Object.entries(doc.extracted).map(([k, v]) => (
                    <div key={k} style={{
                      display: "flex", justifyContent: "space-between", gap: 12,
                      padding: "8px 12px",
                      background: "#0a0a1a",
                      border: "1px solid #1a1a2e",
                      borderRadius: 4,
                      flexWrap: "wrap",
                    }}>
                      <span style={{ fontSize: 10, color: "#5a5a8a", flex: "0 0 auto" }}>
                        {k.replace(/_/g, " ").toUpperCase()}
                      </span>
                      <span style={{
                        fontSize: 11, color: "#e0e0f0", textAlign: "right",
                        wordBreak: "break-word",
                      }}>
                        {String(v)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right: Analysis + Problem/Solution */}
              <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 20 }}>
                {/* Confidence breakdown */}
                <div>
                  <div style={{ fontSize: 10, letterSpacing: 3, color: "#444", marginBottom: 14 }}>
                    CONFIDENCE BREAKDOWN
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
                    <div style={{ position: "relative" }}>
                      <ScoreRing score={doc.score} color={doc.color} size={80} />
                      <div style={{
                        position: "absolute", top: "50%", left: "50%",
                        transform: "translate(-50%, -50%)",
                        fontSize: 13, color: doc.color, fontWeight: "bold",
                      }}>
                        {doc.score}
                      </div>
                    </div>
                    <div style={{ flex: 1 }}>
                      {[
                        ["Keyword Match", 35, doc.confidence > 50 ? 28 : 15],
                        ["Fields Present", 30, Math.round(doc.fieldsRatio * 28)],
                        ["Format Valid", 20, doc.valid ? 18 : 10],
                        ["Text Quality", 15, 14],
                      ].map(([name, max, val]) => (
                        <div key={name} style={{ marginBottom: 8 }}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                            <span style={{ fontSize: 9, color: "#5a5a8a" }}>{name}</span>
                            <span style={{ fontSize: 9, color: doc.color }}>{val}/{max}</span>
                          </div>
                          <div style={{ height: 4, background: "#1a1a2e", borderRadius: 2 }}>
                            <div style={{
                              height: "100%", borderRadius: 2,
                              background: doc.color,
                              width: `${(val / max) * 100}%`,
                              transition: "width 1s ease",
                            }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Validation */}
                <div>
                  <div style={{ fontSize: 10, letterSpacing: 3, color: "#444", marginBottom: 12 }}>
                    VALIDATION RESULT
                  </div>
                  <div style={{
                    padding: "10px 14px",
                    background: doc.valid ? "#052e16" : "#1c0a05",
                    border: `1px solid ${doc.valid ? "#16a34a" : "#92400e"}`,
                    borderRadius: 4, marginBottom: 8,
                    fontSize: 11,
                    color: doc.valid ? "#4ade80" : "#fbbf24",
                  }}>
                    {doc.valid ? "✓ All required fields validated successfully" : "⚠ " + doc.errors[0]}
                  </div>
                  {doc.warnings.map((w, i) => (
                    <div key={i} style={{
                      padding: "8px 12px", background: "#1c1003",
                      border: "1px solid #d97706", borderRadius: 4,
                      fontSize: 10, color: "#fbbf24", marginBottom: 4,
                    }}>
                      ⚡ {w}
                    </div>
                  ))}
                </div>

                {/* Business context */}
                <div style={{
                  padding: 16,
                  background: `${doc.color}08`,
                  border: `1px solid ${doc.color}25`,
                  borderRadius: 6,
                }}>
                  <div style={{ fontSize: 10, color: doc.color, letterSpacing: 2, marginBottom: 10 }}>
                    BUSINESS PROBLEM SOLVED
                  </div>
                  <div style={{ fontSize: 11, color: "#9090c0", lineHeight: 1.7, marginBottom: 12 }}>
                    <span style={{ color: "#ef4444" }}>BEFORE: </span>{doc.problem}
                  </div>
                  <div style={{
                    display: "flex", alignItems: "center", gap: 8,
                    padding: "8px 12px",
                    background: "#052e16",
                    border: "1px solid #16a34a",
                    borderRadius: 4,
                  }}>
                    <span style={{ fontSize: 16 }}>📉</span>
                    <div>
                      <div style={{ fontSize: 9, color: "#4ade80", letterSpacing: 2 }}>AUTOMATION RESULT</div>
                      <div style={{ fontSize: 12, color: "#4ade80", fontWeight: "bold" }}>{doc.saving}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Architecture diagram */}
        <div style={{
          marginTop: 24,
          border: "1px solid #1a1a2e",
          borderRadius: 8,
          background: "#080818",
          padding: 24,
        }}>
          <div style={{ fontSize: 10, letterSpacing: 3, color: "#444", marginBottom: 20, textAlign: "center" }}>
            SYSTEM ARCHITECTURE — ALL COMPONENTS MODULAR & CONFIGURABLE
          </div>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
            gap: 12,
          }}>
            {[
              { name: "config.py", desc: "Document types, rules, thresholds — all editable", color: "#00D4FF" },
              { name: "classifier.py", desc: "Keyword + TF-IDF + Regex scoring", color: "#7C3AED" },
              { name: "strategy_selector.py", desc: "Auto-selects A/B/C/D strategy", color: "#059669" },
              { name: "8 × extractor.py", desc: "Document-specific field extractors", color: "#EC4899" },
              { name: "validator.py", desc: "Configurable validation rules", color: "#F59E0B" },
              { name: "scorer.py", desc: "Confidence scoring + storage action", color: "#0EA5E9" },
              { name: "pipeline.py", desc: "Main orchestrator: plug-and-play", color: "#6366F1" },
            ].map((m) => (
              <div key={m.name} style={{
                padding: "12px 14px",
                background: "#0a0a1a",
                border: `1px solid ${m.color}30`,
                borderRadius: 6,
              }}>
                <div style={{ fontSize: 10, color: m.color, marginBottom: 5, fontWeight: "bold" }}>{m.name}</div>
                <div style={{ fontSize: 9, color: "#5a5a8a", lineHeight: 1.5 }}>{m.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Total impact */}
        <div style={{
          marginTop: 16,
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: 12,
        }}>
          {[
            { label: "Document Types", value: "8", sub: "Invoice → Report" },
            { label: "Extraction Strategies", value: "4", sub: "A, B, C, D" },
            { label: "Avg Processing Time", value: "358ms", sub: "per document" },
            { label: "Hours Saved / Month", value: "220+", sub: "across all doc types" },
            { label: "Config Lines", value: "~150", sub: "fully editable YAML/Python" },
          ].map((stat) => (
            <div key={stat.label} style={{
              padding: "16px", textAlign: "center",
              background: "#080818",
              border: "1px solid #1a1a2e",
              borderRadius: 8,
            }}>
              <div style={{ fontSize: 24, color: "#00D4FF", fontWeight: "bold", marginBottom: 4 }}>{stat.value}</div>
              <div style={{ fontSize: 10, color: "#e0e0f0", marginBottom: 2 }}>{stat.label}</div>
              <div style={{ fontSize: 9, color: "#444" }}>{stat.sub}</div>
            </div>
          ))}
        </div>

        <div style={{ textAlign: "center", marginTop: 20, fontSize: 9, color: "#2a2a4a", letterSpacing: 2 }}>
          MIDPE v1.0 — BUILT WITH PYTHON · REGEX · TF-IDF · PDFPLUMBER · PYMUPDF · TESSERACT
        </div>
      </div>
    </div>
  );
}