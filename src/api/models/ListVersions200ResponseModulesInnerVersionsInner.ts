/* tslint:disable */
/* eslint-disable */

/**
 * 
 * @export
 * @interface ListVersions200ResponseModulesInnerVersionsInner
 */
export interface ListVersions200ResponseModulesInnerVersionsInner {
    /**
     * 
     * @type {string}
     * @memberof ListVersions200ResponseModulesInnerVersionsInner
     */
    version?: string;
}

export function instanceOfListVersions200ResponseModulesInnerVersionsInner(obj: object): obj is ListVersions200ResponseModulesInnerVersionsInner {
    let validKeys = ['version'];
    return Object.keys(obj).every(key => validKeys.includes(key));
}

export function ListVersions200ResponseModulesInnerVersionsInnerFromJSON(json: any): ListVersions200ResponseModulesInnerVersionsInner {
    return ListVersions200ResponseModulesInnerVersionsInnerFromJSONTyped(json);
}

export function ListVersions200ResponseModulesInnerVersionsInnerFromJSONTyped(json: any): ListVersions200ResponseModulesInnerVersionsInner {
    if (json === undefined || json === null) {
        return json;
    }
    return {
        'version': !json['version'] ? undefined : json['version'],
    };
}

export function ListVersions200ResponseModulesInnerVersionsInnerToJSON(value?: ListVersions200ResponseModulesInnerVersionsInner | null): any {
    return ListVersions200ResponseModulesInnerVersionsInnerToJSONTyped(value);
}

export function ListVersions200ResponseModulesInnerVersionsInnerToJSONTyped(value?: ListVersions200ResponseModulesInnerVersionsInner | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        'version': value.version,
    };
}

