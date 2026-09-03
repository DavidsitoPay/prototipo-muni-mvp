import type { NistAssessmentItem, NistQuestion, NistSummary } from "../types";
import { apiClient } from "./client";

export async function fetchNistQuestions(): Promise<NistQuestion[]> {
  const { data } = await apiClient.get<NistQuestion[]>("/nist/questions");
  return data;
}

export async function fetchNistAssessment(): Promise<NistAssessmentItem[]> {
  const { data } = await apiClient.get<NistAssessmentItem[]>("/nist/assessment");
  return data;
}

export async function updateNistAssessment(
  answers: { question_code: string; score: number }[]
): Promise<NistAssessmentItem[]> {
  const { data } = await apiClient.put<NistAssessmentItem[]>("/nist/assessment", answers);
  return data;
}

export async function fetchNistSummary(): Promise<NistSummary> {
  const { data } = await apiClient.get<NistSummary>("/nist/summary");
  return data;
}
