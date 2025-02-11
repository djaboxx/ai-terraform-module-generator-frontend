import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import ModuleList from './components/ModuleList';
import ModuleDetail from './components/ModuleDetail';
import Register from './components/Register';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#7B42BC', // A purple shade similar to HashiCorp's brand
    },
    secondary: {
      main: '#04999B', // A teal accent color
    },
  },
});

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<ModuleList />} />
              <Route path="/modules/:namespace/:name/:provider" element={<ModuleDetail />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
