// Loaded directly by Claude Code. Check with: claude plugin validate <plugin> --strict --json
const TASKS = Object.freeze([
  Object.freeze({ id: "T-1", state: "open" }),
  Object.freeze({ id: "T-2", state: "closed" }),
  Object.freeze({ id: "T-3", state: "open" }),
]);
const HELP = "Use /task-view for the native view, or /task-view all, /task-view open, /task-view closed, /task-view help for text.";
function rows(filter: string) {
  return TASKS.filter(task => filter === "all" || task.state === filter)
    .map(task => `${task.id}: ${task.state}`).join("\n");
}

export function register(on) {
  let filter = "all";
  on("session.start", async ($, event, next) => {
    filter = "all";
    await $.command.register({ name: "task-view", description: "Inspect local tasks", argumentHint: "all | open | closed | help" });
    return next(event);
  });
  // Registration uses name; the command event and its matcher use command.
  on("command.run", { command: "task-view" }, async ($, event) => {
    const argument = typeof event.args === "string" ? event.args.trim().toLowerCase() : "";
    if (argument === "help") return { text: HELP };
    if (["all", "open", "closed"].includes(argument)) return { text: rows(argument) };
    if (argument) return { text: `Unknown task view. ${HELP}` };
    filter = "all";
    try {
      const placement = await $.ui.open({ id: "task-view", title: "Task view" });
      if (placement?.isPlaced) return {};
    } catch {
      // A denied or unavailable pane still has a useful deterministic text route.
    }
    return { text: `The native pane is unavailable.\n${rows("all")}\n${HELP}` };
  });
  on("ui.render", { component: "Pane" }, ($, event, next) => {
    if (event.requestId !== "task-view" || !["terminal", "desktop"].includes(event.surface)) return next(event);
    const { Box, Text, Select, Button } = $.ui.resolve(event);
    return Box({ flexDirection: "column", children: [
      Text({ children: "Task view — read-only" }),
      Text({ children: "Choose a view; results update immediately." }),
      Select({ key: "view", value: filter, autoFocus: true,
        options: [{ value: "all", label: "All tasks" }, { value: "open", label: "Open" }, { value: "closed", label: "Closed" }],
        onSelect: value => {
          if (!["all", "open", "closed"].includes(value)) return;
          filter = value;
          $.ui.invalidate("ui.render");
        },
      }),
      Text({ children: rows(filter) }),
      Button({ key: "cancel", children: "Close", onPress: async () => { await $.ui.close({ id: "task-view" }); } }),
    ] });
  });
}
