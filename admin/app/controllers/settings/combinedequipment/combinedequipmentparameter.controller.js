'use strict';

app.controller('CombinedEquipmentParameterController', function ($scope, $uibModal, $translate, MeterService, VirtualMeterService, OfflineMeterService, CombinedEquipmentParameterService, CombinedEquipmentService, PointService, toaster, SweetAlert) {
	$scope.currentCombinedEquipment = { selected: undefined };
	$scope.is_show_add_parameter = false;
	$scope.combinedequipments = [];
	$scope.meters = [];
	$scope.offlinemeters = [];
	$scope.virtualmeters = [];
	$scope.mergedMeters = [];

	$scope.getAllCombinedEquipments = function () {
		CombinedEquipmentService.getAllCombinedEquipments(function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.combinedequipments = response.data;
			} else {
				$scope.combinedequipments = [];
			}
		});
	};

	$scope.changeCombinedEquipment = function (item, model) {
		$scope.currentCombinedEquipment = item;
		$scope.currentCombinedEquipment.selected = model;
		$scope.is_show_add_parameter = true;
		$scope.getParametersByCombinedEquipmentID($scope.currentCombinedEquipment.id);
	};

	$scope.getParametersByCombinedEquipmentID = function (id) {
		$scope.combinedequipmentparameters = [];
		CombinedEquipmentParameterService.getParametersByCombinedEquipmentID(id, function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.combinedequipmentparameters = response.data;
			}
		});
	};

	$scope.addCombinedEquipmentParameter = function () {

		var modalInstance = $uibModal.open({
			templateUrl: 'views/settings/combinedequipment/combinedequipmentparameter.model.html',
			controller: 'ModalAddCombinedEquipmentParameterCtrl',
			windowClass: "animated fadeIn",
			resolve: {
				params: function () {
					return {
						points: angular.copy($scope.points),
						mergedmeters: angular.copy($scope.mergedmeters),
					};
				}
			}
		});
		modalInstance.result.then(function (combinedequipmentparameter) {
			var combinedequipmentid = $scope.currentCombinedEquipment.id;
			if (combinedequipmentparameter.point != null) {
				combinedequipmentparameter.point_id = combinedequipmentparameter.point.id;
			}
			if (combinedequipmentparameter.numerator_meter != null) {
				combinedequipmentparameter.numerator_meter_uuid = combinedequipmentparameter.numerator_meter.uuid;
			}
			if (combinedequipmentparameter.denominator_meter != null) {
				combinedequipmentparameter.denominator_meter_uuid = combinedequipmentparameter.denominator_meter.uuid;
			}

			CombinedEquipmentParameterService.addCombinedEquipmentParameter(combinedequipmentid, combinedequipmentparameter, function (response) {
				if (angular.isDefined(response.status) && response.status === 201) {
					toaster.pop({
						type: "success",
						title: $translate.instant("TOASTER.SUCCESS_TITLE"),
						body: $translate.instant("TOASTER.SUCCESS_ADD_BODY", { template: $translate.instant("COMBINED_EQUIPMENT.PARAMETER") }),
						showCloseButton: true,
					});
					$scope.getParametersByCombinedEquipmentID($scope.currentCombinedEquipment.id);
				} else {
					toaster.pop({
						type: "error",
						title: $translate.instant("TOASTER.ERROR_ADD_BODY", { template: $translate.instant("COMBINED_EQUIPMENT.PARAMETER") }),
						body: $translate.instant(response.data.description),
						showCloseButton: true,
					});
				}
			});
		}, function () {

		});
	};

	$scope.editCombinedEquipmentParameter = function (combinedequipmentparameter) {
		var modalInstance = $uibModal.open({
			templateUrl: 'views/settings/combinedequipment/combinedequipmentparameter.model.html',
			controller: 'ModalEditCombinedEquipmentParameterCtrl',
			windowClass: "animated fadeIn",
			resolve: {
				params: function () {
					return {
						combinedequipmentparameter: angular.copy(combinedequipmentparameter),
						points: angular.copy($scope.points),
						mergedmeters: angular.copy($scope.mergedmeters),
					};
				}
			}
		});

		modalInstance.result.then(function (modifiedCombinedEquipmentParameter) {
			if (modifiedCombinedEquipmentParameter.point != null) {
				modifiedCombinedEquipmentParameter.point_id = modifiedCombinedEquipmentParameter.point.id;
			}
			if (modifiedCombinedEquipmentParameter.numerator_meter != null) {
				modifiedCombinedEquipmentParameter.numerator_meter_uuid = modifiedCombinedEquipmentParameter.numerator_meter.uuid;
			}
			if (modifiedCombinedEquipmentParameter.denominator_meter != null) {
				modifiedCombinedEquipmentParameter.denominator_meter_uuid = modifiedCombinedEquipmentParameter.denominator_meter.uuid;
			}
			CombinedEquipmentParameterService.editCombinedEquipmentParameter($scope.currentCombinedEquipment.id, modifiedCombinedEquipmentParameter, function (response) {
				if (angular.isDefined(response.status) && response.status === 200) {
					toaster.pop({
						type: "success",
						title: $translate.instant("TOASTER.SUCCESS_TITLE"),
						body: $translate.instant("TOASTER.SUCCESS_UPDATE_BODY", { template: $translate.instant("COMBINED_EQUIPMENT.PARAMETER") }),
						showCloseButton: true,
					});
					$scope.getParametersByCombinedEquipmentID($scope.currentCombinedEquipment.id);
				} else {
					toaster.pop({
						type: "error",
						title: $translate.instant("TOASTER.ERROR_UPDATE_BODY", { template: $translate.instant("COMBINED_EQUIPMENT.PARAMETER") }),
						body: $translate.instant(response.data.description),
						showCloseButton: true,
					});
				}
			});
		}, function () {
			//do nothing;
		});
	};

	$scope.deleteCombinedEquipmentParameter = function (combinedequipmentparameter) {
		SweetAlert.swal({
			title: $translate.instant("SWEET.TITLE"),
			text: $translate.instant("SWEET.TEXT"),
			type: "warning",
			showCancelButton: true,
			confirmButtonColor: "#DD6B55",
			confirmButtonText: $translate.instant("SWEET.CONFIRM_BUTTON_TEXT"),
			cancelButtonText: $translate.instant("SWEET.CANCEL_BUTTON_TEXT"),
			closeOnConfirm: true,
			closeOnCancel: true
		},
			function (isConfirm) {
				if (isConfirm) {
					CombinedEquipmentParameterService.deleteCombinedEquipmentParameter($scope.currentCombinedEquipment.id, combinedequipmentparameter.id, function (response) {
						if (angular.isDefined(response.status) && response.status === 204) {
							toaster.pop({
								type: "success",
								title: $translate.instant("TOASTER.SUCCESS_TITLE"),
								body: $translate.instant("TOASTER.SUCCESS_DELETE_BODY", { template: $translate.instant("COMBINED_EQUIPMENT.PARAMETER") }),
								showCloseButton: true,
							});
							$scope.getParametersByCombinedEquipmentID($scope.currentCombinedEquipment.id);
						} else {
							toaster.pop({
								type: "error",
								title: $translate.instant("TOASTER.ERROR_DELETE_BODY", { template: $translate.instant("COMBINED_EQUIPMENT.PARAMETER") }),
								body: $translate.instant(response.data.description),
								showCloseButton: true,
							});
						}
					});
				}
			});
	};

	$scope.colorMeterType = function (type) {
		if (type == 'meters') {
			return 'btn-primary'
		} else if (type == 'virtualmeters') {
			return 'btn-info'
		} else {
			return 'btn-success'
		}
	};

	$scope.showCombinedEquipmentParameterType = function (type) {
		if (type == 'constant') {
			return 'COMBINED_EQUIPMENT.CONSTANT';
		} else if (type == 'point') {
			return 'COMBINED_EQUIPMENT.POINT';
		} else if (type == 'fraction') {
			return 'COMBINED_EQUIPMENT.FRACTION';
		}
	};

	$scope.showCombinedEquipmentParameterNumerator = function (combinedequipmentparameter) {
		if (combinedequipmentparameter.numerator_meter == null) {
			return '-';
		} else {
			return '(' + combinedequipmentparameter.numerator_meter.type + ')' + combinedequipmentparameter.numerator_meter.name;
		}
	};


	$scope.showCombinedEquipmentParameterDenominator = function (combinedequipmentparameter) {
		if (combinedequipmentparameter.denominator_meter == null) {
			return '-';
		} else {
			return '(' + combinedequipmentparameter.denominator_meter.type + ')' + combinedequipmentparameter.denominator_meter.name;
		}
	};

	$scope.getMergedMeters = function () {
		$scope.mergedmeters = [];
		$scope.meters = [];
		$scope.offlinemeters = [];
		$scope.virtualmeters = [];
		MeterService.getAllMeters(function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.meters = response.data;
				for (var i = 0; i < $scope.meters.length; i++) {
					var mergedmeter = { "uuid": $scope.meters[i].uuid, "name": "meter/" + $scope.meters[i].name };
					$scope.mergedmeters.push(mergedmeter);
				}
			} else {
				$scope.meters = [];
			}
		});

		OfflineMeterService.getAllOfflineMeters(function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.offlinemeters = response.data;
				for (var i = 0; i < $scope.offlinemeters.length; i++) {
					var mergedmeter = { "uuid": $scope.offlinemeters[i].uuid, "name": "offlinemeter/" + $scope.offlinemeters[i].name };
					$scope.mergedmeters.push(mergedmeter);
				}
			} else {
				$scope.offlinemeters = [];
			}
		});

		VirtualMeterService.getAllVirtualMeters(function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.virtualmeters = response.data;
				for (var i = 0; i < $scope.virtualmeters.length; i++) {
					var mergedmeter = { "uuid": $scope.virtualmeters[i].uuid, "name": "virtualmeter/" + $scope.virtualmeters[i].name };
					$scope.mergedmeters.push(mergedmeter);
				}
			} else {
				$scope.virtualmeters = [];
			}
		});
	};

	$scope.getAllPoints = function () {
		PointService.getAllPoints(function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.points = response.data;
			} else {
				$scope.points = [];
			}
		});

	};

	$scope.getAllCombinedEquipments();
	$scope.getMergedMeters();
	$scope.getAllPoints();

	$scope.$on('handleBroadcastCombinedEquipmentChanged', function (event) {
		$scope.getAllCombinedEquipments();
	});
});


app.controller('ModalAddCombinedEquipmentParameterCtrl', function ($scope, $uibModalInstance, params) {

	$scope.operation = "COMBINED_EQUIPMENT.ADD_PARAMETER";
	$scope.combinedequipmentparameter = {
		parameter_type: "constant",
	};
	$scope.is_disabled = false;
	$scope.points = params.points;
	$scope.mergedmeters = params.mergedmeters;
	$scope.ok = function () {

		$uibModalInstance.close($scope.combinedequipmentparameter);
	};

	$scope.cancel = function () {
		$uibModalInstance.dismiss('cancel');
	};
});

app.controller('ModalEditCombinedEquipmentParameterCtrl', function ($scope, $uibModalInstance, params) {
	$scope.operation = "COMBINED_EQUIPMENT.EDIT_PARAMETER";
	$scope.combinedequipmentparameter = params.combinedequipmentparameter;
	$scope.points = params.points;
	$scope.mergedmeters = params.mergedmeters;
	$scope.is_disabled = true;
	$scope.ok = function () {
		$uibModalInstance.close($scope.combinedequipmentparameter);
	};

	$scope.cancel = function () {
		$uibModalInstance.dismiss('cancel');
	};
});
