class TerraformModuleClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.verify_ssl = True
        self.headers = {'Content-Type': 'application/json'}

    def set_jwt_token(self, token: str):
        self.token = token
        self.headers['Authorization'] = f'Bearer {token}'

    def get_headers(self) -> Dict[str, str]:
        if self.token:
            return {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
        return {'Content-Type': 'application/json'}

    def _handle_response(self, response):
        """Handle common response cases according to OpenAPI spec"""
        if response.status_code == 204:
            # Special handling for endpoints that return 204 with X-Terraform-Get header
            terraform_get = response.headers.get('X-Terraform-Get')
            if terraform_get:
                return {'download_url': terraform_get}
            return None
            
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            if response.status_code < 400:
                return None
            raise TerraformModuleClientError(f"Invalid JSON response: {response.text}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            logger.debug(f"Making {method} request to {url}")
            
            # Create safe copy of headers for logging
            safe_headers = self.get_headers().copy()
            if 'Authorization' in safe_headers:
                safe_headers['Authorization'] = 'Bearer [REDACTED]'
            logger.debug(f"Request headers: {safe_headers}")
            
            response = requests.request(method, url, headers=self.get_headers(), verify=self.verify_ssl, **kwargs)
            logger.debug(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            return self._handle_response(response)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise TerraformModuleClientError(f"API request failed: {e}")

    def discover_endpoints(self) -> Dict[str, Any]:
        """Registry discovery protocol endpoint"""
        return self._make_request('GET', '/.well-known/terraform.json')
        
    def search_modules(self, query: str = "", provider: Optional[str] = None,
                      namespace: Optional[str] = None, limit: int = 10,
                      offset: int = 0) -> Dict[str, Any]:
        """Search for modules with optional filtering"""
        params = {k: v for k, v in {
            'query': query,
            'provider': provider,
            'namespace': namespace,
            'limit': limit,
            'offset': offset
        }.items() if v is not None}
        
        return self._make_request('GET', '/v1/modules/search', params=params)
        
    def list_versions(self, namespace: str, name: str, provider: str) -> Dict[str, Any]:
        """List available versions for a module"""
        return self._make_request('GET', f'/v1/modules/{namespace}/{name}/{provider}/versions')
        
    def get_download_url(self, namespace: str, name: str, provider: str, version: str) -> Dict[str, Any]:
        """Get download URL for a specific module version"""
        return self._make_request('GET', f'/v1/modules/{namespace}/{name}/{provider}/{version}/download')
        
    def get_module_source(self, namespace: str, name: str, provider: str, version: str) -> Dict[str, Any]:
        """Download the module source code"""
        return self._make_request('GET', f'/v1/modules/{namespace}/{name}/{provider}/{version}/source')