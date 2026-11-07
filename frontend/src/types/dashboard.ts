export interface ColumnMeta {
  name: string;
  dtype: 'numeric' | 'datetime' | 'categorical' | 'boolean';
  null_count: number;
  unique_count: number;
  sample_values: any[];
  min_val?: any;
  max_val?: any;
  mean_val?: number;
}

export interface DatasetMeta {
  filename: string;
  file_type: string;
  total_rows: number;
  total_columns: number;
  columns: ColumnMeta[];
  sheet_names: string[];
  active_sheet?: string;
  duplicate_count: number;
  preview_rows: Record<string, any>[];
}

export interface ChartConfig {
  id: string;
  title: string;
  chart_type: string;
  x_col?: string;
  y_col?: string;
  color_col?: string;
  agg?: string;
  top_n?: number;
  sort_order?: string;
  time_group?: string;
  filter_conditions?: any[];
  plotly_spec: {
    data?: any[];
    layout?: any;
  };
  width?: 'half' | 'full';
  created_at?: string;
}

export interface KPIConfig {
  id: string;
  title: string;
  metric_col: string;
  agg: string;
  value: number;
  formatted_value: string;
  prefix?: string;
  suffix?: string;
}

export interface FilterItem {
  id: string;
  column: string;
  filter_type: string;
  options: string[];
  current_value?: any;
  min_val?: number;
  max_val?: number;
}

export interface ClarificationQuestion {
  question: string;
  parameter_needed: string;
  options: string[];
  original_intent: string;
  partial_entities: Record<string, any>;
}

export interface DashboardState {
  project_name: string;
  session_id: string;
  dataset_meta?: DatasetMeta;
  charts: ChartConfig[];
  kpis: KPIConfig[];
  filters: FilterItem[];
  selected_chart_id?: string;
  last_modified_chart_id?: string;
  command_history: {
    user_command: string;
    system_response: string;
    intent: string;
    affected_id?: string;
  }[];
}

export interface CommandResponse {
  success: boolean;
  detected_language: string;
  intent: string;
  message: string;
  entities: Record<string, any>;
  requires_clarification: boolean;
  clarification?: ClarificationQuestion;
  updated_state?: DashboardState;
  error_details?: string;
}
