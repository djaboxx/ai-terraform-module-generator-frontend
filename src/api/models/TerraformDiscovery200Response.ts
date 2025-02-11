/* tslint:disable */
/* eslint-disable */

/**
 * 
 * @export
 * @interface TerraformDiscovery200Response
 */
export interface TerraformDiscovery200Response {
    /**
     * 
     * @type {string}
     * @memberof TerraformDiscovery200Response
     */
    modules?: string;
}

export function instanceOfTerraformDiscovery200Response(obj: object): obj is TerraformDiscovery200Response {
    let validKeys = ['modules'];
    return Object.keys(obj).every(key => validKeys.includes(key));
}

export function TerraformDiscovery200ResponseFromJSON(json: any): TerraformDiscovery200Response {
    return TerraformDiscovery200ResponseFromJSONTyped(json);
}

export function TerraformDiscovery200ResponseFromJSONTyped(json: any): TerraformDiscovery200Response {
    if (json === undefined || json === null) {
        return json;
    }
    return {
        'modules': !json['modules'] ? undefined : json['modules'],
    };
}

export function TerraformDiscovery200ResponseToJSON(value?: TerraformDiscovery200Response | null): any {
    return TerraformDiscovery200ResponseToJSONTyped(value);
}

export function TerraformDiscovery200ResponseToJSONTyped(value?: TerraformDiscovery200Response | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        'modules': value.modules,
    };
}

