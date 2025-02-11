import { searchModules } from './modules';
import axios from 'axios';

jest.mock('axios', () => {
  const mockAxiosGet = jest.fn();
  const mockAxiosInstance = {
    get: mockAxiosGet,
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    patch: jest.fn(),
    head: jest.fn(),
    options: jest.fn(),
    request: jest.fn(),
    defaults: {},
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn(), clear: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn(), clear: jest.fn() }
    },
    getUri: jest.fn()
  };

  return {
    create: () => mockAxiosInstance,
    default: {
      create: () => mockAxiosInstance
    }
  };
});

const getMockAxiosInstance = () => (axios.create() as any);

describe('searchModules', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch modules with the correct query parameters', async () => {
    const mockResponse = { data: { modules: [] } };
    const mockInstance = getMockAxiosInstance();
    mockInstance.get.mockResolvedValueOnce(mockResponse);

    const query = 'test';
    const provider = 'aws';
    const namespace = 'example';
    const limit = 5;
    const offset = 0;

    const result = await searchModules(query, provider, namespace, limit, offset);

    expect(mockInstance.get).toHaveBeenCalledWith('/search', {
      params: { q: query, provider, namespace, limit, offset }
    });
    expect(result).toEqual([]);
  });
});
