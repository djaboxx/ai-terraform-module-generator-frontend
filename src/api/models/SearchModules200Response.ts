/* tslint:disable */
/* eslint-disable */

import {
    SearchModules200ResponseModulesInner,
    SearchModules200ResponseModulesInnerFromJSON,
    SearchModules200ResponseModulesInnerToJSON,
} from './SearchModules200ResponseModulesInner';

/**
 * 
 * @export
 * @interface SearchModules200Response
 */
export interface SearchModules200Response {
    /**
     * 
     * @type {Array<SearchModules200ResponseModulesInner>}
     * @memberof SearchModules200Response
     */
    modules?: Array<SearchModules200ResponseModulesInner>;
}

export function instanceOfSearchModules200Response(obj: object): obj is SearchModules200Response {
    let validKeys = ['modules'];
    return Object.keys(obj).every(key => validKeys.includes(key));
}

export function SearchModules200ResponseFromJSON(json: any): SearchModules200Response {
    return SearchModules200ResponseFromJSONTyped(json);
}

export function SearchModules200ResponseFromJSONTyped(json: any): SearchModules200Response {
    if (json === undefined || json === null) {
        return json;
    }
    return {
        'modules': !json['modules'] ? undefined : ((json['modules'] as Array<any>).map(SearchModules200ResponseModulesInnerFromJSON)),
    };
}

export function SearchModules200ResponseToJSON(value?: SearchModules200Response | null): any {
    return SearchModules200ResponseToJSONTyped(value);
}

export function SearchModules200ResponseToJSONTyped(value?: SearchModules200Response | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        'modules': value.modules === undefined ? undefined : ((value.modules as Array<any>).map(SearchModules200ResponseModulesInnerToJSON)),
    };
}

