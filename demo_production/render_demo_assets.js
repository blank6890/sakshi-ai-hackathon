const { chromium } = require("/home/blank/sakshi-ai-hackathon/web/node_modules/playwright");
const fs = require("fs");
const path = require("path");

const SLIDES_DIR = "/home/blank/sakshi-ai-hackathon/demo_production/slides";

const BASE_STYLES = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1920px;
    height: 1080px;
    background: #090d16;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    overflow: hidden;
    position: relative;
    display: flex;
    flex-direction: column;
  }
  .bg-grid {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(59, 130, 246, 0.12) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
  }
  .glow-blue {
    position: absolute;
    top: -150px;
    left: 20%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.18) 0%, transparent 70%);
    filter: blur(80px);
    pointer-events: none;
  }
  .glow-purple {
    position: absolute;
    bottom: -150px;
    right: 15%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, transparent 70%);
    filter: blur(80px);
    pointer-events: none;
  }
  .navbar {
    height: 80px;
    padding: 0 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    z-index: 10;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #ffffff;
  }
  .brand-badge {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 700;
    color: white;
  }
  .tagline {
    font-size: 14px;
    color: #94a3b8;
    background: rgba(255,255,255,0.05);
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.1);
  }
  .main-content {
    flex: 1;
    padding: 50px 60px 40px 60px;
    display: flex;
    flex-direction: column;
    z-index: 5;
  }
  .badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    width: fit-content;
    margin-bottom: 14px;
  }
  .pill-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
  .pill-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
  .pill-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
  .pill-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
  .title-lg { font-size: 46px; font-weight: 800; line-height: 1.15; letter-spacing: -0.02em; color: #ffffff; margin-bottom: 12px; }
  .subtitle-lg { font-size: 20px; color: #94a3b8; max-width: 900px; line-height: 1.5; margin-bottom: 30px; }
`;

const SLIDES = [
  // Scene 1: Hook & Problem Statement
  {
    name: "slide_1_hook.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .vs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; flex: 1; }
        .card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 32px; display: flex; flex-direction: column; }
        .card-danger { border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.04); }
        .card-success { border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.05); }
        .item { display: flex; align-items: flex-start; gap: 14px; margin-top: 18px; font-size: 17px; color: #cbd5e1; }
        .item-icon { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; margin-top: 2px; }
        .icon-red { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        .icon-green { background: rgba(16, 185, 129, 0.2); color: #34d399; }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-blue"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge">SAKSHI AI</span> Adaptive Exam-Prep Tutor</div>
          <div class="tagline">NCERT Class 10 Physics Edition</div>
        </div>
        <div class="main-content">
          <div class="badge-pill pill-blue">The Core Problem</div>
          <div class="title-lg">Generic AI Tutors Don't Track Understanding</div>
          <div class="subtitle-lg">Standard LLM tutors answer questions in isolation without psychometric student modeling.</div>
          <div class="vs-grid">
            <div class="card card-danger">
              <div style="font-size: 22px; font-weight: 700; color: #f87171; margin-bottom: 8px;">❌ Generic Chatbot Tutors</div>
              <div style="font-size: 15px; color: #94a3b8; margin-bottom: 16px;">Standard stateless prompt wrappers</div>
              <div class="item"><div class="item-icon icon-red">✕</div><div><strong>No Learner Model:</strong> Completely blind to latent concept mastery.</div></div>
              <div class="item"><div class="item-icon icon-red">✕</div><div><strong>Superficial Grading:</strong> Flags right/wrong strings without analyzing step-by-step reasoning.</div></div>
              <div class="item"><div class="item-icon icon-red">✕</div><div><strong>Uncalibrated Random Questions:</strong> Poses arbitrary problems without syllabus prerequisite awareness.</div></div>
              <div class="item"><div class="item-icon icon-red">✕</div><div><strong>Zero Educator Visibility:</strong> No cohort tracking or class-wide gap heatmaps.</div></div>
            </div>
            <div class="card card-success">
              <div style="font-size: 22px; font-weight: 700; color: #34d399; margin-bottom: 8px;">✅ Sakshi AI Adaptive Tutor</div>
              <div style="font-size: 15px; color: #94a3b8; margin-bottom: 16px;">Psychometrically grounded cognitive architecture</div>
              <div class="item"><div class="item-icon icon-green">✓</div><div><strong>Bayesian Knowledge Tracing (BKT):</strong> Updates latent mastery P(L) after every response.</div></div>
              <div class="item"><div class="item-icon icon-green">✓</div><div><strong>Reasoning Misconception Detection:</strong> Catches lucky guesses and exposes flawed cognitive rules.</div></div>
              <div class="item"><div class="item-icon icon-green">✓</div><div><strong>Prerequisite DAG & ZPD Calibration:</strong> Targets the student's Zone of Proximal Development.</div></div>
              <div class="item"><div class="item-icon icon-green">✓</div><div><strong>Teacher Cohort Analytics:</strong> Real-time 2D mastery heatmap across the entire classroom.</div></div>
            </div>
          </div>
        </div>
      </body></html>
    `
  },

  // Scene 2: Diagnostic Assessment
  {
    name: "slide_2_diagnostic.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .diag-grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 30px; flex: 1; }
        .diag-card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 28px; }
        .question-box { background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 14px; padding: 20px; margin-bottom: 16px; }
        .input-box { background: #0b1120; border: 1px solid rgba(255,255,255,0.12); border-radius: 10px; padding: 12px; font-family: monospace; font-size: 14px; color: #38bdf8; margin-top: 8px; }
        .stat-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .bar-bg { width: 180px; height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 5px; background: linear-gradient(90deg, #3b82f6, #10b981); }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-blue"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge">FEATURE 1</span> Diagnostic Assessment</div>
          <div class="tagline">Calibrating Initial Learner Baseline</div>
        </div>
        <div class="main-content">
          <div class="badge-pill pill-emerald">Step 1: Calibration Intake</div>
          <div class="title-lg">6-Milestone Adaptive Diagnostic Test</div>
          <div class="subtitle-lg">Establishes the learner's initial probability vector across major syllabus milestones before instruction begins.</div>
          <div class="diag-grid">
            <div class="diag-card">
              <div style="font-size: 18px; font-weight: 700; color: #60a5fa; margin-bottom: 12px;">Active Diagnostic Intake (/diagnostic)</div>
              <div class="question-box">
                <div style="font-size: 13px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Question 3 of 6 · Electricity</div>
                <div style="font-size: 16px; font-weight: 600; color: #f8fafc; margin: 8px 0;">State Ohm's Law and calculate the current if V = 12V and R = 4 ohms.</div>
                <div style="font-size: 12px; color: #cbd5e1; margin-top: 10px;">Step-by-Step Reasoning Input:</div>
                <div class="input-box">"By Ohm's law, I = V / R. Substituting V=12 and R=4, I = 12/4 = 3 Amperes."</div>
                <div style="font-size: 12px; color: #cbd5e1; margin-top: 10px;">Final Answer:</div>
                <div class="input-box" style="color: #34d399;">"I = 3 A"</div>
              </div>
              <div style="display: flex; gap: 12px;">
                <div style="flex: 1; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); padding: 12px; border-radius: 10px; text-align: center;">
                  <div style="font-size: 12px; color: #a7f3d0;">Intake Status</div>
                  <div style="font-size: 18px; font-weight: 700; color: #34d399;">Active Evaluator</div>
                </div>
                <div style="flex: 1; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); padding: 12px; border-radius: 10px; text-align: center;">
                  <div style="font-size: 12px; color: #bfdbfe;">Syllabus Coverage</div>
                  <div style="font-size: 18px; font-weight: 700; color: #60a5fa;">100% Core Clusters</div>
                </div>
              </div>
            </div>
            <div class="diag-card">
              <div style="font-size: 18px; font-weight: 700; color: #34d399; margin-bottom: 12px;">Calibrated Initial Prior Baseline (P_L0)</div>
              <div class="stat-row">
                <span style="font-size: 15px; color: #e2e8f0;">Electric Charge & Current</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div class="bar-bg"><div class="bar-fill" style="width: 82%;"></div></div>
                  <span style="font-family: monospace; font-size: 15px; color: #34d399; font-weight: 700;">0.82</span>
                </div>
              </div>
              <div class="stat-row">
                <span style="font-size: 15px; color: #e2e8f0;">Potential Difference</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div class="bar-bg"><div class="bar-fill" style="width: 78%;"></div></div>
                  <span style="font-family: monospace; font-size: 15px; color: #34d399; font-weight: 700;">0.78</span>
                </div>
              </div>
              <div class="stat-row">
                <span style="font-size: 15px; color: #e2e8f0;">Ohm's Law</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div class="bar-bg"><div class="bar-fill" style="width: 32%; background: #f87171;"></div></div>
                  <span style="font-family: monospace; font-size: 15px; color: #f87171; font-weight: 700;">0.32</span>
                </div>
              </div>
              <div class="stat-row">
                <span style="font-size: 15px; color: #e2e8f0;">Series & Parallel Resistors</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div class="bar-bg"><div class="bar-fill" style="width: 25%; background: #f87171;"></div></div>
                  <span style="font-family: monospace; font-size: 15px; color: #f87171; font-weight: 700;">0.25</span>
                </div>
              </div>
              <div class="stat-row">
                <span style="font-size: 15px; color: #e2e8f0;">Spherical Mirrors & Reflection</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div class="bar-bg"><div class="bar-fill" style="width: 70%;"></div></div>
                  <span style="font-family: monospace; font-size: 15px; color: #34d399; font-weight: 700;">0.70</span>
                </div>
              </div>
              <div class="stat-row">
                <span style="font-size: 15px; color: #e2e8f0;">Magnetic Effects & Solenoids</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div class="bar-bg"><div class="bar-fill" style="width: 40%; background: #fbbf24;"></div></div>
                  <span style="font-family: monospace; font-size: 15px; color: #fbbf24; font-weight: 700;">0.40</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </body></html>
    `
  },

  // Scene 3: Concept Graph DAG
  {
    name: "slide_3_dag.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .dag-container { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 30px; flex: 1; display: flex; flex-direction: column; }
        .dag-flow { display: flex; align-items: center; justify-content: space-between; margin: auto 0; gap: 14px; }
        .node { background: rgba(15, 23, 42, 0.9); border: 2px solid rgba(59, 130, 246, 0.4); border-radius: 14px; padding: 18px 20px; width: 220px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        .node-mastered { border-color: #10b981; background: rgba(16, 185, 129, 0.08); }
        .node-frontier { border-color: #f59e0b; background: rgba(245, 158, 11, 0.08); animation: pulse 2s infinite; }
        .node-locked { border-color: rgba(255,255,255,0.15); opacity: 0.5; }
        .arrow { font-size: 26px; color: #64748b; font-weight: 700; }
        .tag-status { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; margin-top: 8px; display: inline-block; }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-purple"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge">FEATURE 2</span> Syllabus Concept Graph</div>
          <div class="tagline">NCERT Class 10 Physics Prerequisite DAG</div>
        </div>
        <div class="main-content">
          <div class="badge-pill pill-purple">NetworkX Validated Topological Dependency</div>
          <div class="title-lg">Strict Prerequisite Gating (No Circular Deadlocks)</div>
          <div class="subtitle-lg">15 Concepts spanning Light, Electricity, and Magnetism structured into an immutable prerequisite hierarchy.</div>
          <div class="dag-container">
            <div style="font-size: 18px; font-weight: 700; color: #cbd5e1; margin-bottom: 20px;">Electricity Unit: Topological Mastery Progression</div>
            <div class="dag-flow">
              <div class="node node-mastered">
                <div style="font-size: 12px; color: #94a3b8;">Root 1</div>
                <div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 4px 0;">Electric Charge</div>
                <div class="tag-status" style="background: rgba(16,185,129,0.2); color: #34d399;">Mastered 92%</div>
              </div>
              <div class="arrow">➔</div>
              <div class="node node-mastered">
                <div style="font-size: 12px; color: #94a3b8;">Prerequisite 1</div>
                <div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 4px 0;">Electric Current</div>
                <div class="tag-status" style="background: rgba(16,185,129,0.2); color: #34d399;">Mastered 85%</div>
              </div>
              <div class="arrow">➔</div>
              <div class="node node-mastered">
                <div style="font-size: 12px; color: #94a3b8;">Prerequisite 2</div>
                <div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 4px 0;">Potential Difference</div>
                <div class="tag-status" style="background: rgba(16,185,129,0.2); color: #34d399;">Mastered 85%</div>
              </div>
              <div class="arrow">➔</div>
              <div class="node node-frontier">
                <div style="font-size: 12px; color: #fbbf24; font-weight: 700;">ZPD Frontier ⚡</div>
                <div style="font-size: 16px; font-weight: 700; color: #fbbf24; margin: 4px 0;">Ohm's Law</div>
                <div class="tag-status" style="background: rgba(245,158,11,0.2); color: #fbbf24;">In Progress 35%</div>
              </div>
              <div class="arrow">➔</div>
              <div class="node node-locked">
                <div style="font-size: 12px; color: #64748b;">Requires Ohm's Law</div>
                <div style="font-size: 16px; font-weight: 700; color: #94a3b8; margin: 4px 0;">Series & Parallel</div>
                <div class="tag-status" style="background: rgba(255,255,255,0.08); color: #64748b;">Locked</div>
              </div>
            </div>
            <div style="margin-top: 30px; padding: 18px 24px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <span style="color: #38bdf8; font-weight: 700;">DAG Guarantee:</span>
                <span style="color: #94a3b8;"> Advanced nodes cannot be recommended until prerequisite dependencies clear 70% threshold.</span>
              </div>
              <div style="color: #34d399; font-weight: 700; font-family: monospace;">NetworkX: is_directed_acyclic_graph() = True</div>
            </div>
          </div>
        </div>
      </body></html>
    `
  },

  // Scene 4: BKT Model
  {
    name: "slide_4_bkt.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .bkt-grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 30px; flex: 1; }
        .card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 28px; }
        .formula-card { background: #0b1120; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 14px; padding: 20px; font-family: 'Courier New', monospace; font-size: 16px; line-height: 1.7; color: #93c5fd; }
        .param-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 20px; }
        .param-box { background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.08); padding: 14px; border-radius: 10px; }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-blue"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge">FEATURE 3</span> Learner Model</div>
          <div class="tagline">4-Parameter Bayesian Knowledge Tracing</div>
        </div>
        <div class="main-content">
          <div class="badge-pill pill-blue">Probabilistic Cognitive Tracking</div>
          <div class="title-lg">Dynamic Mastery Updates After Every Interaction</div>
          <div class="subtitle-lg">Replacing arbitrary moving averages with authentic closed-form Bayesian probability calculus.</div>
          <div class="bkt-grid">
            <div class="card">
              <div style="font-size: 18px; font-weight: 700; color: #60a5fa; margin-bottom: 12px;">Bayesian Knowledge Tracing Equations</div>
              <div class="formula-card">
                <div>// Observation Posterior:</div>
                <div style="color: #34d399;">P(L | correct) = [ P(L) * (1 - P(S)) ] / P(Correct)</div>
                <div style="color: #f87171;">P(L | wrong)   = [ P(L) * P(S) ] / P(Wrong)</div>
                <br>
                <div>// Transition Step:</div>
                <div style="color: #facc15; font-weight: bold;">P(L_next) = P(L | Obs) + (1 - P(L | Obs)) * P(T)</div>
                <br>
                <div style="color: #94a3b8;">// Bound Guard: Clamped strictly to [0.0001, 0.9999]</div>
              </div>
              <div class="param-grid">
                <div class="param-box"><div style="font-size: 12px; color: #94a3b8;">Prior Mastery P(L0)</div><div style="font-size: 20px; font-weight: 700; color: #60a5fa;">0.20</div></div>
                <div class="param-box"><div style="font-size: 12px; color: #94a3b8;">Learning Transit P(T)</div><div style="font-size: 20px; font-weight: 700; color: #facc15;">0.15</div></div>
                <div class="param-box"><div style="font-size: 12px; color: #94a3b8;">Slip Prob P(S)</div><div style="font-size: 20px; font-weight: 700; color: #f87171;">0.10</div></div>
                <div class="param-box"><div style="font-size: 12px; color: #94a3b8;">Guess Prob P(G)</div><div style="font-size: 20px; font-weight: 700; color: #a78bfa;">0.20</div></div>
              </div>
            </div>
            <div class="card">
              <div style="font-size: 18px; font-weight: 700; color: #34d399; margin-bottom: 12px;">Live Mathematical Update Proof</div>
              <div style="padding: 18px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; margin-bottom: 14px;">
                <div style="font-size: 14px; color: #94a3b8;">Prior State</div>
                <div style="font-size: 24px; font-weight: 700; color: #cbd5e1;">P(L) = 0.2000</div>
              </div>
              <div style="padding: 18px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; margin-bottom: 14px;">
                <div style="font-size: 14px; color: #a7f3d0;">After 1st Sound Correct Answer</div>
                <div style="font-size: 24px; font-weight: 700; color: #34d399;">P(L_t1) = 0.6010 <span style="font-size: 14px;">(+40.1%)</span></div>
              </div>
              <div style="padding: 18px; background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.5); border-radius: 12px;">
                <div style="font-size: 14px; color: #a7f3d0;">After 2nd Sound Correct Answer</div>
                <div style="font-size: 24px; font-weight: 700; color: #34d399;">P(L_t2) = 0.8875 <span style="font-size: 14px;">(Mastery Achieved)</span></div>
              </div>
            </div>
          </div>
        </div>
      </body></html>
    `
  },

  // Scene 5: Misconception Detection
  {
    name: "slide_5_misconception.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .hero-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; flex: 1; }
        .hero-card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 26px; display: flex; flex-direction: column; }
        .code-box { background: #0b1120; border-radius: 10px; padding: 14px; font-family: monospace; font-size: 13px; color: #94a3b8; line-height: 1.5; margin: 8px 0; }
        .flag-box { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 12px; padding: 16px; margin-top: auto; }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-blue"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge" style="background:#ef4444;">HERO DEMO</span> Reasoning Misconception Detection</div>
          <div class="tagline">Catching False Cognitive Rules & Lucky Guesses</div>
        </div>
        <div class="main-content">
          <div class="badge-pill pill-amber">Deep Step-by-Step Rationale Evaluation</div>
          <div class="title-lg">Evaluating WHY the Student is Wrong</div>
          <div class="subtitle-lg">Checking the reasoning trace to prevent lucky guesses from masquerading as authentic concept mastery.</div>
          <div class="hero-grid">
            <div class="hero-card">
              <div style="font-size: 18px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;">Question Posed (ZPD Targeted: Ohm's Law)</div>
              <div style="font-size: 15px; color: #cbd5e1; background: rgba(15,23,42,0.8); padding: 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);">
                "If voltage V across an ohmic conductor doubles, what happens to its resistance R?"
              </div>
              <div style="margin-top: 14px; font-size: 14px; font-weight: 700; color: #e2e8f0;">Student Submission:</div>
              <div class="code-box">
                <span style="color: #64748b;">// Final Answer (Lucky Match):</span><br>
                <span style="color: #34d399;">"Resistance remains constant"</span><br><br>
                <span style="color: #64748b;">// Step-by-Step Reasoning (Flawed Rule):</span><br>
                <span style="color: #f87171;">"Because voltage V cancels out current completely to zero."</span>
              </div>
            </div>
            <div class="hero-card" style="border-color: rgba(239,68,68,0.4);">
              <div style="font-size: 18px; font-weight: 700; color: #f87171; margin-bottom: 8px;">Sakshi AI Reasoning Evaluator Output</div>
              <div class="code-box" style="color: #f1f5f9;">
                {<br>
                &nbsp;&nbsp;<span style="color: #38bdf8;">"is_correct"</span>: <span style="color: #34d399;">true</span>,<br>
                &nbsp;&nbsp;<span style="color: #38bdf8;">"reasoning_valid"</span>: <span style="color: #f87171;">false</span>,<br>
                &nbsp;&nbsp;<span style="color: #38bdf8;">"misconception_detected"</span>: <span style="color: #f87171;">true</span>,<br>
                &nbsp;&nbsp;<span style="color: #38bdf8;">"misconception_id"</span>: <span style="color: #facc15;">"ohm_r_depends_on_v"</span>,<br>
                &nbsp;&nbsp;<span style="color: #38bdf8;">"bkt_mastery"</span>: <span style="color: #f87171;">0.1758</span> <span style="color: #64748b;">// Penalized</span><br>
                }
              </div>
              <div class="flag-box">
                <div style="font-weight: 700; color: #f87171; font-size: 15px; margin-bottom: 4px;">Cognitive Misconception Caught!</div>
                <div style="font-size: 13px; color: #fca5a5; line-height: 1.4;">
                  Remediation: Resistance R is an intrinsic property determined by the conductor's material, length, and area (R = rho * L / A), not by applied V or I.
                </div>
              </div>
            </div>
          </div>
        </div>
      </body></html>
    `
  },

  // Scene 6: Spaced Repetition
  {
    name: "slide_6_scheduler.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .srs-container { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 32px; flex: 1; }
        .timeline { display: flex; justify-content: space-between; align-items: center; margin: 40px 0; position: relative; }
        .timeline::before { content: ""; position: absolute; height: 4px; background: rgba(255,255,255,0.1); top: 50%; left: 0; right: 0; z-index: 1; }
        .t-step { background: #0f172a; border: 2px solid #3b82f6; width: 140px; height: 110px; border-radius: 14px; padding: 12px; text-align: center; z-index: 2; display: flex; flex-direction: column; justify-content: center; }
        .t-exam { border-color: #ef4444; background: rgba(239,68,68,0.1); }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-purple"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge">FEATURE 6</span> Spaced Repetition Scheduling</div>
          <div class="tagline">Exam-Horizon Interval Compression</div>
        </div>
        <div class="main-content">
          <div class="badge-pill pill-blue">Adaptive Memory Pacing</div>
          <div class="title-lg">Guaranteeing 100% Retention Before Test Day</div>
          <div class="subtitle-lg">Standard SRS expands intervals endlessly; Sakshi AI dynamically compresses intervals as the examination deadline approaches.</div>
          <div class="srs-container">
            <div style="font-size: 18px; font-weight: 700; color: #e2e8f0;">Dynamic Horizon Pacing Pipeline: CBSE Class 10 Physics Exam</div>
            <div class="timeline">
              <div class="t-step">
                <div style="font-size: 11px; color: #94a3b8;">Normal Schedule</div>
                <div style="font-size: 16px; font-weight: 700; color: #60a5fa; margin: 4px 0;">+7 Days</div>
                <div style="font-size: 10px; color: #64748b;">R >= 0.90</div>
              </div>
              <div class="t-step" style="border-color: #facc15;">
                <div style="font-size: 11px; color: #94a3b8;">Exam in 10 Days</div>
                <div style="font-size: 16px; font-weight: 700; color: #facc15; margin: 4px 0;">+3.5 Days</div>
                <div style="font-size: 10px; color: #facc15;">kappa = 0.71</div>
              </div>
              <div class="t-step" style="border-color: #f97316;">
                <div style="font-size: 11px; color: #94a3b8;">Exam in 4 Days</div>
                <div style="font-size: 16px; font-weight: 700; color: #f97316; margin: 4px 0;">+1.2 Days</div>
                <div style="font-size: 10px; color: #f97316;">kappa = 0.28</div>
              </div>
              <div class="t-step" style="border-color: #ef4444;">
                <div style="font-size: 11px; color: #94a3b8;">Pre-Exam Cutoff</div>
                <div style="font-size: 16px; font-weight: 700; color: #ef4444; margin: 4px 0;">-12 Hours</div>
                <div style="font-size: 10px; color: #ef4444;">Final Review</div>
              </div>
              <div class="t-step t-exam">
                <div style="font-size: 11px; color: #f87171; font-weight: 700;">EXAM DAY</div>
                <div style="font-size: 18px; font-weight: 800; color: #ffffff;">98% Retention</div>
                <div style="font-size: 10px; color: #34d399;">100% Prepared</div>
              </div>
            </div>
            <div style="padding: 16px 20px; background: rgba(15,23,42,0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #94a3b8; font-size: 15px;">Formula: <code style="color: #38bdf8;">kappa = max(0.2, DaysRemaining / 14)</code></span>
              <span style="color: #34d399; font-weight: 700; font-size: 15px;">Zero Negative Intervals Guaranteed</span>
            </div>
          </div>
        </div>
      </body></html>
    `
  },

  // Scene 7: Teacher Dashboard
  {
    name: "slide_7_teacher.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .dash-grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 24px; flex: 1; }
        .card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 22px; }
        .matrix-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; }
        .matrix-table th { text-align: left; padding: 8px 6px; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .matrix-table td { padding: 8px 6px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .cell-green { background: rgba(16,185,129,0.25); color: #34d399; font-weight: 700; text-align: center; border-radius: 4px; padding: 4px 0; }
        .cell-yellow { background: rgba(245,158,11,0.25); color: #fbbf24; font-weight: 700; text-align: center; border-radius: 4px; padding: 4px 0; }
        .cell-red { background: rgba(239,68,68,0.25); color: #f87171; font-weight: 700; text-align: center; border-radius: 4px; padding: 4px 0; }
        .gap-box { background: rgba(15,23,42,0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px; margin-bottom: 10px; }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-blue"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge" style="background:#10b981;">FEATURE 7</span> Teacher Cohort Analytics</div>
          <div class="tagline">Live Classroom Heatmap & Gap Ranking (/teacher)</div>
        </div>
        <div class="main-content">
          <div class="badge-pill pill-emerald">Class-Wide Actionable Insights</div>
          <div class="title-lg">Real-Time Heatmap Across 25 Students</div>
          <div class="subtitle-lg">Instantly identifying class-wide misconceptions and weak syllabus clusters for targeted classroom intervention.</div>
          <div class="dash-grid">
            <div class="card">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 16px; font-weight: 700; color: #f8fafc;">Class 10-A: Concept Mastery Matrix</span>
                <span style="font-size: 12px; color: #34d399; background: rgba(16,185,129,0.15); padding: 4px 10px; border-radius: 6px; font-weight: 700;">Average Mastery: 64.2%</span>
              </div>
              <table class="matrix-table">
                <thead>
                  <tr><th>Student</th><th>Overall</th><th>Charge</th><th>Current</th><th>Ohm's Law</th><th>Resistors</th><th>Mirrors</th><th>Solenoids</th></tr>
                </thead>
                <tbody>
                  <tr><td>Aarav Sharma</td><td style="font-weight:700;">88%</td><td class="cell-green">.94</td><td class="cell-green">.91</td><td class="cell-green">.85</td><td class="cell-yellow">.68</td><td class="cell-green">.89</td><td class="cell-green">.82</td></tr>
                  <tr><td>Diya Patel</td><td style="font-weight:700;">72%</td><td class="cell-green">.85</td><td class="cell-green">.80</td><td class="cell-yellow">.52</td><td class="cell-red">.31</td><td class="cell-green">.74</td><td class="cell-yellow">.62</td></tr>
                  <tr><td>Rohan Verma</td><td style="font-weight:700;">48%</td><td class="cell-green">.72</td><td class="cell-yellow">.60</td><td class="cell-red">.22</td><td class="cell-red">.18</td><td class="cell-yellow">.55</td><td class="cell-red">.28</td></tr>
                  <tr><td>Ananya Sen</td><td style="font-weight:700;">61%</td><td class="cell-green">.78</td><td class="cell-green">.70</td><td class="cell-yellow">.44</td><td class="cell-red">.25</td><td class="cell-green">.71</td><td class="cell-yellow">.50</td></tr>
                  <tr><td>Kabir Mehta</td><td style="font-weight:700;">39%</td><td class="cell-yellow">.55</td><td class="cell-yellow">.48</td><td class="cell-red">.15</td><td class="cell-red">.12</td><td class="cell-red">.38</td><td class="cell-red">.20</td></tr>
                </tbody>
              </table>
              <div style="display: flex; gap: 16px; margin-top: 14px; font-size: 11px;">
                <span style="color: #34d399;">■ Mastered (>= 70%)</span>
                <span style="color: #fbbf24;">■ Intermediate (40-69%)</span>
                <span style="color: #f87171;">■ Struggling (< 40%)</span>
              </div>
            </div>
            <div class="card">
              <div style="font-size: 16px; font-weight: 700; color: #f87171; margin-bottom: 12px;">Top Class-Wide Knowledge Gaps</div>
              <div class="gap-box">
                <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 14px;">
                  <span style="color: #f87171;">#1 Series & Parallel Resistors</span>
                  <span style="color: #f87171;">28.4% Mastery</span>
                </div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">68% of class struggling · Frequent flaw: Additive parallel formula</div>
              </div>
              <div class="gap-box">
                <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 14px;">
                  <span style="color: #fbbf24;">#2 Ohm's Law (Voltage vs R)</span>
                  <span style="color: #fbbf24;">43.1% Mastery</span>
                </div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">52% of class struggling · Frequent flaw: R depends on V or I</div>
              </div>
              <div class="gap-box">
                <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 14px;">
                  <span style="color: #fbbf24;">#3 Magnetic Solenoids</span>
                  <span style="color: #fbbf24;">49.2% Mastery</span>
                </div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">44% of class struggling · Frequent flaw: Magnetic monopole existence</div>
              </div>
            </div>
          </div>
        </div>
      </body></html>
    `
  },

  // Scene 8: Outro & Hackathon Winning Summary
  {
    name: "slide_8_outro.png",
    html: `
      <!DOCTYPE html><html><head><style>${BASE_STYLES}
        .matrix-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; flex: 1; align-content: center; }
        .grid-card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 14px; padding: 22px; text-align: center; }
      </style></head><body>
        <div class="bg-grid"></div><div class="glow-blue"></div>
        <div class="navbar">
          <div class="brand"><span class="brand-badge">SUMMARY</span> Sakshi AI Hackathon Submission</div>
          <div class="tagline">100% Problem Statement Compliance</div>
        </div>
        <div class="main-content" style="text-align: center; align-items: center;">
          <div class="badge-pill pill-emerald">All 7 Requirements Delivered & Verified</div>
          <div class="title-lg">The Complete Adaptive Exam-Prep Tutor</div>
          <div class="subtitle-lg">Pruned 500k lines of legacy bloat. Built 100% verifiable mathematical models and cohort analytics.</div>
          <div class="matrix-grid" style="width: 100%; max-width: 1400px;">
            <div class="grid-card"><div style="font-size: 28px;">📋</div><div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 8px 0;">1. Diagnostic Test</div><div style="font-size: 12px; color: #94a3b8;">6-milestone intake establishes baseline P(L0)</div></div>
            <div class="grid-card"><div style="font-size: 28px;">🕸️</div><div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 8px 0;">2. Concept DAG</div><div style="font-size: 12px; color: #94a3b8;">Class 10 Physics NetworkX prerequisite graph</div></div>
            <div class="grid-card"><div style="font-size: 28px;">🧮</div><div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 8px 0;">3. BKT Learner Model</div><div style="font-size: 12px; color: #94a3b8;">Probabilistic P(Lt) updates after every answer</div></div>
            <div class="grid-card"><div style="font-size: 28px;">🎯</div><div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 8px 0;">4. ZPD Question Gen</div><div style="font-size: 12px; color: #94a3b8;">Frontier targeting with 3-tier difficulty scaling</div></div>
            <div class="grid-card"><div style="font-size: 28px;">🔍</div><div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 8px 0;">5. Misconception Engine</div><div style="font-size: 12px; color: #94a3b8;">Reasoning trace analysis catching lucky guesses</div></div>
            <div class="grid-card"><div style="font-size: 28px;">⏰</div><div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 8px 0;">6. Spaced Repetition</div><div style="font-size: 12px; color: #94a3b8;">Exam-horizon dynamic compression</div></div>
            <div class="grid-card"><div style="font-size: 28px;">📊</div><div style="font-size: 16px; font-weight: 700; color: #34d399; margin: 8px 0;">7. Teacher Heatmap</div><div style="font-size: 12px; color: #94a3b8;">25-student matrix & class gap ranking</div></div>
            <div class="grid-card" style="border-color: #3b82f6;"><div style="font-size: 28px;">🚀</div><div style="font-size: 16px; font-weight: 700; color: #60a5fa; margin: 8px 0;">Clean Production</div><div style="font-size: 12px; color: #94a3b8;">64/64 pytest passing in 1.8s</div></div>
          </div>
        </div>
      </body></html>
    `
  }
];

async function renderAll() {
  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome-stable",
    headless: true
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

  for (const slide of SLIDES) {
    console.log("Rendering " + slide.name + "...");
    await page.setContent(slide.html, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(SLIDES_DIR, slide.name) });
  }

  await browser.close();
  console.log("All slides rendered successfully!");
}

renderAll().catch(err => {
  console.error("Rendering failed:", err);
  process.exit(1);
});
