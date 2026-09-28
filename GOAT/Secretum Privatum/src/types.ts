export type AssetCategory = "MasterClass" | "Study" | "Memory" | "Media";
export type AssetStatus = "Staged" | "Processed" | "Encrypted";

export interface AssetBlock {
  id: string;
  title: string;
  category: AssetCategory;
  fileType: string;
  size: string;
  parsedSummary: string;
  status: AssetStatus;
  sourcePath?: string;
  checksum?: string;
}

export interface OrganizerManifest {
  name: string;
  description: string;
  image: string;
  attributes: Array<{ trait_type: string; value: string }>;
  properties: {
    encrypted_vault_data: {
      storage_uri: string;
      mime_type: string;
      checksum: string;
      initialization_vector_hex: string;
    };
  };
}
