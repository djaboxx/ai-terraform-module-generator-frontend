import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ModuleDetail from './ModuleDetail';
import { DefaultApi } from '../api/apis';

jest.mock('../api/apis');

const mockApi = {
  listVersions: jest.fn(),
  downloadModuleSource: jest.fn()
};

(DefaultApi as unknown as jest.Mock).mockImplementation(() => mockApi);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithRouter = (ui: React.ReactNode, { route = '/modules/test/module1/aws' } = {}) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path="/modules/:namespace/:name/:provider" element={ui} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('ModuleDetail', () => {
  beforeEach(() => {
    queryClient.clear();
    mockApi.listVersions.mockReset();
    mockApi.downloadModuleSource.mockReset();
  });

  it('displays loading state initially', () => {
    mockApi.listVersions.mockImplementation(() => new Promise(() => {})); // Never resolves
    renderWithRouter(<ModuleDetail />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays module details when loaded successfully', async () => {
    mockApi.listVersions.mockResolvedValue({
      data: {
        modules: [{
          versions: [{ version: '1.0.0' }],
          description: 'Test module description',
          readme: '# Test Module',
          inputs: [{
            name: 'test_input',
            type: 'string',
            description: 'A test input'
          }]
        }]
      }
    });
    mockApi.downloadModuleSource.mockResolvedValue({ data: { content: 'module content' }});

    renderWithRouter(<ModuleDetail />);
    
    await waitFor(() => {
      expect(screen.getByText('Test module description')).toBeInTheDocument();
    });
  });

  it('displays error message when loading fails', async () => {
    const errorMessage = 'Failed to load';
    mockApi.listVersions.mockRejectedValue(new Error(errorMessage));
    renderWithRouter(<ModuleDetail />);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('displays not found message when no module data is available', async () => {
    mockApi.listVersions.mockResolvedValue({ data: { modules: [] } });
    renderWithRouter(<ModuleDetail />);

    await waitFor(() => {
      expect(screen.getByText('Module not found')).toBeInTheDocument();
    });
  });
});