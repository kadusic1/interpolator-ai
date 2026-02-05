export interface AgentQuery {
  user_input: string;
  image_base64?: string | null;
  method: "lagrange" | "newton_forward" | "newton_backward" | "direct" | "hermite";
}

export interface InterpolationResponse {
  results: number[] | null;
  polynomial_degree: number;
  coefficients: number[];
}

export interface InterpolationResponseWithMetadata extends InterpolationResponse {
  points: [number, number][];
  method: string;
  image_base64: string;
  formatted_results: [number, number][] | null;
}

export type MessageType = "user" | "ai";

export interface Message {
  id: string;
  type: MessageType;
  content: string | InterpolationResponseWithMetadata[];
  image?: string | null;
  timestamp: number;
}
