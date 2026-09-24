import { apiGet, apiPost, apiPostJson, apiUploadFile } from "./client";
import type {
  CheckConfig,
  CheckOut,
  DatasetSummary,
  HistoryEntry,
  RunResponse,
  SchemaResponse,
} from "./types";

export function uploadDataset(file: File): Promise<DatasetSummary> {
  return apiUploadFile<DatasetSummary>("/datasets/upload", file);
}

export function listDatasets(): Promise<DatasetSummary[]> {
  return apiGet<DatasetSummary[]>("/datasets");
}

export function getDataset(datasetId: number): Promise<DatasetSummary> {
  return apiGet<DatasetSummary>(`/datasets/${datasetId}`);
}

export function getSchema(datasetId: number): Promise<SchemaResponse> {
  return apiGet<SchemaResponse>(`/datasets/${datasetId}/schema`);
}

export function suggestChecks(datasetId: number): Promise<CheckConfig[]> {
  return apiPost<CheckConfig[]>(`/datasets/${datasetId}/suggest-checks`);
}

export function getChecks(datasetId: number): Promise<CheckOut[]> {
  return apiGet<CheckOut[]>(`/datasets/${datasetId}/checks`);
}

export function saveChecks(datasetId: number, checks: CheckConfig[]): Promise<CheckOut[]> {
  return apiPostJson<CheckOut[]>(`/datasets/${datasetId}/checks`, checks);
}

export function runChecks(datasetId: number): Promise<RunResponse> {
  return apiPost<RunResponse>(`/datasets/${datasetId}/run-checks`);
}

export function getHistory(datasetId: number): Promise<HistoryEntry[]> {
  return apiGet<HistoryEntry[]>(`/datasets/${datasetId}/history`);
}
