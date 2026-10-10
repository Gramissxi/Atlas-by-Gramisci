import type { HTMLAttributes } from "react";
import { combinarClases } from "../../lib/utilidades";

type VarianteInsignia = "local" | "internet" | "neutro" | "alerta";

type PropiedadesInsignia = HTMLAttributes<HTMLSpanElement> & {
  variante?: VarianteInsignia;
};

const variantes: Record<VarianteInsignia, string> = {
  local: "border-[#6b7f55] bg-[#edf4e7] text-[#29441f]",
  internet: "border-[#67889b] bg-[#e8f1f4] text-[#193f4d]",
  neutro: "border-borde bg-[#f3f4f2] text-[#475049]",
  alerta: "border-[#d6a743] bg-[#fff4d8] text-[#6d4c00]",
};

export function Insignia({
  className,
  variante = "neutro",
  ...propiedades
}: PropiedadesInsignia) {
  return (
    <span
      className={combinarClases(
        "inline-flex h-7 items-center rounded-md border px-2 text-xs font-semibold",
        variantes[variante],
        className,
      )}
      {...propiedades}
    />
  );
}
