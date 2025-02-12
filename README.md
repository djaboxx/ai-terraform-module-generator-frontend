# AI Terraform Module Generator Frontend

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default tseslint.config({
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

- Replace `tseslint.configs.recommended` to `tseslint.configs.recommendedTypeChecked` or `tseslint.configs.strictTypeChecked`
- Optionally add `...tseslint.configs.stylisticTypeChecked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and update the config:

```js
// eslint.config.js
import react from 'eslint-plugin-react'

export default tseslint.config({
  // Set the react version
  settings: { react: { version: '18.3' } },
  plugins: {
    // Add the react plugin
    react,
  },
  rules: {
    // other rules...
    // Enable its recommended rules
    ...react.configs.recommended.rules,
    ...react.configs['jsx-runtime'].rules,
  },
})
```

## Application Architecture

### Component Structure

```
App.tsx
└── Layout
    ├── ModuleList (/)
    │   └── Module Cards
    ├── ModuleDetail (/modules/:namespace/:name/:provider)
    │   └── Module Info Tabs
    └── Register (/register)
```

### How Components Work Together

1. **App.tsx** (Main Application Container)
   - Sets up routing using React Router
   - Configures the Material-UI theme
   - Initializes React Query for API data management
   - Wraps everything in the Layout component

2. **Layout Component**
   - Provides the common page structure
   - Shows the top navigation bar
   - Renders other components in its main content area

3. **ModuleList Component** (Home Page)
   - Shows when you visit the root URL '/'
   - Features:
     - Search box for filtering modules
     - Grid of module cards
     - Each card links to its ModuleDetail page
   - Data Flow:
     - Uses React Query to fetch module data
     - Automatically refetches when search input changes
     - Shows loading/error states

4. **ModuleDetail Component** (Module Page)
   - Shows when you click a module card
   - URL pattern: /modules/:namespace/:name/:provider
   - Features:
     - Module metadata (name, provider, version)
     - Tabbed interface for:
       - README content
       - Input parameters
       - Output values
       - Dependencies
   - Data Flow:
     - First fetches version information
     - Then fetches detailed module data
     - Updates tabs without page reload

5. **API Integration**
   - All API calls go through the DefaultApi class
   - Endpoints used:
     - GET /v1/modules/search
     - GET /v1/modules/:namespace/:name/:provider/versions
     - GET /v1/modules/:namespace/:name/:provider/:version

### Debugging Flow

When something's not working:

1. Start at the Network Tab:
   ```
   ModuleList search → /v1/modules/search?query=...
                    ↓
   Click module → /v1/modules/{namespace}/{name}/{provider}/versions
                    ↓
   Load details → /v1/modules/{namespace}/{name}/{provider}/{version}
   ```

2. Check Console Messages:
   - 🔍 Search/fetch operations
   - 📦 Data responses
   - ⌛ Loading states
   - ❌ Errors

3. Use React DevTools:
   - ModuleList: Check searchQuery state
   - ModuleDetail: Check URL parameters
   - Both: Verify data in useQuery hooks

This architecture follows a standard React pattern where:
- State flows down (parent to child)
- Actions flow up (child to parent)
- Data fetching is centralized
- Components are focused on presentation

## Debugging with Chrome DevTools

### Opening DevTools
1. Open Chrome and navigate to the application (usually http://localhost:3000)
2. Press F12 or right-click anywhere and select "Inspect"
3. DevTools will open, usually on the right side of your window

### Key DevTools Features for This Project

#### Network Tab
- Shows all API calls to the backend
- Click 'Fetch/XHR' to filter for API requests only
- You'll see requests to endpoints like:
  - `/v1/modules/search` for module searches
  - `/v1/modules/{namespace}/{name}/{provider}` for module details

#### Console Tab
- Shows errors and console.log messages
- Errors will appear in red
- Look here first if something isn't working

#### React DevTools
1. Install "React Developer Tools" Chrome extension
2. In DevTools, look for the "Components" and "Profiler" tabs
3. Components tab shows the React component hierarchy
4. You can inspect props and state of any component

### Common Debugging Scenarios

1. Module Search Not Working:
   - Open Network tab
   - Type in the search box
   - Look for the `/v1/modules/search` request
   - Check the request URL and parameters
   - Check the response data

2. Module Details Not Loading:
   - Open Network tab
   - Click on a module
   - Look for requests to `/v1/modules/{namespace}/{name}/{provider}`
   - Check the response for errors

3. Component Issues:
   - Open React Components tab
   - Find the component in the tree (ModuleList or ModuleDetail)
   - Check its props and state
   - Look for error boundaries in red

Need help? Open DevTools and look at the specific area where you're having trouble. The error messages and network requests will help identify the issue.
