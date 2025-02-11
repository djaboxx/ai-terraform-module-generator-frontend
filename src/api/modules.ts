import axios from 'axios';

interface Module {
  namespace: string;
  name: string;
  provider: string;
  version: string;
  description: string;
  owner: string;
  source: string;
}

const api = axios.create({
  baseURL: '/v1/modules'
});

export const searchModules = async (
  query: string = '',
  provider?: string,
  namespace?: string,
  limit: number = 10,
  offset: number = 0
): Promise<Module[]> => {
  try {
    const response = await api.get('/search', {
      params: { q: query, provider, namespace, limit, offset }
    });
    
    if (!response.data.modules) {
      return [];
    }
    
    return response.data.modules.map((module: any) => ({
      namespace: module.namespace || '',
      name: module.name || '',
      provider: module.provider || '',
      version: module.version || '',
      description: module.description || '',
      owner: module.owner || '',
      source: module.source || ''
    }));
  } catch (error) {
    console.error('Error fetching modules:', error);
    throw new Error('Failed to fetch modules');
  }
};

export const getModuleDetails = async (
  namespace: string,
  name: string,
  provider: string
): Promise<Module> => {
  const response = await api.get(`/${namespace}/${name}/${provider}/versions`);
  
  if (!response.data.modules || response.data.modules.length === 0) {
    throw new Error('Module not found');
  }
  
  const latestModule = response.data.modules[0];
  const versions = latestModule.versions || [];
  
  if (versions.length === 0) {
    throw new Error('No versions found for module');
  }
  
  const latestVersion = versions[0];
  
  return {
    namespace,
    name,
    provider,
    version: latestVersion.version || '',
    description: '',
    owner: '',
    source: ''
  };
};

export const getModuleVersions = async (
  namespace: string,
  name: string,
  provider: string
): Promise<string[]> => {
  const response = await api.get(`/${namespace}/${name}/${provider}/versions`);
  
  if (!response.data.modules) {
    return [];
  }
  
  return response.data.modules.flatMap((module: any) => 
    module.versions?.map((version: any) => version.version || '') || []
  ).filter((version: string) => version !== '');
};