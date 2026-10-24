// Build with npm run build. Machine-specific configuration remains private.
import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
export function pilotConfigPath(project:string):string {
  if(process.env.PI_PILOT_CONFIG)return resolve(process.env.PI_PILOT_CONFIG);
  const local=join(project,'config.local.json');
  return existsSync(local)?local:join(project,'config.json');
}
