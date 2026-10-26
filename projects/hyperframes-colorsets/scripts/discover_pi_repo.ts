#!/usr/bin/env -S node --experimental-strip-types
// Node.js 24 built-in TypeScript stripping; use the SDK already installed with Pi.
// Run: node --experimental-strip-types discover_pi_repo.ts <host> <cwd> <agentDir> <locate|discover>
// This reads package settings and resources without constructing a session or auth store.
async function main() {
  const { join, resolve } = await import("node:path");
  const { pathToFileURL } = await import("node:url");
  const [hostRoot, cwd, agentDir, mode] = process.argv.slice(2);
  if (!hostRoot || !cwd || !agentDir || !["locate", "discover"].includes(mode)) {
    throw new Error("Expected Pi host root, workspace, isolated agent directory and locate|discover");
  }
  const { DefaultPackageManager, DefaultResourceLoader, SettingsManager } = await import(
    pathToFileURL(join(hostRoot, "dist", "index.js")).href
  );
  const settings = SettingsManager.create(cwd, agentDir, { projectTrusted: true });
  const packages = new DefaultPackageManager({ cwd, agentDir, settingsManager: settings });
  const configured = packages.listConfiguredPackages();
  if (configured.length !== 1 || configured[0].scope !== "project") {
    throw new Error("Expected exactly one native project-scoped package declaration");
  }
  const installedPath = packages.getInstalledPath(configured[0].source, "project");
  if (!installedPath) throw new Error("Native Pi did not resolve an installed package path");
  const location = { configuredPackages: configured, installedPath: resolve(installedPath) };
  if (mode === "locate") {
    console.log(JSON.stringify(location));
    return;
  }
  const loader = new DefaultResourceLoader({
    cwd,
    agentDir,
    settingsManager: SettingsManager.inMemory({}, { projectTrusted: true }),
    additionalExtensionPaths: [location.installedPath],
    noExtensions: true,
    disabledBuiltinExtensions: ["mcp"],
    noSkills: true,
    noPromptTemplates: true,
    noThemes: true,
    noContextFiles: true,
  });
  await loader.reload();
  const skills = loader.getSkills();
  const extensions = loader.getExtensions();
  const prompts = loader.getPrompts();
  const themes = loader.getThemes();
  console.log(JSON.stringify({
    ...location,
    api: "DefaultPackageManager.getInstalledPath + DefaultResourceLoader",
    skills: skills.skills.map(({ name, filePath, baseDir, sourceInfo }) => ({
      name, filePath, baseDir, sourceInfo, command: `/skill:${name}`,
    })),
    diagnostics: skills.diagnostics,
    extensionCount: extensions.extensions.length,
    extensionErrors: extensions.errors,
    promptCount: prompts.prompts.length,
    promptDiagnostics: prompts.diagnostics,
    themeCount: themes.themes.length,
    themeDiagnostics: themes.diagnostics,
    contextFileCount: loader.getAgentsFiles().agentsFiles.length,
    modelCalls: 0,
  }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
