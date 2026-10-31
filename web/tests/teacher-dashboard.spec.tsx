import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { test, expect } from 'vitest';
import TeacherDashboardPage from '@/app/(workspace)/teacher/page';
import DiagnosticPage from '@/app/(workspace)/diagnostic/page';

test('renders teacher dashboard with class gap alert and heatmap', async () => {
  render(<TeacherDashboardPage />);
  expect(await screen.findByText(/Class-Wide Knowledge Gaps/i)).toBeInTheDocument();
  expect(await screen.findByText(/Concept Mastery Heatmap/i)).toBeInTheDocument();
  expect(await screen.findByText(/Top Reasoning Misconceptions/i)).toBeInTheDocument();

  // Verify dashboard header and cohort selector
  expect(screen.getByText(/Teacher Analytics Dashboard: Class 10 Physics/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Cohort:/i)).toBeInTheDocument();

  // Verify top gaps and high priority badges
  expect(screen.getByText(/Series & Parallel Resistance/i)).toBeInTheDocument();
  expect(screen.getAllByText(/High Priority Gap/i).length).toBeGreaterThan(0);

  // Verify heatmap students and chapters
  expect(screen.getByText('Aarav Sharma')).toBeInTheDocument();
  expect(screen.getAllByText('Light').length).toBeGreaterThan(0);
  expect(screen.getAllByText('Electricity').length).toBeGreaterThan(0);
  expect(screen.getAllByText('Magnetism').length).toBeGreaterThan(0);

  // Verify misconceptions & remedial strategy
  expect(screen.getAllByText(/Resistance depends on Voltage or Current/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/Remedial Teaching Strategy/i).length).toBeGreaterThan(0);
});

test('renders diagnostic assessment intake screen and submits calibrated answers', async () => {
  render(<DiagnosticPage />);

  // Verify title and milestone prompt
  expect(screen.getByText(/Class 10 Physics Diagnostic Assessment/i)).toBeInTheDocument();
  expect(screen.getByText(/According to the laws of reflection/i)).toBeInTheDocument();

  // Verify answer input and step-by-step reasoning textarea
  const answerInput = screen.getByLabelText(/Your Answer/i);
  const reasoningInput = screen.getByLabelText(/Step-by-Step Reasoning/i);
  expect(answerInput).toBeInTheDocument();
  expect(reasoningInput).toBeInTheDocument();

  // Fill in answer and reasoning for Q1
  fireEvent.change(answerInput, { target: { value: '45 degrees' } });
  fireEvent.change(reasoningInput, { target: { value: 'Angle of incidence equals angle of reflection (i = r)' } });

  // Submit assessment
  const submitBtn = screen.getByRole('button', { name: /Submit Assessment/i });
  fireEvent.click(submitBtn);

  // Verify calibration completion radar / summary
  expect(await screen.findByText(/Diagnostic Calibration Complete/i)).toBeInTheDocument();
  expect(screen.getByText(/Diagnostic Score/i)).toBeInTheDocument();
  expect(screen.getByText(/Initial Concept Mastery Radar/i)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /Continue to Learning Path/i })).toBeInTheDocument();
});
