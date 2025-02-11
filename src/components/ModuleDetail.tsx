import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Link,
  Stack,
  Container
} from '@mui/material';
import { useState } from 'react';
import { DefaultApi } from '../api/apis';

const api = new DefaultApi();

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface ModuleInput {
  name: string;
  type: string;
  description: string;
  default?: any;
}

interface ModuleOutput {
  name: string;
  description: string;
}

interface ModuleDependency {
  source: string;
  version: string;
}

interface ModuleMetadata {
  description?: string;
  readme?: string;
  inputs?: ModuleInput[];
  outputs?: ModuleOutput[];
  dependencies?: ModuleDependency[];
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const LoadingState = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
    <CircularProgress />
  </Box>
);

const ErrorState = ({ message }: { message: string }) => (
  <Box mt={2}>
    <Alert severity="error">{message}</Alert>
  </Box>
);

const ModuleDetail = () => {
  const { namespace, name, provider } = useParams<{ namespace: string; name: string; provider: string }>();
  const [tabValue, setTabValue] = useState(0);
  
  const { data: versions, isLoading: isLoadingVersions, error: versionsError } = useQuery({
    queryKey: ['moduleVersions', namespace, name, provider],
    queryFn: () => api.listVersions({ namespace: namespace!, name: name!, provider: provider! }),
    enabled: !!(namespace && name && provider)
  });

  const latestVersion = versions?.modules?.[0]?.versions?.[0]?.version;
  
  const { data: module, isLoading: isLoadingModule, error: moduleError } = useQuery({
    queryKey: ['moduleDetails', namespace, name, provider, latestVersion],
    queryFn: () => api.downloadModuleSource({
      namespace: namespace!,
      name: name!,
      provider: provider!,
      version: latestVersion!
    }),
    enabled: !!(namespace && name && provider && latestVersion)
  });

  if (isLoadingVersions || (latestVersion && isLoadingModule)) {
    return <LoadingState />;
  }

  if (versionsError || moduleError) {
    const errorMessage = ((versionsError || moduleError) as Error)?.message || 'Error loading module details';
    return <ErrorState message={errorMessage} />;
  }

  if (!versions?.modules?.length) {
    return <ErrorState message="Module not found" />;
  }

  if (!module) {
    return <ErrorState message="Failed to load module details" />;
  }

  const moduleData = versions.modules[0] as unknown as ModuleMetadata;

  return (
    <Container>
      <Box sx={{ maxWidth: '1200px', margin: '0 auto', padding: 3 }}>
        <Typography variant="h4" gutterBottom>
          {name}
        </Typography>
        
        <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
          <Chip label={`Provider: ${provider}`} color="primary" />
          <Chip label={`Version: ${latestVersion}`} color="secondary" />
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Typography variant="body1" paragraph>
          {moduleData.description || 'No description available'}
        </Typography>

        <Paper sx={{ mt: 4 }}>
          <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
            <Tab label="README" />
            <Tab label="Inputs" />
            <Tab label="Outputs" />
            <Tab label="Dependencies" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <Typography component="div" className="markdown-body">
              {moduleData.readme || 'No README available'}
            </Typography>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {moduleData.inputs?.length ? (
              moduleData.inputs.map((input: ModuleInput) => (
                <Box key={input.name} sx={{ mb: 2 }}>
                  <Typography variant="h6">{input.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Type: {input.type}
                  </Typography>
                  <Typography>{input.description}</Typography>
                  {input.default !== undefined && (
                    <Typography variant="body2">
                      Default: {JSON.stringify(input.default)}
                    </Typography>
                  )}
                </Box>
              ))
            ) : (
              <Typography>No inputs defined</Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            {moduleData.outputs?.length ? (
              moduleData.outputs.map((output: ModuleOutput) => (
                <Box key={output.name} sx={{ mb: 2 }}>
                  <Typography variant="h6">{output.name}</Typography>
                  <Typography>{output.description}</Typography>
                </Box>
              ))
            ) : (
              <Typography>No outputs defined</Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            {moduleData.dependencies?.length ? (
              moduleData.dependencies.map((dep: ModuleDependency) => (
                <Box key={dep.source} sx={{ mb: 2 }}>
                  <Link href={dep.source}>{dep.source}</Link>
                  <Typography variant="body2">Version: {dep.version}</Typography>
                </Box>
              ))
            ) : (
              <Typography>No dependencies</Typography>
            )}
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default ModuleDetail;