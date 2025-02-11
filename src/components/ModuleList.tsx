import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  TextField,
  Box,
  CircularProgress,
  Alert,
  Container
} from '@mui/material';
import { DefaultApi } from '../api/apis';

const api = new DefaultApi();

const ModuleList = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
  const { data: searchResponse, isLoading, error } = useQuery({
    queryKey: ['modules', searchQuery],
    queryFn: () => api.searchModules({
      query: searchQuery,
      limit: 10,
      offset: 0
    })
  });

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Box mt={2}>
          <Alert severity="error">Error loading modules: {error instanceof Error ? error.message : 'Unknown error'}</Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ my: 4 }}>
        <TextField
          fullWidth
          label="Search modules"
          variant="outlined"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ mb: 4 }}
        />
        
        <Grid container spacing={3}>
          {searchResponse?.modules?.map((module) => (
            <Grid item xs={12} sm={6} md={4} key={`${module.namespace}/${module.name}/${module.provider}`}>
              <Card 
                component={Link}
                to={`/modules/${module.namespace}/${module.name}/${module.provider}`}
                sx={{ 
                  textDecoration: 'none',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  '&:hover': {
                    boxShadow: 6
                  }
                }}
              >
                <CardContent>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {module.name}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    {module.namespace}/{module.provider}
                  </Typography>
                  <Typography variant="body2">
                    {module.description || 'No description available'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default ModuleList;