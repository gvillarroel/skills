// Run with: pi --extension ./view-mode.ts
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  let mode = "compact";
  pi.registerCommand("view-mode", {
    description: "Choose compact or detailed output; /view-mode [compact|detailed]",
    handler: async (args, ctx) => {
      const choices = ["compact", "detailed"];
      let next = args.trim();
      if (!next && ctx.hasUI) {
        next = (await ctx.ui.select(`Output: ${mode}`, choices, { timeout: 30000 })) ?? "";
        if (!next) return;
      }
      const valid = choices.includes(next);
      const message = valid ? `Output mode: ${next}`
        : "Use /view-mode compact or /view-mode detailed.";
      if (valid) mode = next;
      if (ctx.hasUI) ctx.ui.notify(message, valid ? "info" : "warning");
      else pi.sendMessage({ customType: "view-mode", content: message, display: true },
        { triggerTurn: false });
    },
  });
}
