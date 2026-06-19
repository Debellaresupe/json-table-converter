export type CandidateRoot = {
  path: string;
  kind: string;
  score: number;
  length?: number;
  object_ratio?: number;
  primitive_ratio?: number;
  columns_preview: string[];
};

export type AnalyzeResponse = {
  summary: Record<string, unknown>;
  candidate_roots: CandidateRoot[];
  recommended_root_path: string;
  recommended_array_mode: "explode" | "join" | "json-stringify";
  recommended_null_mode: "empty" | "null";
  warnings: string[];
};

export type TransformOptions = {
  root_path?: string;
  array_mode: "explode" | "join" | "json-stringify";
  primitive_array_mode: "join" | "index" | "json-stringify";
  null_mode: "empty" | "null";
  join_delimiter: string;
  preview_limit?: number;
};

export type TransformResponse = {
  columns: { field: string; headerName: string; type: string }[];
  rows: Record<string, unknown>[];
  meta: {
    row_count: number;
    column_count: number;
    returned_rows: number;
    root_path: string;
    array_mode: string;
    primitive_array_mode: string;
    truncated: boolean;
    warnings: string[];
  };
};

export type ReferencePreviewResponse = {
  header_rows: (string | number | null)[][];
  rows: unknown[][];
  meta: {
    row_count: number;
    column_count: number;
    returned_rows: number;
    truncated: boolean;
  };
};
