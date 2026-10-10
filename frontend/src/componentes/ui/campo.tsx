import type { InputHTMLAttributes } from "react";
import { combinarClases } from "../../lib/utilidades";

export function Campo({ className, ...propiedades }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={combinarClases(
        "h-11 w-full rounded-md border border-borde bg-white px-3 text-sm text-texto outline-none transition-colors placeholder:text-[#66736b] focus:border-[#0f5f66] focus:ring-2 focus:ring-[#c8dbd9]",
        className,
      )}
      {...propiedades}
    />
  );
}
