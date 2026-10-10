import type { HTMLAttributes } from "react";
import { combinarClases } from "../../lib/utilidades";

export function Panel({ className, ...propiedades }: HTMLAttributes<HTMLElement>) {
  return (
    <section
      className={combinarClases(
        "rounded-md border border-borde bg-panel shadow-atlas",
        className,
      )}
      {...propiedades}
    />
  );
}

export function EncabezadoPanel({
  className,
  ...propiedades
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={combinarClases(
        "flex min-h-12 items-center justify-between border-b border-borde px-4",
        className,
      )}
      {...propiedades}
    />
  );
}

export function CuerpoPanel({
  className,
  ...propiedades
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={combinarClases("p-4", className)} {...propiedades} />;
}
