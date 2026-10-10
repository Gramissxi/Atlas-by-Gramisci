import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function combinarClases(...clases: ClassValue[]) {
  return twMerge(clsx(clases));
}
