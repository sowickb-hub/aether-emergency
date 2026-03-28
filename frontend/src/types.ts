/** Shared TypeScript types for Aether Emergency */

export type HazardLevel = 'RED' | 'ORANGE' | 'YELLOW';
export type PrimaryNeed = 'MEDICAL' | 'FIRE' | 'RESCUE' | 'HAZMAT' | 'EVACUATION';
export type EMSCode = 'P1' | 'P2' | 'P3';

export interface DispatchResult {
  hazard_level: HazardLevel;
  hazard_justification: string;
  primary_need: PrimaryNeed;
  secondary_needs: string[];
  location_details: string;
  casualties_reported: string;
  imminent_threats: string[];
  recommended_units: string[];
  first_aid_protocols: string[];
  ems_priority_code: EMSCode;
  estimated_response_time_min: number;
  narrative_summary: string;
  confidence_score: number;
  image_observations: string;
}

export interface ImagePayload {
  mime_type: string;
  data: string; // base64
}

export interface AnalyzeRequest {
  text: string;
  images: ImagePayload[];
}
