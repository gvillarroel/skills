// Build with npm run build. Release only sessions observed by this provider owner.
import { cleanupSessionResources, type Provider } from '@earendil-works/pi-ai';

const sessionOwners=new Map<string,Set<symbol>>();
export function ownProviderSessions(provider:Provider){
  const owner=Symbol('pilot-model-runtime'),sessions=new Set<string>();let disposed=false;
  const remember=(options:{sessionId?:string}|undefined)=>{
    if(disposed)throw new Error('The model runtime owner is closed.');
    const id=options?.sessionId;if(!id)return;
    sessions.add(id);let owners=sessionOwners.get(id);if(!owners){owners=new Set();sessionOwners.set(id,owners);}owners.add(owner);
  };
  const wrapped:Provider={...provider,
    stream(model,context,options){remember(options);return provider.stream(model,context,options);},
    streamSimple(model,context,options){remember(options);return provider.streamSimple(model,context,options);},
  };
  const dispose=()=>{if(disposed)return;disposed=true;const errors:unknown[]=[];for(const id of sessions){const owners=sessionOwners.get(id);owners?.delete(owner);if(owners?.size)continue;sessionOwners.delete(id);try{cleanupSessionResources(id);}catch(error){errors.push(error);}}sessions.clear();if(errors.length)throw new AggregateError(errors,'Owned model session cleanup failed.');};
  return {provider:wrapped,dispose};
}
