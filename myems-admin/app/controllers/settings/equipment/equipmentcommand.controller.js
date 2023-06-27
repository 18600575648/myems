'use strict';

app.controller('EquipmentCommandController', function (
    $scope,
    $window,
    $timeout,
    $translate,
    EquipmentService,
    CommandService,
    EquipmentCommandService,
    toaster) {
    $scope.cur_user = JSON.parse($window.localStorage.getItem("myems_admin_ui_current_user"));
    $scope.currentEquipment = {selected:undefined};
    $scope.getAllCommands = function() {
		CommandService.getAllCommands(function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.commands = response.data;
			} else {
				$scope.commands = [];
			}
		});
	};

    $scope.getCommandsByEquipmentID = function (id) {
        let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
        EquipmentCommandService.getCommandsByEquipmentID(id, headers, function (response) {
            if (angular.isDefined(response.status) && response.status === 200) {
                $scope.equipmentcommands = response.data;
            } else {
                $scope.equipmentcommands = [];
            }
        });
    };

    $scope.changeEquipment=function(item,model){
  	  $scope.currentEquipment=item;
  	  $scope.currentEquipment.selected=model;
  	  $scope.getCommandsByEquipmentID($scope.currentEquipment.id);
    };

    $scope.getAllEquipments = function () {
        let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
        EquipmentService.getAllEquipments(headers, function (response) {
            if (angular.isDefined(response.status) && response.status === 200) {
                $scope.equipments = response.data;
                $timeout(function () {
                    $scope.getCommandsByEquipmentID($scope.currentEquipment.id);
                }, 1000);
            } else {
                $scope.equipments = [];
            }
        });

    };

    $scope.pairCommand = function (dragEl, dropEl) {
        var commandid = angular.element('#' + dragEl).scope().command.id;
        var equipmentid = $scope.currentEquipment.id;
		let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
        EquipmentCommandService.addPair(equipmentid, commandid, headers, function (response) {
            if (angular.isDefined(response.status) && response.status === 201) {
                toaster.pop({
                    type: "success",
                    title: $translate.instant("TOASTER.SUCCESS_TITLE"),
                    body: $translate.instant("TOASTER.BIND_COMMAND_SUCCESS"),
                    showCloseButton: true,
                });
                $scope.getCommandsByEquipmentID($scope.currentEquipment.id);
            } else {
                toaster.pop({
                    type: "error",
                    title: $translate.instant(response.data.title),
                    body: $translate.instant(response.data.description),
                    showCloseButton: true,
                });
            }
        });
    };

    $scope.deleteCommandPair = function (dragEl, dropEl) {
        if (angular.element('#' + dragEl).hasClass('source')) {
            return;
        }
        var equipmentcommandid = angular.element('#' + dragEl).scope().equipmentcommand.id;
        var equipmentid = $scope.currentEquipment.id;
		let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
        EquipmentCommandService.deletePair(equipmentid, equipmentcommandid, headers, function (response) {
            if (angular.isDefined(response.status) && response.status === 204) {
                toaster.pop({
                    type: "success",
                    title: $translate.instant("TOASTER.SUCCESS_TITLE"),
                    body: $translate.instant("TOASTER.UNBIND_COMMAND_SUCCESS"),
                    showCloseButton: true,
                });
                $scope.getCommandsByEquipmentID($scope.currentEquipment.id);
            } else {
                toaster.pop({
                    type: "error",
                    title: $translate.instant(response.data.title),
                    body: $translate.instant(response.data.description),
                    showCloseButton: true,
                });
            }
        });
    };

    $scope.getAllCommands();
    $scope.getAllEquipments();

  	$scope.$on('handleBroadcastEquipmentChanged', function(event) {
      $scope.getAllEquipments();
  	});
});
