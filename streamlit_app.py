import streamlit as st
import requests
from typing import Optional, Dict, Any
import json

class TerraformModuleClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def search_modules(
        self,
        query: str = "",
        provider: Optional[str] = None,
        namespace: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search for modules with optional filtering."""
        params = {
            "query": query,
            "provider": provider,
            "namespace": namespace,
            "limit": limit,
            "offset": offset
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(f"{self.base_url}/v1/modules/search", params=params)
        response.raise_for_status()
        return response.json()

    def get_module_versions(
        self,
        namespace: str,
        name: str,
        provider: str
    ) -> Dict[str, Any]:
        """Get available versions for a module."""
        response = requests.get(
            f"{self.base_url}/v1/modules/{namespace}/{name}/{provider}/versions"
        )
        response.raise_for_status()
        return response.json()

    def get_module_details(
        self,
        namespace: str,
        name: str,
        provider: str,
        version: str
    ) -> Dict[str, Any]:
        """Get details for a specific module version."""
        response = requests.get(
            f"{self.base_url}/v1/modules/{namespace}/{name}/{provider}/{version}"
        )
        response.raise_for_status()
        return response.json()

    def get_accessible_namespaces(self) -> Dict[str, Any]:
        """Fetch namespaces the user has access to."""
        response = requests.get(f"{self.base_url}/v1/namespaces")
        response.raise_for_status()
        return response.json()

# Initialize the client
client = TerraformModuleClient()

# Set up the main page
st.title("Terraform Module Registry")
st.markdown("Search and explore Terraform modules")

# Fetch accessible namespaces
try:
    namespaces = client.get_accessible_namespaces().get("namespaces", [])
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching namespaces: {str(e)}")
    namespaces = []

# Create the search interface
col1, col2, col3 = st.columns(3)

with col1:
    search_query = st.text_input("Search modules", "")
with col2:
    provider_filter = st.selectbox("Provider", ["", "aws", "azure", "gcp", "kubernetes"])
with col3:
    namespace_filter = st.selectbox("Namespace", [""] + namespaces)

try:
    # Search for modules
    if search_query or provider_filter or namespace_filter:
        results = client.search_modules(
            query=search_query,
            provider=provider_filter if provider_filter else None,
            namespace=namespace_filter if namespace_filter else None
        )
        
        if not results.get("modules"):
            st.info("No modules found")
        else:
            # Display results in a clean format
            for module in results["modules"]:
                with st.expander(f"{module['namespace']}/{module['name']}/{module['provider']} - {module['version']}"):
                    st.markdown(f"**Description:** {module.get('description', 'No description available')}")
                    st.markdown(f"**Provider:** {module['provider']}")
                    st.markdown(f"**Owner:** {module.get('owner', 'Unknown')}")
                    
                    if st.button("View Versions", key=f"versions_{module['namespace']}_{module['name']}_{module['provider']}"):
                        versions = client.get_module_versions(
                            module['namespace'],
                            module['name'],
                            module['provider']
                        )
                        if versions.get("modules") and versions["modules"][0].get("versions"):
                            version_list = [v["version"] for v in versions["modules"][0]["versions"]]
                            st.json({"Available Versions": version_list})
                        else:
                            st.warning("No versions available")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the backend: {str(e)}")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Add some helpful information at the bottom
st.markdown("---")
st.markdown("""
### How to use:
1. Enter a search term to find modules
2. Filter by provider or namespace if needed
3. Click on a module to see its details
4. Click "View Versions" to see available versions
""")