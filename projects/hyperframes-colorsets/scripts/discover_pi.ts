#!/usr/bin/env -S node --experimental-strip-types
// Node.js 24 runs this TypeScript through its built-in type stripping; no npm dependencies.
// Run: node --experimental-strip-types discover_pi.ts <host> <package> <cwd> <agentDir>
// Use the installed Pi SDK; no agent session, auth store or model is constructed.
// Dynamic imports keep this script compatible with an untyped package.json.
async function main() {
  const { join } = await import("node:path");
  const { pathToFileURL } = await import("node:url");

  const [hostRoot, packageRoot, cwd, agentDir] = process.argv.slice(2);
  if (!hostRoot || !packageRoot || !cwd || !agentDir) {
    throw new Error("Expected Pi host root, package root, workspace and isolated agent directory");
  }
  const { DefaultResourceLoader, SettingsManager } = await import(
    pathToFileURL(join(hostRoot, "dist", "index.js")).href
  );
  const settingsManager = SettingsManager.inMemory({}, { projectTrusted: true });
  const loader = new DefaultResourceLoader({
    cwd,
    agentDir,
    settingsManager,
    additionalExtensionPaths: [packageRoot],
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
    api: "DefaultResourceLoader",
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
    projectTrusted: settingsManager.isProjectTrusted(),
    modelCalls: 0,
  }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
