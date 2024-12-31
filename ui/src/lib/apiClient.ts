import {DocumentTypesApi, Configuration, FilesApi, GeneratorsApi} from '@/generated/api';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

const configuration = new Configuration({ basePath: apiBaseUrl });

export const documentApi = new DocumentTypesApi(configuration);
export const filesApi = new FilesApi(configuration);
export const generatorsApi = new GeneratorsApi(configuration);