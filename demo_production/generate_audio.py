import asyncio
import os
import edge_tts

SCENES = {
    "scene_1_hook": (
        "Most AI tutors today are just chat bots. They answer questions, but have zero idea what a student actually understands. "
        "Welcome to Sakshi AI: an adaptive, syllabus-grounded exam prep tutor powered by an authentic Bayesian learner model."
    ),
    "scene_2_diagnostic": (
        "We start with an adaptive diagnostic test. Covering core milestones across the syllabus, it assesses both final answers and step-by-step reasoning "
        "to calculate the student's initial mastery baseline, initializing our Bayesian Knowledge Tracing engine."
    ),
    "scene_3_dag": (
        "At the core is our syllabus concept graph. For Class 10 Physics, we structured units like Light, Electricity, and Magnetism into a strict "
        "Directed Acyclic Graph, verified by NetworkX to guarantee prerequisite order and unlock advanced concepts only when fundamentals are mastered."
    ),
    "scene_4_bkt": (
        "Instead of crude moving averages, Sakshi AI implements authentic Bayesian Knowledge Tracing. With calibrated slip, guess, and transition parameters, "
        "student mastery updates mathematically after every single interaction, tracking true latent understanding."
    ),
    "scene_5_misconception": (
        "Here is where Sakshi AI shines: misconception detection from student reasoning. Even when a student makes a lucky guess, our evaluator analyzes "
        "their step-by-step derivation to catch flawed cognitive rules, like confusing resistance with voltage dependence, providing instant targeted remediation."
    ),
    "scene_6_scheduler": (
        "To ensure exam readiness, our spaced repetition scheduler features exam-horizon compression. As test day nears, intervals dynamically tighten, "
        "guaranteeing that unstable concepts are reinforced before the exam."
    ),
    "scene_7_teacher": (
        "For educators, Sakshi AI delivers actionable cohort intelligence. The teacher dashboard features a live mastery heatmap across 25 students, "
        "ranks class-wide curriculum gaps, and breaks down the most common misconceptions across the classroom."
    ),
    "scene_8_outro": (
        "Diagnostic testing. Syllabus DAG. BKT learner model. ZPD targeted generation. Reasoning misconception detection. Exam-paced spaced repetition. "
        "And a class-wide teacher dashboard. Sakshi AI: the future of intelligent exam preparation."
    ),
}

VOICE = "en-US-ChristopherNeural"

async def generate():
    out_dir = "/home/blank/sakshi-ai-hackathon/demo_production/audio"
    os.makedirs(out_dir, exist_ok=True)
    for name, text in SCENES.items():
        out_path = os.path.join(out_dir, f"{name}.mp3")
        print(f"Generating {out_path}...")
        communicate = edge_tts.Communicate(text, VOICE, rate="+4%")
        await communicate.save(out_path)
        print(f"Done: {out_path}")

if __name__ == "__main__":
    asyncio.run(generate())
