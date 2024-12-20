-- ---------------------------------------------------------------------------------------------------------------------
-- WARNING: BACKUP YOUR DATABASE BEFORE UPGRADING
-- THIS SCRIPT IS ONLY FOR UPGRADING 1.4.0 TO 1.5.0
-- THE CURRENT VERSION CAN BE FOUND AT `myems_system_db`.`tbl_versions`
-- ---------------------------------------------------------------------------------------------------------------------

START TRANSACTION;

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_baseline_db`.`tbl_meter_hourly`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_baseline_db`.`tbl_meter_hourly` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `meter_id` BIGINT NOT NULL,
  `start_datetime_utc` DATETIME NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_meter_hourly_index_1` ON  `myems_energy_baseline_db`.`tbl_meter_hourly`   (`meter_id`, `start_datetime_utc`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_baseline_db`.`tbl_offline_meter_hourly`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_baseline_db`.`tbl_offline_meter_hourly` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `offline_meter_id` BIGINT NOT NULL,
  `start_datetime_utc` DATETIME NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_offline_meter_hourly_index_1` ON  `myems_energy_baseline_db`.`tbl_offline_meter_hourly`   (`offline_meter_id`, `start_datetime_utc`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_baseline_db`.`tbl_virtual_meter_hourly`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_baseline_db`.`tbl_virtual_meter_hourly` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `virtual_meter_id` BIGINT NOT NULL,
  `start_datetime_utc` DATETIME NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_virtual_meter_hourly_index_1` ON  `myems_energy_baseline_db`.`tbl_virtual_meter_hourly`   (`virtual_meter_id`, `start_datetime_utc`);

-- MyEMS Energy Model Database
-- store energy consumption models in 8760 hours of year, hour by hour
-- ---------------------------------------------------------------------------------------------------------------------
-- Schema myems_energy_model_db
-- ---------------------------------------------------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS `myems_energy_model_db` ;

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_combined_equipment_input_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_combined_equipment_input_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `combined_equipment_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_combined_equipment_input_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_combined_equipment_input_category_8760`   (`combined_equipment_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_combined_equipment_input_item_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_combined_equipment_input_item_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `combined_equipment_id` BIGINT NOT NULL,
  `energy_item_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_combined_equipment_input_item_8760_index_1` ON  `myems_energy_model_db`.`tbl_combined_equipment_input_item_8760`   (`combined_equipment_id`, `energy_item_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_combined_equipment_output_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_combined_equipment_output_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `combined_equipment_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_combined_equipment_output_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_combined_equipment_output_category_8760`   (`combined_equipment_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_equipment_input_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_equipment_input_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `equipment_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_equipment_input_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_equipment_input_category_8760`   (`equipment_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_equipment_input_item_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_equipment_input_item_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `equipment_id` BIGINT NOT NULL,
  `energy_item_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_equipment_input_item_8760_index_1` ON  `myems_energy_model_db`.`tbl_equipment_input_item_8760`   (`equipment_id`, `energy_item_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_equipment_output_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_equipment_output_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `equipment_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_equipment_output_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_equipment_output_category_8760`   (`equipment_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_meter_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_meter_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `meter_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_meter_8760_index_1` ON  `myems_energy_model_db`.`tbl_meter_8760`   (`meter_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_offline_meter_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_offline_meter_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `offline_meter_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_offline_meter_8760_index_1` ON  `myems_energy_model_db`.`tbl_offline_meter_8760`   (`offline_meter_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_shopfloor_input_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_shopfloor_input_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `shopfloor_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_shopfloor_input_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_shopfloor_input_category_8760`   (`shopfloor_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_shopfloor_input_item_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_shopfloor_input_item_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `shopfloor_id` BIGINT NOT NULL,
  `energy_item_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_shopfloor_input_item_8760_index_1` ON  `myems_energy_model_db`.`tbl_shopfloor_input_item_8760`   (`shopfloor_id`, `energy_item_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_space_input_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_space_input_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `space_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_space_input_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_space_input_category_8760`   (`space_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_space_input_item_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_space_input_item_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `space_id` BIGINT NOT NULL,
  `energy_item_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_space_input_item_8760_index_1` ON  `myems_energy_model_db`.`tbl_space_input_item_8760`   (`space_id`, `energy_item_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_space_output_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_space_output_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `space_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_space_output_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_space_output_category_8760`   (`space_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_store_input_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_store_input_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `store_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_store_input_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_store_input_category_8760`   (`store_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_store_input_item_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_store_input_item_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `store_id` BIGINT NOT NULL,
  `energy_item_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_store_input_item_8760_index_1` ON  `myems_energy_model_db`.`tbl_store_input_item_8760`   (`store_id`, `energy_item_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_tenant_input_category_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_tenant_input_category_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `tenant_id` BIGINT NOT NULL,
  `energy_category_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_tenant_input_category_8760_index_1` ON  `myems_energy_model_db`.`tbl_tenant_input_category_8760`   (`tenant_id`, `energy_category_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_tenant_input_item_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_tenant_input_item_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `tenant_id` BIGINT NOT NULL,
  `energy_item_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_tenant_input_item_8760_index_1` ON  `myems_energy_model_db`.`tbl_tenant_input_item_8760`   (`tenant_id`, `energy_item_id`, `hour_of_year`);

-- ---------------------------------------------------------------------------------------------------------------------
-- Table `myems_energy_model_db`.`tbl_virtual_meter_8760`
-- ---------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `myems_energy_model_db`.`tbl_virtual_meter_8760` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `virtual_meter_id` BIGINT NOT NULL,
  `hour_of_year` INT NOT NULL,
  `actual_value` DECIMAL(18, 3) NOT NULL,
  PRIMARY KEY (`id`));
CREATE INDEX `tbl_virtual_meter_8760_index_1` ON  `myems_energy_model_db`.`tbl_virtual_meter_8760`   (`virtual_meter_id`, `hour_of_year`);


-- UPDATE VERSION NUMBER
UPDATE `myems_system_db`.`tbl_versions` SET version='1.5.0', release_date='2021-12-12' WHERE id=1;

COMMIT;
