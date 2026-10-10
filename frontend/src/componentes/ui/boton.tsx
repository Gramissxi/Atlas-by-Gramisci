import type { ButtonHTMLAttributes } from "react";
import { combinarClases } from "../../lib/utilidades";

type VarianteBoton = "primario" | "secundario" | "fantasma" | "peligro";
type TamanoBoton = "normal" | "chico" | "icono";

type PropiedadesBoton = ButtonHTMLAttributes<HTMLButtonElement> & {
  variante?: VarianteBoton;
  tamano?: TamanoBoton;
};

const variantes: Record<VarianteBoton, string> = {
  primario: "bg-primario text-primarioTexto hover:bg-[#114d55]",
  secundario: "bg-secundario text-white hover:bg-[#38664b]",
  fantasma: "bg-transparent text-texto hover:bg-[#e7ede8]",
  peligro: "bg-[#b42318] text-white hover:bg-[#981b14]",
};

const tamanos: Record<TamanoBoton, string> = {
  normal: "h-10 px-4 text-sm",
  chico: "h-8 px-3 text-xs",
  icono: "h-9 w-9 p-0",
};

export function Boton({
  className,
  variante = "primario",
  tamano = "normal",
  type = "button",
  ...propiedades
}: PropiedadesBoton) {
  return (
    <button
      type={type}
      className={combinarClases(
        "inline-flex items-center justify-center gap-2 rounded-md border border-transparent font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-[#0f5f66] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        variantes[variante],
        tamanos[tamano],
        className,
      )}
      {...propiedades}
    />
  );
}
