// frontend/src/api/profile.ts
//
// Profile API — one function per call of the profiles API
// ─────────────────────────────────────────────────────────────────────────────
// Names each route of the profiles API once, with the shape of what it
// receives and returns, and carries the rules of the files, the same as the
// backend's (backend/profiles/validators.py): a file is checked here before
// it is sent, in the language of the interface; the backend remains the
// safety net.

import { getJson, send, type Answer } from "./http";

// ── Shapes ────────────────────────────────────────────────────────────

// Fields shared by the two profiles. The first three are those of the
// account behind the profile: the names are changed with it, the address
// only through its own confirmation (see api/account.ts). A file field
// holds the URL of the file (/api/files/...), or null when there is none.
type Contact = {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: string;
  postal_code: string;
  city: string;
  country: string;
  updated_at: string;
};

export type ProfileDocument = {
  id: number;
  name: string;
  file: string;
  uploaded_at: string;
};

export type CandidateProfile = Contact & {
  photo: string | null;
  cv: string | null;
  documents: ProfileDocument[];
};

export type EmployerProfile = Contact & {
  company_name: string;
  company_address: string;
  company_postal_code: string;
  company_city: string;
  company_country: string;
  company_phone: string;
  logo: string | null;
};

export type Profile = CandidateProfile | EmployerProfile;

// The text fields a page may change: everything but the address, the files
// and the dates
export type ProfileFields = Partial<
  Omit<CandidateProfile, "email" | "photo" | "cv" | "documents" | "updated_at"> &
    Omit<EmployerProfile, "email" | "logo" | "updated_at">
>;

// The file fields of the profile, by their name in the API
export type ProfileFileField = "photo" | "cv" | "logo";

// ── Rules of the files ────────────────────────────────────────────────

// Largest file accepted, in bytes (5 MB, as the backend)
export const MAX_FILE_SIZE = 5 * 1024 * 1024;

// How many further documents a candidate may keep (as the backend)
export const MAX_DOCUMENTS = 10;

// Extensions accepted for each kind of file, lower case, with the dot: the
// form the "accept" attribute of a file input expects
const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"];
const DOCUMENT_EXTENSIONS = [".pdf", ".docx"];

export const ACCEPTED: Record<ProfileFileField | "document", string[]> = {
  photo: IMAGE_EXTENSIONS,
  logo: IMAGE_EXTENSIONS,
  cv: DOCUMENT_EXTENSIONS,
  document: [...DOCUMENT_EXTENSIONS, ...IMAGE_EXTENSIONS],
};

// Why a file cannot be sent, or null when it can. The caller turns the code
// into a message in the language of the interface.
export function fileProblem(
  file: File,
  kind: keyof typeof ACCEPTED,
): "tooBig" | "wrongType" | null {
  if (file.size > MAX_FILE_SIZE) return "tooBig";
  const name = file.name.toLowerCase();
  if (!ACCEPTED[kind].some((extension) => name.endsWith(extension))) {
    return "wrongType";
  }
  return null;
}

// ── Calls ─────────────────────────────────────────────────────────────

const PROFILE = "/api/profile/";

// The profile of the logged-in user, created empty if needed. The shape
// depends on the role, which the caller knows from the session
export function getProfile<T extends Profile>(): Promise<T> {
  return getJson<T>(PROFILE);
}

// Changes the text fields sent; the others keep their value
export function updateProfile<T extends Profile>(
  fields: ProfileFields,
): Promise<Answer<T>> {
  return send<T>("PATCH", PROFILE, fields);
}

// Stores one file of the profile in the place of the current one
export function uploadFile<T extends Profile>(
  field: ProfileFileField,
  file: File,
): Promise<Answer<T>> {
  const form = new FormData();
  form.append(field, file);
  return send<T>("PATCH", PROFILE, form);
}

// Removes one file of the profile; answers the profile without it
export function removeFile<T extends Profile>(
  field: ProfileFileField,
): Promise<Answer<T>> {
  return send<T>("DELETE", `${PROFILE}${field}/`);
}

// Adds a further document of a candidate; 201 with the document
export function addDocument(file: File): Promise<Answer<ProfileDocument>> {
  const form = new FormData();
  form.append("file", file);
  return send<ProfileDocument>("POST", `${PROFILE}documents/`, form);
}

// Removes one document of the candidate; 204
export function removeDocument(id: number): Promise<Answer<null>> {
  return send<null>("DELETE", `${PROFILE}documents/${id}/`);
}
