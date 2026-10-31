#!/usr/bin/env bash
set -e

OUT_DIR="/home/blank/sakshi-ai-hackathon/demo_production/audio"
mkdir -p "$OUT_DIR"
VOICE="en-US-ChristopherNeural"

echo "Generating Scene 1..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "Most AI tutors today are just chat bots. They answer questions, but have zero idea what a student actually understands. Welcome to Sakshi AI: an adaptive, syllabus-grounded exam prep tutor powered by an authentic Bayesian learner model." \
  --write-media "$OUT_DIR/scene_1_hook.mp3"

echo "Generating Scene 2..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "We start with an adaptive diagnostic test. Covering core milestones across the syllabus, it assesses both final answers and step-by-step reasoning to calculate the student's initial mastery baseline, initializing our Bayesian Knowledge Tracing engine." \
  --write-media "$OUT_DIR/scene_2_diagnostic.mp3"

echo "Generating Scene 3..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "At the core is our syllabus concept graph. For Class 10 Physics, we structured units like Light, Electricity, and Magnetism into a strict Directed Acyclic Graph, verified by NetworkX to guarantee prerequisite order and unlock advanced concepts only when fundamentals are mastered." \
  --write-media "$OUT_DIR/scene_3_dag.mp3"

echo "Generating Scene 4..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "Instead of crude moving averages, Sakshi AI implements authentic Bayesian Knowledge Tracing. With calibrated slip, guess, and transition parameters, student mastery updates mathematically after every single interaction, tracking true latent understanding." \
  --write-media "$OUT_DIR/scene_4_bkt.mp3"

echo "Generating Scene 5..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "Here is where Sakshi AI shines: misconception detection from student reasoning. Even when a student makes a lucky guess, our evaluator analyzes their step-by-step derivation to catch flawed cognitive rules, like confusing resistance with voltage dependence, providing instant targeted remediation." \
  --write-media "$OUT_DIR/scene_5_misconception.mp3"

echo "Generating Scene 6..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "To ensure exam readiness, our spaced repetition scheduler features exam-horizon compression. As test day nears, intervals dynamically tighten, guaranteeing that unstable concepts are reinforced before the exam." \
  --write-media "$OUT_DIR/scene_6_scheduler.mp3"

echo "Generating Scene 7..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "For educators, Sakshi AI delivers actionable cohort intelligence. The teacher dashboard features a live mastery heatmap across 25 students, ranks class-wide curriculum gaps, and breaks down the most common misconceptions across the classroom." \
  --write-media "$OUT_DIR/scene_7_teacher.mp3"

echo "Generating Scene 8..."
uv tool run edge-tts --voice "$VOICE" --rate "+4%" \
  --text "Diagnostic testing. Syllabus DAG. BKT learner model. ZPD targeted generation. Reasoning misconception detection. Exam-paced spaced repetition. And a class-wide teacher dashboard. Sakshi AI: the future of intelligent exam preparation." \
  --write-media "$OUT_DIR/scene_8_outro.mp3"

echo "All audio tracks generated successfully!"
ls -la "$OUT_DIR"
