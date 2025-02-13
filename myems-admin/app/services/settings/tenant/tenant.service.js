'use strict';
app.factory('TenantService', function($http) {
    return {
        getAllTenants:function(callback){
            $http.get(getAPI()+'tenants')
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        searchTenants: function(query, callback) {
            $http.get(getAPI()+'tenants', { params: { q: query } })
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        addTenant: function(tenant, headers, callback) {
            $http.post(getAPI()+'tenants',{data:tenant}, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        editTenant: function(tenant, headers, callback) {
            $http.put(getAPI()+'tenants/'+tenant.id,{data:tenant}, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        deleteTenant: function(tenant, headers, callback) {
            $http.delete(getAPI()+'tenants/'+tenant.id, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
    };
});
