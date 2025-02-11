import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ModuleList from './ModuleList';
import { DefaultApi } from '../api/apis';

jest.mock('../api/apis');

const mockApi = {
  searchModules: jest.fn()
};

(DefaultApi as unknown as jest.Mock).mockImplementation(() => mockApi);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </QueryClientProvider>
);

describe('ModuleList', () => {
  beforeEach(() => {
    queryClient.clear();
    mockApi.searchModules.mockReset();
  });

  it('displays loading state initially', () => {
    mockApi.searchModules.mockImplementation(() => new Promise(() => {})); // Never resolves
    render(<ModuleList />, { wrapper });
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays modules when loaded successfully', async () => {
    mockApi.searchModules.mockResolvedValue({
      data: {
        modules: [
          {
            id: '1',
            namespace: 'test',
            name: 'module1',
            provider: 'aws',
            description: 'Test module'
          }
        ]
      }
    });
    
    render(<ModuleList />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('module1')).toBeInTheDocument();
      expect(screen.getByText('test/aws')).toBeInTheDocument();
      expect(screen.getByText('Test module')).toBeInTheDocument();
    });
  });

  it('displays error message when loading fails', async () => {
    const errorMessage = 'Failed to load';
    mockApi.searchModules.mockRejectedValue(new Error(errorMessage));
    render(<ModuleList />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(`Error loading modules: ${errorMessage}`)).toBeInTheDocument();
    });
  });
});