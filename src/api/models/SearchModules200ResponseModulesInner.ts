/* tslint:disable */
/* eslint-disable */

/**
 * 
 * @export
 * @interface SearchModules200ResponseModulesInner
 */
export interface SearchModules200ResponseModulesInner {
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    id?: string;
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    owner?: string;
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    namespace?: string;
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    name?: string;
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    version?: string;
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    description?: string;
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    source?: string;
    /**
     * 
     * @type {string}
     * @memberof SearchModules200ResponseModulesInner
     */
    provider?: string;
}

export function instanceOfSearchModules200ResponseModulesInner(obj: object): obj is SearchModules200ResponseModulesInner {
    let validKeys = ['id', 'owner', 'namespace', 'name', 'version', 'description', 'source', 'provider'];
    return Object.keys(obj).every(key => validKeys.includes(key));
}

export function SearchModules200ResponseModulesInnerFromJSON(json: any): SearchModules200ResponseModulesInner {
    return SearchModules200ResponseModulesInnerFromJSONTyped(json);
}

export function SearchModules200ResponseModulesInnerFromJSONTyped(json: any): SearchModules200ResponseModulesInner {
    if (json === undefined || json === null) {
        return json;
    }
    return {
        'id': !json['id'] ? undefined : json['id'],
        'owner': !json['owner'] ? undefined : json['owner'],
        'namespace': !json['namespace'] ? undefined : json['namespace'],
        'name': !json['name'] ? undefined : json['name'],
        'version': !json['version'] ? undefined : json['version'],
        'description': !json['description'] ? undefined : json['description'],
        'source': !json['source'] ? undefined : json['source'],
        'provider': !json['provider'] ? undefined : json['provider'],
    };
}

export function SearchModules200ResponseModulesInnerToJSON(value?: SearchModules200ResponseModulesInner | null): any {
    return SearchModules200ResponseModulesInnerToJSONTyped(value);
}

export function SearchModules200ResponseModulesInnerToJSONTyped(value?: SearchModules200ResponseModulesInner | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        'id': value.id,
        'owner': value.owner,
        'namespace': value.namespace,
        'name': value.name,
        'version': value.version,
        'description': value.description,
        'source': value.source,
        'provider': value.provider,
    };
}

