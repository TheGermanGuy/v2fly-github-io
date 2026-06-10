import fs from "fs";
import path from "path";
import type Anthropic from "@anthropic-ai/sdk";

const MEDIA_TYPES: Record<string, "image/png" | "image/jpeg" | "image/webp" | "image/gif"> = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
};

export function loadImageBlocks(paths: string[]): Anthropic.ImageBlockParam[] {
  return paths.map((p) => {
    const mediaType = MEDIA_TYPES[path.extname(p).toLowerCase()];
    if (!mediaType) {
      throw new Error(`Nicht unterstütztes Bildformat: ${p} (erlaubt: png, jpg, webp, gif)`);
    }
    if (!fs.existsSync(p)) {
      throw new Error(`Datei nicht gefunden: ${p}`);
    }
    return {
      type: "image",
      source: {
        type: "base64",
        media_type: mediaType,
        data: fs.readFileSync(p).toString("base64"),
      },
    };
  });
}
